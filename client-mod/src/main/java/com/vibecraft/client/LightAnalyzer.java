package com.vibecraft.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.block.BlockState;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.world.ClientWorld;
import net.minecraft.registry.Registries;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.LightType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;

/**
 * Analyzes lighting levels in a region using client-side data.
 * The client has access to both block light and sky light values.
 */
public final class LightAnalyzer {
    private static final Logger LOGGER = LoggerFactory.getLogger("vibecraft-light");
    private static final int MAX_BLOCKS = 128 * 128 * 64; // Large but reasonable limit

    // Blocks that emit light
    private static final Set<String> LIGHT_SOURCES = Set.of(
        "torch", "wall_torch", "soul_torch", "soul_wall_torch",
        "lantern", "soul_lantern", "sea_lantern", "glowstone",
        "shroomlight", "crying_obsidian", "redstone_lamp",
        "jack_o_lantern", "campfire", "soul_campfire",
        "candle", "magma_block", "end_rod", "froglight",
        "beacon", "conduit", "respawn_anchor", "lava"
    );

    private LightAnalyzer() {}

    /**
     * Analyze lighting levels in a rectangular region.
     * Returns light distribution, dark spots, and optimal placement suggestions.
     */
    public static JsonObject analyzeRegion(int x1, int y1, int z1, int x2, int y2, int z2, int resolution) {
        JsonObject result = new JsonObject();

        MinecraftClient client = MinecraftClient.getInstance();
        ClientWorld world = client.world;

        if (world == null) {
            result.addProperty("error", "Not in a world");
            return result;
        }

        // Normalize coordinates
        int minX = Math.min(x1, x2);
        int maxX = Math.max(x1, x2);
        int minY = Math.min(y1, y2);
        int maxY = Math.max(y1, y2);
        int minZ = Math.min(z1, z2);
        int maxZ = Math.max(z1, z2);

        int sizeX = maxX - minX + 1;
        int sizeY = maxY - minY + 1;
        int sizeZ = maxZ - minZ + 1;

        // Apply resolution (sampling every N blocks)
        if (resolution < 1) resolution = 1;
        if (resolution > 4) resolution = 4;

        int sampledSizeX = (sizeX + resolution - 1) / resolution;
        int sampledSizeY = (sizeY + resolution - 1) / resolution;
        int sampledSizeZ = (sizeZ + resolution - 1) / resolution;
        int totalSamples = sampledSizeX * sampledSizeY * sampledSizeZ;

        if (totalSamples > MAX_BLOCKS) {
            result.addProperty("error", "Region too large: " + totalSamples + " samples (max " + MAX_BLOCKS + "). Try higher resolution.");
            return result;
        }

        // Light level statistics
        int[] lightDistribution = new int[16]; // 0-15 light levels
        List<JsonObject> darkSpots = new ArrayList<>();
        List<JsonObject> existingLights = new ArrayList<>();
        long totalLight = 0;
        int sampleCount = 0;
        int airBlocks = 0;

        BlockPos.Mutable pos = new BlockPos.Mutable();

        for (int y = minY; y <= maxY; y += resolution) {
            for (int z = minZ; z <= maxZ; z += resolution) {
                for (int x = minX; x <= maxX; x += resolution) {
                    pos.set(x, y, z);
                    BlockState state = world.getBlockState(pos);

                    // Skip solid blocks - we care about light in air/passable spaces
                    if (!state.isAir() && state.isOpaque()) {
                        // Check if it's a light source
                        String blockId = Registries.BLOCK.getId(state.getBlock()).toString();
                        String simpleName = blockId.replace("minecraft:", "");
                        if (isLightSource(simpleName)) {
                            JsonObject light = new JsonObject();
                            JsonArray position = new JsonArray();
                            position.add(x);
                            position.add(y);
                            position.add(z);
                            light.add("position", position);
                            light.addProperty("block", blockId);
                            light.addProperty("light_level", state.getLuminance());
                            existingLights.add(light);
                        }
                        continue;
                    }

                    airBlocks++;
                    sampleCount++;

                    // Get combined light level (max of block light and sky light)
                    int blockLight = world.getLightLevel(LightType.BLOCK, pos);
                    int skyLight = world.getLightLevel(LightType.SKY, pos);
                    int combinedLight = Math.max(blockLight, skyLight);

                    lightDistribution[combinedLight]++;
                    totalLight += combinedLight;

                    // Track dark spots (light < 8 allows mob spawning)
                    if (combinedLight < 8 && darkSpots.size() < 100) {
                        JsonObject darkSpot = new JsonObject();
                        JsonArray position = new JsonArray();
                        position.add(x);
                        position.add(y);
                        position.add(z);
                        darkSpot.add("position", position);
                        darkSpot.addProperty("block_light", blockLight);
                        darkSpot.addProperty("sky_light", skyLight);
                        darkSpot.addProperty("combined", combinedLight);
                        darkSpot.addProperty("mob_spawn_risk", combinedLight < 1 ? "high" : "medium");
                        darkSpots.add(darkSpot);
                    }
                }
            }
        }

        // Calculate statistics
        double avgLight = sampleCount > 0 ? (double) totalLight / sampleCount : 0;

        // Count by category
        int wellLit = 0; // >= 12
        int dim = 0;     // 8-11
        int dark = 0;    // < 8
        for (int i = 0; i < 16; i++) {
            if (i >= 12) wellLit += lightDistribution[i];
            else if (i >= 8) dim += lightDistribution[i];
            else dark += lightDistribution[i];
        }

        // Build result
        JsonObject stats = new JsonObject();
        stats.addProperty("total_samples", sampleCount);
        stats.addProperty("air_blocks", airBlocks);
        stats.addProperty("average_light_level", Math.round(avgLight * 10) / 10.0);
        stats.addProperty("dark_spots_count", dark);
        stats.addProperty("existing_lights", existingLights.size());
        result.add("stats", stats);

        // Light distribution
        JsonObject distribution = new JsonObject();
        distribution.addProperty("well_lit", wellLit);
        distribution.addProperty("well_lit_percentage", sampleCount > 0 ? Math.round(wellLit * 1000.0 / sampleCount) / 10.0 : 0);
        distribution.addProperty("dim", dim);
        distribution.addProperty("dim_percentage", sampleCount > 0 ? Math.round(dim * 1000.0 / sampleCount) / 10.0 : 0);
        distribution.addProperty("dark", dark);
        distribution.addProperty("dark_percentage", sampleCount > 0 ? Math.round(dark * 1000.0 / sampleCount) / 10.0 : 0);
        result.add("light_distribution", distribution);

        // Full histogram
        JsonArray histogram = new JsonArray();
        for (int i = 0; i < 16; i++) {
            histogram.add(lightDistribution[i]);
        }
        result.add("histogram", histogram);

        // Dark spots
        JsonArray darkSpotsArray = new JsonArray();
        for (JsonObject spot : darkSpots) {
            darkSpotsArray.add(spot);
        }
        result.add("dark_spots", darkSpotsArray);

        // Existing light sources
        JsonArray existingLightsArray = new JsonArray();
        for (JsonObject light : existingLights) {
            existingLightsArray.add(light);
        }
        result.add("existing_lights", existingLightsArray);

        // Mob spawn risk assessment
        String mobSpawnRisk;
        if (dark == 0) {
            mobSpawnRisk = "none";
        } else if (dark < sampleCount * 0.1) {
            mobSpawnRisk = "low";
        } else if (dark < sampleCount * 0.3) {
            mobSpawnRisk = "medium";
        } else {
            mobSpawnRisk = "high";
        }
        result.addProperty("mob_spawn_risk", mobSpawnRisk);

        // Generate optimal light placement suggestions
        JsonArray placements = generateOptimalPlacements(darkSpots, minY, maxY);
        result.add("optimal_placements", placements);

        // Summary
        String summary;
        if (avgLight >= 12) {
            summary = "Excellent lighting. No mob spawning possible.";
        } else if (avgLight >= 8) {
            summary = "Good lighting with some dim areas. Consider adding lights in dark spots.";
        } else if (avgLight >= 4) {
            summary = "Poor lighting. Significant mob spawning risk. Add more light sources.";
        } else {
            summary = "Very dark area. High mob spawning risk. Needs substantial lighting.";
        }
        result.addProperty("summary", summary);

        // Region info
        JsonArray dimensions = new JsonArray();
        dimensions.add(sizeX);
        dimensions.add(sizeY);
        dimensions.add(sizeZ);
        result.add("dimensions", dimensions);

        JsonArray origin = new JsonArray();
        origin.add(minX);
        origin.add(minY);
        origin.add(minZ);
        result.add("origin", origin);

        result.addProperty("resolution", resolution);

        LOGGER.info("Light analysis: {} samples, avg={}, dark={}, risk={}",
            sampleCount, Math.round(avgLight * 10) / 10.0, dark, mobSpawnRisk);

        return result;
    }

    private static boolean isLightSource(String blockName) {
        for (String source : LIGHT_SOURCES) {
            if (blockName.contains(source)) {
                return true;
            }
        }
        return false;
    }

    private static JsonArray generateOptimalPlacements(List<JsonObject> darkSpots, int minY, int maxY) {
        JsonArray placements = new JsonArray();
        if (darkSpots.isEmpty()) {
            return placements;
        }

        // Cluster dark spots and suggest lights at cluster centers
        // Simple algorithm: suggest a light every ~14 blocks in dark areas (torch light radius)
        Set<String> covered = new HashSet<>();
        int suggestedCount = 0;

        for (JsonObject spot : darkSpots) {
            if (suggestedCount >= 20) break; // Limit suggestions

            JsonArray pos = spot.getAsJsonArray("position");
            int x = pos.get(0).getAsInt();
            int y = pos.get(1).getAsInt();
            int z = pos.get(2).getAsInt();

            // Check if this area is already covered by a previous suggestion
            String key = (x / 14) + "," + (y / 8) + "," + (z / 14);
            if (covered.contains(key)) {
                continue;
            }
            covered.add(key);

            JsonObject placement = new JsonObject();
            JsonArray position = new JsonArray();
            position.add(x);
            position.add(y);
            position.add(z);
            placement.add("position", position);

            // Suggest appropriate light source
            String suggestedSource;
            String reason;
            if (y < minY + 3) {
                suggestedSource = "lantern";
                reason = "Floor level - lantern provides good coverage";
            } else if (y > maxY - 3) {
                suggestedSource = "lantern";
                reason = "Ceiling area - hanging lantern recommended";
            } else {
                suggestedSource = "torch";
                reason = "Wall placement recommended";
            }
            placement.addProperty("suggested_source", suggestedSource);
            placement.addProperty("reason", reason);

            placements.add(placement);
            suggestedCount++;
        }

        return placements;
    }
}
