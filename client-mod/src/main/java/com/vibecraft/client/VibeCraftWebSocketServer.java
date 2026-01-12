package com.vibecraft.client;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.java_websocket.server.WebSocketServer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

final class VibeCraftWebSocketServer extends WebSocketServer {
    private static final Logger LOGGER = LoggerFactory.getLogger("vibecraft-client-bridge");
    private static final Gson GSON = new Gson();

    private final VibeCraftClientConfig config;
    private final String expectedPath;

    VibeCraftWebSocketServer(InetSocketAddress address, VibeCraftClientConfig config) {
        super(address);
        this.config = config;
        this.expectedPath = VibeCraftClientMod.normalizePath(config.path);
        setConnectionLostTimeout(60);
    }

    @Override
    public void onOpen(WebSocket conn, ClientHandshake handshake) {
        String resource = handshake != null ? handshake.getResourceDescriptor() : null;
        String path = normalizeResource(resource);
        if (!expectedPath.equals(path)) {
            conn.close(1008, "Invalid path");
            return;
        }
        if (!config.enabled) {
            conn.close(1008, "Bridge disabled");
            return;
        }
        LOGGER.info("VibeCraft bridge client connected from {}", conn.getRemoteSocketAddress());
    }

    @Override
    public void onMessage(WebSocket conn, String message) {
        handleMessage(conn, message);
    }

    @Override
    public void onMessage(WebSocket conn, ByteBuffer bytes) {
        String message = StandardCharsets.UTF_8.decode(bytes).toString();
        handleMessage(conn, message);
    }

    @Override
    public void onClose(WebSocket conn, int code, String reason, boolean remote) {
        LOGGER.info("VibeCraft bridge connection closed: {} ({})", reason, code);
    }

    @Override
    public void onError(WebSocket conn, Exception ex) {
        LOGGER.warn("VibeCraft bridge error", ex);
    }

    @Override
    public void onStart() {
        LOGGER.info("VibeCraft bridge server started");
    }

    private void handleMessage(WebSocket conn, String raw) {
        JsonObject request;
        try {
            JsonElement parsed = JsonParser.parseString(raw);
            if (!parsed.isJsonObject()) {
                sendError(conn, null, "Invalid request payload");
                return;
            }
            request = parsed.getAsJsonObject();
        } catch (Exception e) {
            sendError(conn, null, "Invalid JSON");
            return;
        }

        String id = getString(request, "id");
        String type = getString(request, "type");
        if (type == null || type.isEmpty()) {
            sendError(conn, id, "Missing message type");
            return;
        }

        if (!authorize(request)) {
            sendError(conn, id, "Authentication failed");
            return;
        }

        JsonObject payload = request.has("payload") && request.get("payload").isJsonObject()
                ? request.getAsJsonObject("payload")
                : new JsonObject();

        VibeCraftClientMod.BridgeResponse response;
        switch (type) {
            case "hello" -> response = VibeCraftClientMod.handleHello();
            case "server.info" -> response = VibeCraftClientMod.handleServerInfo();
            case "command.execute" -> {
                String command = getString(payload, "command");
                response = VibeCraftClientMod.handleCommandExecute(command);
            }

            // Screenshot capture
            case "screenshot.capture" -> {
                int maxWidth = getInt(payload, "max_width", 1920);
                int maxHeight = getInt(payload, "max_height", 1080);
                response = VibeCraftClientMod.handleScreenshot(maxWidth, maxHeight);
            }

            // Region scanning
            case "region.scan" -> {
                int x1 = getInt(payload, "x1", 0);
                int y1 = getInt(payload, "y1", 0);
                int z1 = getInt(payload, "z1", 0);
                int x2 = getInt(payload, "x2", 0);
                int y2 = getInt(payload, "y2", 0);
                int z2 = getInt(payload, "z2", 0);
                boolean includeStates = getBool(payload, "include_states", false);
                response = VibeCraftClientMod.handleRegionScan(x1, y1, z1, x2, y2, z2, includeStates);
            }
            case "region.heightmap" -> {
                int x1 = getInt(payload, "x1", 0);
                int z1 = getInt(payload, "z1", 0);
                int x2 = getInt(payload, "x2", 0);
                int z2 = getInt(payload, "z2", 0);
                response = VibeCraftClientMod.handleHeightmap(x1, z1, x2, z2);
            }

            // Player context
            case "player.context" -> {
                double reach = getDouble(payload, "reach", 128.0);
                response = VibeCraftClientMod.handlePlayerContext(reach);
            }
            case "player.entities" -> {
                double radius = getDouble(payload, "radius", 32.0);
                response = VibeCraftClientMod.handleNearbyEntities(radius);
            }

            // Palette analysis
            case "palette.analyze" -> {
                int x = getInt(payload, "x", 0);
                int y = getInt(payload, "y", 0);
                int z = getInt(payload, "z", 0);
                int radius = getInt(payload, "radius", 16);
                response = VibeCraftClientMod.handlePaletteAnalyze(x, y, z, radius);
            }
            case "palette.region" -> {
                int x1 = getInt(payload, "x1", 0);
                int y1 = getInt(payload, "y1", 0);
                int z1 = getInt(payload, "z1", 0);
                int x2 = getInt(payload, "x2", 0);
                int y2 = getInt(payload, "y2", 0);
                int z2 = getInt(payload, "z2", 0);
                response = VibeCraftClientMod.handlePaletteRegion(x1, y1, z1, x2, y2, z2);
            }

            // Light analysis
            case "light.analyze" -> {
                int x1 = getInt(payload, "x1", 0);
                int y1 = getInt(payload, "y1", 0);
                int z1 = getInt(payload, "z1", 0);
                int x2 = getInt(payload, "x2", 0);
                int y2 = getInt(payload, "y2", 0);
                int z2 = getInt(payload, "z2", 0);
                int resolution = getInt(payload, "resolution", 2);
                response = VibeCraftClientMod.handleLightAnalysis(x1, y1, z1, x2, y2, z2, resolution);
            }

            // Symmetry check
            case "symmetry.check" -> {
                int x1 = getInt(payload, "x1", 0);
                int y1 = getInt(payload, "y1", 0);
                int z1 = getInt(payload, "z1", 0);
                int x2 = getInt(payload, "x2", 0);
                int y2 = getInt(payload, "y2", 0);
                int z2 = getInt(payload, "z2", 0);
                String axis = getString(payload, "axis");
                if (axis == null || axis.isEmpty()) axis = "x";
                int tolerance = getInt(payload, "tolerance", 0);
                int resolution = getInt(payload, "resolution", 1);
                response = VibeCraftClientMod.handleSymmetryCheck(x1, y1, z1, x2, y2, z2, axis, tolerance, resolution);
            }

            default -> response = VibeCraftClientMod.BridgeResponse.error("Unknown message type: " + type);
        }

        sendResponse(conn, id, response);
    }

    private boolean authorize(JsonObject request) {
        if (config.token == null || config.token.isEmpty()) {
            return true;
        }
        String token = getString(request, "token");
        return config.token.equals(token);
    }

    private void sendResponse(WebSocket conn, String id, VibeCraftClientMod.BridgeResponse response) {
        JsonObject envelope = new JsonObject();
        if (id != null) {
            envelope.addProperty("id", id);
        }
        envelope.addProperty("ok", response.ok);
        if (response.ok) {
            if (response.result != null) {
                envelope.add("result", response.result);
            }
        } else {
            envelope.addProperty("error", response.error != null ? response.error : "Unknown error");
        }
        conn.send(GSON.toJson(envelope));
    }

    private void sendError(WebSocket conn, String id, String message) {
        JsonObject envelope = new JsonObject();
        if (id != null) {
            envelope.addProperty("id", id);
        }
        envelope.addProperty("ok", false);
        envelope.addProperty("error", message);
        conn.send(GSON.toJson(envelope));
    }

    private String getString(JsonObject obj, String field) {
        if (obj == null || !obj.has(field)) {
            return null;
        }
        JsonElement value = obj.get(field);
        if (value == null || value.isJsonNull()) {
            return null;
        }
        return value.getAsString();
    }

    private int getInt(JsonObject obj, String field, int defaultValue) {
        if (obj == null || !obj.has(field)) {
            return defaultValue;
        }
        JsonElement value = obj.get(field);
        if (value == null || value.isJsonNull()) {
            return defaultValue;
        }
        try {
            return value.getAsInt();
        } catch (Exception e) {
            return defaultValue;
        }
    }

    private double getDouble(JsonObject obj, String field, double defaultValue) {
        if (obj == null || !obj.has(field)) {
            return defaultValue;
        }
        JsonElement value = obj.get(field);
        if (value == null || value.isJsonNull()) {
            return defaultValue;
        }
        try {
            return value.getAsDouble();
        } catch (Exception e) {
            return defaultValue;
        }
    }

    private boolean getBool(JsonObject obj, String field, boolean defaultValue) {
        if (obj == null || !obj.has(field)) {
            return defaultValue;
        }
        JsonElement value = obj.get(field);
        if (value == null || value.isJsonNull()) {
            return defaultValue;
        }
        try {
            return value.getAsBoolean();
        } catch (Exception e) {
            return defaultValue;
        }
    }

    private String normalizeResource(String resource) {
        if (resource == null || resource.isBlank()) {
            return "";
        }
        String path = resource;
        int query = path.indexOf('?');
        if (query >= 0) {
            path = path.substring(0, query);
        }
        if (!path.startsWith("/")) {
            path = "/" + path;
        }
        return path;
    }
}
