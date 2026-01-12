package com.vibecraft.client;

import com.google.gson.JsonObject;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gl.Framebuffer;
import net.minecraft.client.util.ScreenshotRecorder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Base64;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Captures screenshots from the Minecraft client and returns them as base64.
 * Uses Minecraft's built-in ScreenshotRecorder for reliable capture across versions.
 */
public final class ScreenshotHandler {
    private static final Logger LOGGER = LoggerFactory.getLogger("vibecraft-screenshot");

    private ScreenshotHandler() {}

    /**
     * Capture a screenshot and return as base64 PNG.
     * Must be called from the render thread.
     */
    public static JsonObject capture(int maxWidth, int maxHeight) {
        JsonObject result = new JsonObject();

        MinecraftClient client = MinecraftClient.getInstance();
        Framebuffer framebuffer = client.getFramebuffer();

        if (framebuffer == null) {
            result.addProperty("error", "No framebuffer available");
            return result;
        }

        int fbWidth = framebuffer.textureWidth;
        int fbHeight = framebuffer.textureHeight;

        try {
            // Calculate downscale factor to fit within max dimensions
            // Must evenly divide both width and height (Minecraft requirement)
            int downscaleFactor = 1;
            if (maxWidth > 0 && maxHeight > 0) {
                // Find smallest factor that fits max dimensions AND divides evenly
                for (int factor = 1; factor <= 8; factor++) {
                    if (fbWidth % factor == 0 && fbHeight % factor == 0) {
                        if (fbWidth / factor <= maxWidth && fbHeight / factor <= maxHeight) {
                            downscaleFactor = factor;
                            break;
                        }
                        downscaleFactor = factor;  // Keep increasing if doesn't fit yet
                    }
                }
                // Final check: ensure dimensions are divisible
                if (fbWidth % downscaleFactor != 0 || fbHeight % downscaleFactor != 0) {
                    downscaleFactor = 1;  // Fall back to no scaling
                }
            }

            // Create temp directory for screenshot
            Path tempDir = Files.createTempDirectory("vibecraft-screenshot");
            File screenshotDir = tempDir.toFile();

            // Use atomic reference to capture the file path
            AtomicReference<File> capturedFile = new AtomicReference<>();
            CompletableFuture<Void> future = new CompletableFuture<>();

            // Take screenshot using Minecraft's built-in mechanism
            final int finalDownscale = downscaleFactor;
            VersionCompat.saveScreenshot(screenshotDir, null, framebuffer, finalDownscale, (message) -> {
                // Extract filename from message and find the file
                String msgText = message.getString();
                LOGGER.debug("Screenshot callback: {}", msgText);

                // Find the screenshot file in temp dir
                File[] files = screenshotDir.listFiles((dir, name) -> name.endsWith(".png"));
                if (files != null && files.length > 0) {
                    capturedFile.set(files[0]);
                }
                future.complete(null);
            });

            // Wait for callback (with timeout)
            try {
                future.get(5, java.util.concurrent.TimeUnit.SECONDS);
            } catch (Exception e) {
                LOGGER.warn("Screenshot callback timeout, checking for file anyway");
            }

            // Find the file if not set by callback
            if (capturedFile.get() == null) {
                File[] files = screenshotDir.listFiles((dir, name) -> name.endsWith(".png"));
                if (files != null && files.length > 0) {
                    capturedFile.set(files[0]);
                }
            }

            File screenshotFile = capturedFile.get();
            if (screenshotFile == null || !screenshotFile.exists()) {
                result.addProperty("error", "Screenshot file not created");
                // Cleanup
                deleteDirectory(screenshotDir);
                return result;
            }

            // Read file and encode to base64
            byte[] pngBytes = Files.readAllBytes(screenshotFile.toPath());
            String base64 = Base64.getEncoder().encodeToString(pngBytes);

            int finalWidth = fbWidth / finalDownscale;
            int finalHeight = fbHeight / finalDownscale;

            result.addProperty("image", "data:image/png;base64," + base64);
            result.addProperty("width", finalWidth);
            result.addProperty("height", finalHeight);
            result.addProperty("original_width", fbWidth);
            result.addProperty("original_height", fbHeight);

            // Add player context
            if (client.player != null) {
                JsonObject position = new JsonObject();
                position.addProperty("x", client.player.getX());
                position.addProperty("y", client.player.getY());
                position.addProperty("z", client.player.getZ());
                result.add("player_position", position);

                JsonObject rotation = new JsonObject();
                rotation.addProperty("yaw", client.player.getYaw());
                rotation.addProperty("pitch", client.player.getPitch());
                result.add("player_rotation", rotation);
            }

            LOGGER.info("Screenshot captured: {}x{} -> {}x{}, {} bytes",
                fbWidth, fbHeight, finalWidth, finalHeight, pngBytes.length);

            // Cleanup temp files
            screenshotFile.delete();
            deleteDirectory(screenshotDir);

        } catch (Exception e) {
            LOGGER.error("Failed to capture screenshot", e);
            result.addProperty("error", "Screenshot capture failed: " + e.getMessage());
        }

        return result;
    }

    private static void deleteDirectory(File dir) {
        if (dir.isDirectory()) {
            File[] files = dir.listFiles();
            if (files != null) {
                for (File file : files) {
                    deleteDirectory(file);
                }
            }
        }
        dir.delete();
    }
}
