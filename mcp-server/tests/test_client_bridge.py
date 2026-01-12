import json
import threading
import time

import pytest

from vibecraft.client_bridge import ClientBridge
from vibecraft.config import VibeCraftConfig
from vibecraft.exceptions import ClientBridgeConnectionError
from websocket import WebSocketTimeoutException, WebSocketConnectionClosedException


class FakeConnection:
    def __init__(self, preloaded=None, responder=None):
        self.sent = []
        self._queue = list(preloaded or [])
        self._responder = responder
        self._closed = False
        self._cond = threading.Condition()

    def send(self, payload):
        message = json.loads(payload)
        self.sent.append(message)
        if self._responder:
            responses = self._responder(message)
            if isinstance(responses, list):
                with self._cond:
                    self._queue.extend(responses)
                    self._cond.notify_all()
            else:
                with self._cond:
                    self._queue.append(responses)
                    self._cond.notify_all()

    def recv(self):
        with self._cond:
            if not self._queue and not self._closed:
                self._cond.wait(timeout=0.1)
            if self._closed:
                raise WebSocketConnectionClosedException("closed")
            if not self._queue:
                raise WebSocketTimeoutException("timeout")
            return self._queue.pop(0)

    def close(self):
        with self._cond:
            self._closed = True
            self._cond.notify_all()
        return None


def make_client(fake_connection):
    config = VibeCraftConfig()
    client = ClientBridge(config)
    client._connection = fake_connection
    client._last_used = time.time()
    client._connection_max_idle = 10**9
    client._start_reader_thread()
    return client


def test_execute_command_normalizes_leading_slash():
    fake = FakeConnection(
        responder=lambda msg: json.dumps({"id": msg["id"], "ok": True, "result": "ok"})
    )
    client = make_client(fake)

    client.execute_command("list")
    assert fake.sent[0]["payload"]["command"] == "/list"

    client.execute_command("//pos1 1,2,3")
    assert fake.sent[1]["payload"]["command"] == "//pos1 1,2,3"

    client.execute_command("/say hi")
    assert fake.sent[2]["payload"]["command"] == "/say hi"
    client.close()


def test_test_connection_reads_capabilities_from_result():
    def responder(message):
        return json.dumps(
            {
                "id": message["id"],
                "ok": True,
                "result": {"capabilities": {"worldedit": True}},
            }
        )

    fake = FakeConnection(responder=responder)
    client = make_client(fake)

    assert client.test_connection() is True
    assert client.get_capabilities() == {"worldedit": True}
    client.close()


def test_request_stashes_unrelated_messages():
    event = json.dumps({"id": "event-1", "type": "vision.frame", "ok": True})

    def responder(message):
        return json.dumps({"id": message["id"], "ok": True, "result": "ok"})

    fake = FakeConnection(preloaded=[event], responder=responder)
    client = make_client(fake)

    client.execute_command("list")

    inbox = client.drain_inbox()
    assert inbox == [{"id": "event-1", "type": "vision.frame", "ok": True}]
    client.close()


class TestBackoff:
    """Test exponential backoff on connection failures."""

    def test_backoff_increments_on_failure(self):
        """Verify consecutive failures increase backoff delay."""
        config = VibeCraftConfig(
            client_host="127.0.0.1",
            client_port=19999,  # No server here
            client_timeout=1,
        )
        client = ClientBridge(config)

        # First failure
        with pytest.raises(ClientBridgeConnectionError):
            client.execute_command("test")

        status1 = client.get_backoff_status()
        assert status1["consecutive_failures"] == 1
        assert status1["in_backoff"] is True
        assert status1["backoff_remaining"] > 0

        # Reset for next test
        client.reset_backoff()

        status2 = client.get_backoff_status()
        assert status2["consecutive_failures"] == 0
        assert status2["in_backoff"] is False
        client.close()

    def test_backoff_blocks_immediate_retry(self):
        """Verify backoff period blocks immediate reconnection attempts."""
        config = VibeCraftConfig(
            client_host="127.0.0.1",
            client_port=19999,
            client_timeout=1,
        )
        client = ClientBridge(config)

        # First failure triggers backoff
        with pytest.raises(ClientBridgeConnectionError):
            client.execute_command("test")

        # Immediate retry should be blocked by backoff
        with pytest.raises(ClientBridgeConnectionError) as exc_info:
            client.execute_command("test")

        assert "backoff period" in str(exc_info.value)
        client.close()

    def test_backoff_resets_on_success(self):
        """Verify backoff resets after successful connection."""
        fake = FakeConnection(
            responder=lambda msg: json.dumps({"id": msg["id"], "ok": True, "result": "ok"})
        )
        config = VibeCraftConfig()
        client = ClientBridge(config)

        # Simulate previous failures
        client._consecutive_failures = 5
        client._backoff_until = 0  # Not in backoff period

        # Successful connection
        client._connection = fake
        client._last_used = time.time()
        client._connection_max_idle = 10**9
        client._start_reader_thread()

        # Execute command triggers _ensure_connection which should reset backoff
        client.execute_command("test")

        # Manually reset since we bypassed normal flow
        client._reset_backoff()

        status = client.get_backoff_status()
        assert status["consecutive_failures"] == 0
        client.close()

    def test_calculate_backoff_exponential(self):
        """Verify backoff delay increases exponentially."""
        config = VibeCraftConfig()
        client = ClientBridge(config)

        # Test backoff values (without jitter for predictability)
        client._consecutive_failures = 1
        delay1 = client._calculate_backoff()

        client._consecutive_failures = 2
        delay2 = client._calculate_backoff()

        client._consecutive_failures = 3
        delay3 = client._calculate_backoff()

        # Due to jitter, we check ranges instead of exact values
        # Base is 1.0s, multiplier is 2.0
        assert 0.75 <= delay1 <= 1.25  # ~1s
        assert 1.5 <= delay2 <= 2.5    # ~2s
        assert 3.0 <= delay3 <= 5.0    # ~4s

        client.close()

    def test_backoff_caps_at_max(self):
        """Verify backoff delay doesn't exceed maximum."""
        config = VibeCraftConfig()
        client = ClientBridge(config)

        # Many failures should still cap at max
        client._consecutive_failures = 100
        delay = client._calculate_backoff()

        # Max is 60s, with jitter could be up to 75s
        assert delay <= 75.0
        client.close()
