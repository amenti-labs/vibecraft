package com.vibecraft.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public final class VibeCraftClientConfig {
    private static final Logger LOGGER = LoggerFactory.getLogger("vibecraft-client-config");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final String FILE_NAME = "vibecraft-client.json";

    public boolean enabled = true;
    public boolean allowAiControl = false;
    public String host = "127.0.0.1";
    public int port = 8766;
    public String path = "/vibecraft";
    public String token = "";
    public boolean logCommands = false;

    public static VibeCraftClientConfig load() {
        Path path = configPath();
        if (Files.exists(path)) {
            try (BufferedReader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
                VibeCraftClientConfig config = GSON.fromJson(reader, VibeCraftClientConfig.class);
                if (config == null) {
                    config = new VibeCraftClientConfig();
                }
                config.normalize();
                return config;
            } catch (IOException e) {
                LOGGER.warn("Failed to read config {}, using defaults", path, e);
            }
        }

        VibeCraftClientConfig config = new VibeCraftClientConfig();
        config.save();
        return config;
    }

    public void save() {
        Path path = configPath();
        try {
            Files.createDirectories(path.getParent());
            try (BufferedWriter writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
                GSON.toJson(this, writer);
            }
        } catch (IOException e) {
            LOGGER.warn("Failed to write config {}", path, e);
        }
    }

    private void normalize() {
        if (host == null || host.trim().isEmpty()) {
            host = "127.0.0.1";
        }
        if (port <= 0 || port > 65535) {
            port = 8766;
        }
        if (path == null || path.trim().isEmpty()) {
            path = "/vibecraft";
        } else if (!path.startsWith("/")) {
            path = "/" + path.trim();
        }
        if (token == null) {
            token = "";
        }
    }

    public static Path configPath() {
        return FabricLoader.getInstance().getConfigDir().resolve(FILE_NAME);
    }
}
