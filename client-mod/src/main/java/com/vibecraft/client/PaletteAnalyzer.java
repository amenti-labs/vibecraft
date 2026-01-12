package com.vibecraft.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.block.BlockState;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.world.ClientWorld;
import net.minecraft.registry.Registries;
import net.minecraft.util.math.BlockPos;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;

/**
 * Analyzes block usage in a region to understand building style and palette.
 */
public final class PaletteAnalyzer {
    private static final Logger LOGGER = LoggerFactory.getLogger("vibecraft-palette");
    private static final int MAX_RADIUS = 64;
    private static final int MAX_BLOCKS = 128 * 128 * 128;

    // Block categories for style analysis
    private static final Set<String> STRUCTURAL_BLOCKS = Set.of(
        "stone", "cobblestone", "stone_bricks", "bricks", "deepslate",
        "oak_planks", "spruce_planks", "birch_planks", "jungle_planks",
        "acacia_planks", "dark_oak_planks", "mangrove_planks", "cherry_planks",
        "oak_log", "spruce_log", "birch_log", "jungle_log",
        "sandstone", "red_sandstone", "prismarine", "quartz_block",
        "concrete", "terracotta"
    );

    private static final Set<String> DECORATIVE_BLOCKS = Set.of(
        "glass", "glass_pane", "stained_glass",
        "lantern", "torch", "candle", "sea_lantern", "glowstone",
        "flower_pot", "painting", "item_frame",
        "carpet", "banner", "bell"
    );

    private static final Set<String> NATURAL_BLOCKS = Set.of(
        "grass_block", "dirt", "sand", "gravel", "clay",
        "oak_leaves", "spruce_leaves", "birch_leaves",
        "azalea_leaves", "flowering_azalea_leaves",
        "moss_block", "moss_carpet", "vine"
    );

    private PaletteAnalyzer() {}

    /**
     * Analyze block palette in a spherical radius around a point.
     */
    public static JsonObject analyzeRadius(int centerX, int centerY, int centerZ, int radius) {
        JsonObject result = new JsonObject();

        MinecraftClient client = MinecraftClient.getInstance();
        ClientWorld world = client.world;

        if (world == null) {
            result.addProperty("error", "Not in a world");
            return result;
        }

        if (radius > MAX_RADIUS) {
            result.addProperty("error", "Radius too large: " + radius + " (max " + MAX_RADIUS + ")");
            return result;
        }

        Map<String, Integer> blockCounts = new LinkedHashMap<>();
        Map<String, Integer> categoryCounts = new LinkedHashMap<>();
        categoryCounts.put("structural", 0);
        categoryCounts.put("decorative", 0);
        categoryCounts.put("natural", 0);
        categoryCounts.put("other", 0);

        int totalBlocks = 0;
        int airBlocks = 0;
        int radiusSq = radius * radius;

        BlockPos.Mutable pos = new BlockPos.Mutable();
        for (int y = centerY - radius; y <= centerY + radius; y++) {
            for (int z = centerZ - radius; z <= centerZ + radius; z++) {
                for (int x = centerX - radius; x <= centerX + radius; x++) {
                    int dx = x - centerX;
                    int dy = y - centerY;
                    int dz = z - centerZ;
                    if (dx * dx + dy * dy + dz * dz > radiusSq) {
                        continue; // Outside sphere
                    }

                    pos.set(x, y, z);
                    BlockState state = world.getBlockState(pos);

                    if (state.isAir()) {
                        airBlocks++;
                        continue;
                    }

                    totalBlocks++;
                    String blockId = Registries.BLOCK.getId(state.getBlock()).toString();
                    String simpleName = blockId.replace("minecraft:", "");

                    blockCounts.merge(blockId, 1, Integer::sum);

                    // Categorize
                    String category = categorizeBlock(simpleName);
                    categoryCounts.merge(category, 1, Integer::sum);
                }
            }
        }

        // Sort by count descending
        List<Map.Entry<String, Integer>> sorted = new ArrayList<>(blockCounts.entrySet());
        sorted.sort((a, b) -> b.getValue().compareTo(a.getValue()));

        // Build palette (top 20 blocks)
        JsonArray palette = new JsonArray();
        int paletteLimit = Math.min(20, sorted.size());
        for (int i = 0; i < paletteLimit; i++) {
            Map.Entry<String, Integer> entry = sorted.get(i);
            JsonObject block = new JsonObject();
            block.addProperty("block", entry.getKey());
            block.addProperty("count", entry.getValue());
            block.addProperty("percentage", totalBlocks > 0 ? (entry.getValue() * 100.0 / totalBlocks) : 0);
            palette.add(block);
        }
        result.add("palette", palette);

        // Category breakdown
        JsonObject categories = new JsonObject();
        for (Map.Entry<String, Integer> entry : categoryCounts.entrySet()) {
            JsonObject cat = new JsonObject();
            cat.addProperty("count", entry.getValue());
            cat.addProperty("percentage", totalBlocks > 0 ? (entry.getValue() * 100.0 / totalBlocks) : 0);
            categories.add(entry.getKey(), cat);
        }
        result.add("categories", categories);

        // Stats
        JsonObject stats = new JsonObject();
        stats.addProperty("total_solid", totalBlocks);
        stats.addProperty("total_air", airBlocks);
        stats.addProperty("unique_types", blockCounts.size());
        stats.addProperty("radius", radius);
        result.add("stats", stats);

        // Origin
        JsonArray origin = new JsonArray();
        origin.add(centerX);
        origin.add(centerY);
        origin.add(centerZ);
        result.add("origin", origin);

        // Infer style
        String inferredStyle = inferStyle(categoryCounts, sorted, totalBlocks);
        result.addProperty("inferred_style", inferredStyle);

        // Material suggestions based on dominant blocks
        JsonArray suggestions = generateSuggestions(sorted, totalBlocks);
        result.add("material_suggestions", suggestions);

        LOGGER.info("Palette analysis: {} blocks, {} unique types, style={}",
            totalBlocks, blockCounts.size(), inferredStyle);

        return result;
    }

    /**
     * Analyze a rectangular region.
     */
    public static JsonObject analyzeRegion(int x1, int y1, int z1, int x2, int y2, int z2) {
        JsonObject result = new JsonObject();

        MinecraftClient client = MinecraftClient.getInstance();
        ClientWorld world = client.world;

        if (world == null) {
            result.addProperty("error", "Not in a world");
            return result;
        }

        int minX = Math.min(x1, x2);
        int maxX = Math.max(x1, x2);
        int minY = Math.min(y1, y2);
        int maxY = Math.max(y1, y2);
        int minZ = Math.min(z1, z2);
        int maxZ = Math.max(z1, z2);

        int sizeX = maxX - minX + 1;
        int sizeY = maxY - minY + 1;
        int sizeZ = maxZ - minZ + 1;
        int volume = sizeX * sizeY * sizeZ;

        if (volume > MAX_BLOCKS) {
            result.addProperty("error", "Region too large: " + volume + " blocks (max " + MAX_BLOCKS + ")");
            return result;
        }

        Map<String, Integer> blockCounts = new LinkedHashMap<>();
        int totalBlocks = 0;
        int airBlocks = 0;

        BlockPos.Mutable pos = new BlockPos.Mutable();
        for (int y = minY; y <= maxY; y++) {
            for (int z = minZ; z <= maxZ; z++) {
                for (int x = minX; x <= maxX; x++) {
                    pos.set(x, y, z);
                    BlockState state = world.getBlockState(pos);

                    if (state.isAir()) {
                        airBlocks++;
                        continue;
                    }

                    totalBlocks++;
                    String blockId = Registries.BLOCK.getId(state.getBlock()).toString();
                    blockCounts.merge(blockId, 1, Integer::sum);
                }
            }
        }

        // Sort by count descending
        List<Map.Entry<String, Integer>> sorted = new ArrayList<>(blockCounts.entrySet());
        sorted.sort((a, b) -> b.getValue().compareTo(a.getValue()));

        // Build full palette
        JsonArray palette = new JsonArray();
        for (Map.Entry<String, Integer> entry : sorted) {
            JsonObject block = new JsonObject();
            block.addProperty("block", entry.getKey());
            block.addProperty("count", entry.getValue());
            block.addProperty("percentage", totalBlocks > 0 ? (entry.getValue() * 100.0 / totalBlocks) : 0);
            palette.add(block);
        }
        result.add("palette", palette);

        // Stats
        JsonObject stats = new JsonObject();
        stats.addProperty("total_solid", totalBlocks);
        stats.addProperty("total_air", airBlocks);
        stats.addProperty("unique_types", blockCounts.size());
        stats.addProperty("volume", volume);
        result.add("stats", stats);

        // Dimensions
        JsonArray dimensions = new JsonArray();
        dimensions.add(sizeX);
        dimensions.add(sizeY);
        dimensions.add(sizeZ);
        result.add("dimensions", dimensions);

        // Origin
        JsonArray origin = new JsonArray();
        origin.add(minX);
        origin.add(minY);
        origin.add(minZ);
        result.add("origin", origin);

        return result;
    }

    private static String categorizeBlock(String blockName) {
        // Check if any structural block is contained in the name
        for (String structural : STRUCTURAL_BLOCKS) {
            if (blockName.contains(structural)) {
                return "structural";
            }
        }

        for (String decorative : DECORATIVE_BLOCKS) {
            if (blockName.contains(decorative)) {
                return "decorative";
            }
        }

        for (String natural : NATURAL_BLOCKS) {
            if (blockName.contains(natural)) {
                return "natural";
            }
        }

        return "other";
    }

    private static String inferStyle(Map<String, Integer> categories,
                                     List<Map.Entry<String, Integer>> sortedBlocks,
                                     int totalBlocks) {
        if (totalBlocks < 10) {
            return "minimal";
        }

        // Check dominant materials
        Set<String> topBlocks = new HashSet<>();
        int checkCount = Math.min(5, sortedBlocks.size());
        for (int i = 0; i < checkCount; i++) {
            topBlocks.add(sortedBlocks.get(i).getKey().replace("minecraft:", ""));
        }

        // Style detection heuristics
        if (containsAny(topBlocks, "stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks")) {
            if (containsAny(topBlocks, "oak_", "dark_oak_")) {
                return "medieval";
            }
            return "castle";
        }

        if (containsAny(topBlocks, "quartz", "white_concrete", "glass")) {
            return "modern";
        }

        if (containsAny(topBlocks, "cherry_", "bamboo_")) {
            return "japanese";
        }

        if (containsAny(topBlocks, "spruce_", "cobblestone")) {
            return "rustic";
        }

        if (containsAny(topBlocks, "sandstone", "cut_sandstone")) {
            return "desert";
        }

        if (containsAny(topBlocks, "prismarine", "sea_lantern")) {
            return "ocean";
        }

        if (containsAny(topBlocks, "deepslate", "blackstone")) {
            return "gothic";
        }

        int naturalCount = categories.getOrDefault("natural", 0);
        if (naturalCount > totalBlocks * 0.5) {
            return "natural";
        }

        return "mixed";
    }

    private static boolean containsAny(Set<String> blocks, String... patterns) {
        for (String block : blocks) {
            for (String pattern : patterns) {
                if (block.contains(pattern)) {
                    return true;
                }
            }
        }
        return false;
    }

    private static JsonArray generateSuggestions(List<Map.Entry<String, Integer>> sorted, int total) {
        JsonArray suggestions = new JsonArray();

        if (sorted.isEmpty()) {
            return suggestions;
        }

        // Primary material (60% rule)
        Map.Entry<String, Integer> primary = sorted.get(0);
        JsonObject primarySuggestion = new JsonObject();
        primarySuggestion.addProperty("role", "primary");
        primarySuggestion.addProperty("block", primary.getKey());
        primarySuggestion.addProperty("usage", "main walls, floors");
        suggestions.add(primarySuggestion);

        // Secondary material (30% rule)
        if (sorted.size() > 1) {
            Map.Entry<String, Integer> secondary = sorted.get(1);
            JsonObject secondarySuggestion = new JsonObject();
            secondarySuggestion.addProperty("role", "secondary");
            secondarySuggestion.addProperty("block", secondary.getKey());
            secondarySuggestion.addProperty("usage", "trim, roof, accents");
            suggestions.add(secondarySuggestion);
        }

        // Accent material (10% rule)
        if (sorted.size() > 2) {
            Map.Entry<String, Integer> accent = sorted.get(2);
            JsonObject accentSuggestion = new JsonObject();
            accentSuggestion.addProperty("role", "accent");
            accentSuggestion.addProperty("block", accent.getKey());
            accentSuggestion.addProperty("usage", "details, highlights");
            suggestions.add(accentSuggestion);
        }

        return suggestions;
    }
}
