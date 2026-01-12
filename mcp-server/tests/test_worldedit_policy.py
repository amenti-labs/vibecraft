import pytest

from vibecraft.client_bridge import ClientBridge
from vibecraft.config import VibeCraftConfig
from vibecraft.exceptions import ClientBridgeProtocolError


class FakeConnection:
    def __init__(self):
        self.sent = []

    def send(self, payload):
        self.sent.append(payload)

    def recv(self):
        raise AssertionError("recv should not be called when policy blocks")

    def close(self):
        return None


def make_client(mode, fallback="warn", capabilities=None):
    config = VibeCraftConfig(worldedit_mode=mode, worldedit_fallback=fallback)
    client = ClientBridge(config)
    client._connection = FakeConnection()
    client._capabilities = capabilities or {}
    return client


def test_worldedit_off_blocks():
    client = make_client("off")
    with pytest.raises(ClientBridgeProtocolError):
        client.execute_command("//pos1 1,2,3")
    client.close()


def test_worldedit_force_blocks_when_unavailable():
    client = make_client("force", capabilities={"worldedit": {"available": False}})
    with pytest.raises(ClientBridgeProtocolError):
        client.execute_command("//set stone")
    client.close()


def test_worldedit_auto_disable_blocks_when_unavailable():
    client = make_client("auto", fallback="disable", capabilities={"worldedit": False})
    with pytest.raises(ClientBridgeProtocolError):
        client.execute_command("//set stone")
    client.close()


def test_worldedit_policy_blocks_single_slash_command():
    client = make_client("off", capabilities={"worldedit": True})
    with pytest.raises(ClientBridgeProtocolError):
        client.execute_command("/pos1 1,2,3")
    client.close()
