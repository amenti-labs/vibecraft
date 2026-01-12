package com.vibecraft.client;

import com.mojang.authlib.GameProfile;
import net.minecraft.client.gl.Framebuffer;
import net.minecraft.client.util.ScreenshotRecorder;
import net.minecraft.text.Text;
import net.minecraft.world.World;

import java.io.File;
import java.lang.reflect.Method;
import java.util.function.Consumer;

/**
 * Compatibility layer for Minecraft API differences between versions.
 * Uses reflection to call version-specific methods.
 */
public class VersionCompat {

    /**
     * Get the top Y coordinate (inclusive) from a world.
     * 1.21.11+: getTopYInclusive()
     * 1.21.1 and earlier: getTopY() - 1 (or use getHeight() + getBottomY() - 1)
     */
    public static int getTopYInclusive(World world) {
        try {
            // Try 1.21.11+ method first
            Method method = world.getClass().getMethod("getTopYInclusive");
            return (Integer) method.invoke(world);
        } catch (NoSuchMethodException e) {
            // Fall back to 1.21.1 and earlier: use getHeight() + getBottomY() - 1
            return world.getHeight() + world.getBottomY() - 1;
        } catch (Exception e) {
            // Last resort fallback
            return 320;
        }
    }

    /**
     * Get the name from a GameProfile.
     * 1.21.11+: name() (Record accessor)
     * 1.21.1 and earlier: getName()
     */
    public static String getProfileName(GameProfile profile) {
        try {
            // Try 1.21.11+ Record accessor first
            Method method = profile.getClass().getMethod("name");
            return (String) method.invoke(profile);
        } catch (NoSuchMethodException e) {
            // Fall back to older getName()
            try {
                Method method = profile.getClass().getMethod("getName");
                return (String) method.invoke(profile);
            } catch (Exception ex) {
                return "Unknown";
            }
        } catch (Exception e) {
            return "Unknown";
        }
    }

    /**
     * Save a screenshot with version-appropriate method signature.
     * 1.21.11+: saveScreenshot(File, String, Framebuffer, int downscale, Consumer<Text>)
     * 1.21.1 and earlier: saveScreenshot(File, String, Framebuffer, Consumer<Text>)
     */
    public static void saveScreenshot(File directory, String fileName, Framebuffer framebuffer,
                                      int downscaleFactor, Consumer<Text> messageReceiver) {
        try {
            // Try 1.21.11+ method with downscale parameter
            Method method = ScreenshotRecorder.class.getMethod("saveScreenshot",
                    File.class, String.class, Framebuffer.class, int.class, Consumer.class);
            method.invoke(null, directory, fileName, framebuffer, downscaleFactor, messageReceiver);
        } catch (NoSuchMethodException e) {
            // Fall back to 1.21.1 method without downscale
            try {
                Method method = ScreenshotRecorder.class.getMethod("saveScreenshot",
                        File.class, String.class, Framebuffer.class, Consumer.class);
                method.invoke(null, directory, fileName, framebuffer, messageReceiver);
            } catch (Exception ex) {
                throw new RuntimeException("Failed to find compatible saveScreenshot method", ex);
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to save screenshot", e);
        }
    }
}
