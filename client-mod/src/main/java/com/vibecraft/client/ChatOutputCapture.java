package com.vibecraft.client;

import net.fabricmc.fabric.api.client.message.v1.ClientReceiveMessageEvents;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Captures chat/game messages for a short window after a command is executed.
 * This allows the client bridge to return command output to the MCP server.
 */
public final class ChatOutputCapture {
    private static final Logger LOGGER = LoggerFactory.getLogger("vibecraft-capture");

    // Thread-safe list for captured messages
    private static final List<String> capturedMessages = Collections.synchronizedList(new ArrayList<>());

    // Capture state
    private static volatile boolean capturing = false;
    private static volatile long captureStartTime = 0;

    // How long to capture messages after a command (milliseconds)
    private static final long CAPTURE_WINDOW_MS = 500;

    private ChatOutputCapture() {}

    /**
     * Register the message listener. Call this once during mod initialization.
     */
    public static void register() {
        // Listen for game messages (system messages, command output)
        ClientReceiveMessageEvents.GAME.register((message, overlay) -> {
            // Skip overlay messages (action bar) - we want system messages
            if (capturing && !overlay) {
                long elapsed = System.currentTimeMillis() - captureStartTime;
                if (elapsed < CAPTURE_WINDOW_MS) {
                    String text = message.getString();
                    capturedMessages.add(text);
                    LOGGER.debug("Captured message: {}", text);
                }
            }
        });

        // Also listen for chat messages in case some servers send output as chat
        ClientReceiveMessageEvents.CHAT.register((message, signedMessage, sender, params, receptionTimestamp) -> {
            if (capturing) {
                long elapsed = System.currentTimeMillis() - captureStartTime;
                if (elapsed < CAPTURE_WINDOW_MS) {
                    String text = message.getString();
                    // Only capture if it looks like command output (not player chat)
                    if (sender == null) {
                        capturedMessages.add(text);
                        LOGGER.debug("Captured chat message: {}", text);
                    }
                }
            }
        });

        LOGGER.info("ChatOutputCapture registered");
    }

    /**
     * Start capturing messages. Clears any previously captured messages.
     */
    public static void startCapture() {
        synchronized (capturedMessages) {
            capturedMessages.clear();
            captureStartTime = System.currentTimeMillis();
            capturing = true;
        }
        LOGGER.debug("Started capture");
    }

    /**
     * Stop capturing and return all captured messages as a single string.
     * @return The captured output, or empty string if nothing was captured.
     */
    public static String stopAndGetOutput() {
        capturing = false;

        synchronized (capturedMessages) {
            if (capturedMessages.isEmpty()) {
                LOGGER.debug("No messages captured");
                return "";
            }

            String result = String.join("\n", capturedMessages);
            capturedMessages.clear();
            LOGGER.debug("Returning captured output: {}", result);
            return result;
        }
    }

    /**
     * Check if currently capturing.
     */
    public static boolean isCapturing() {
        return capturing;
    }

    /**
     * Get the capture window duration in milliseconds.
     */
    public static long getCaptureWindowMs() {
        return CAPTURE_WINDOW_MS;
    }
}
