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
 * Scans blocks in a region and returns structured data.
 */
public final class RegionScanner {
    private static final Logger LOGGER = LoggerFactory.getLogger("vibecraft-scanner");
    private static final int MAX_BLOCKS = 64 * 64 * 64; // 262,144 blocks max

    private RegionScanner() {}

    /**
     * Scan a region and return block data.
     * Uses palette compression for efficiency.
     */
    public static JsonObject scanRegion(int x1, int y1, int z1, int x2, int y2, int z2, boolean includeStates) {
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
        int totalBlocks = sizeX * sizeY * sizeZ;

        if (totalBlocks > MAX_BLOCKS) {
            result.addProperty("error", "Region too large: " + totalBlocks + " blocks (max " + MAX_BLOCKS + ")");
            return result;
        }

        // Build palette and block data
        Map<String, Integer> paletteMap = new LinkedHashMap<>();
        List<String> palette = new ArrayList<>();
        List<Integer> blocks = new ArrayList<>();

        BlockPos.Mutable pos = new BlockPos.Mutable();
        int airCount = 0;
        int solidCount = 0;

        for (int y = minY; y <= maxY; y++) {
            for (int z = minZ; z <= maxZ; z++) {
                for (int x = minX; x <= maxX; x++) {
                    pos.set(x, y, z);
                    BlockState state = world.getBlockState(pos);

                    String blockId;
                    if (includeStates && !state.getEntries().isEmpty()) {
                        // Include block state
                        blockId = Registries.BLOCK.getId(state.getBlock()).toString() +
                            state.toString().substring(state.toString().indexOf('['));
                    } else {
                        blockId = Registries.BLOCK.getId(state.getBlock()).toString();
                    }

                    // Get or create palette index
                    Integer index = paletteMap.get(blockId);
                    if (index == null) {
                        index = palette.size();
                        paletteMap.put(blockId, index);
                        palette.add(blockId);
                    }
                    blocks.add(index);

                    if (state.isAir()) {
                        airCount++;
                    } else {
                        solidCount++;
                    }
                }
            }
        }

        // Apply run-length encoding for compression
        JsonArray compressedBlocks = new JsonArray();
        if (!blocks.isEmpty()) {
            int currentValue = blocks.get(0);
            int runLength = 1;

            for (int i = 1; i < blocks.size(); i++) {
                int value = blocks.get(i);
                if (value == currentValue) {
                    runLength++;
                } else {
                    // Store as [value, count] for runs > 1, or just value for single blocks
                    if (runLength > 1) {
                        JsonArray run = new JsonArray();
                        run.add(currentValue);
                        run.add(runLength);
                        compressedBlocks.add(run);
                    } else {
                        compressedBlocks.add(currentValue);
                    }
                    currentValue = value;
                    runLength = 1;
                }
            }
            // Don't forget the last run
            if (runLength > 1) {
                JsonArray run = new JsonArray();
                run.add(currentValue);
                run.add(runLength);
                compressedBlocks.add(run);
            } else {
                compressedBlocks.add(currentValue);
            }
        }

        // Build result
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

        JsonArray paletteArray = new JsonArray();
        for (String block : palette) {
            paletteArray.add(block);
        }
        result.add("palette", paletteArray);
        result.add("blocks", compressedBlocks);

        JsonObject stats = new JsonObject();
        stats.addProperty("total", totalBlocks);
        stats.addProperty("air", airCount);
        stats.addProperty("solid", solidCount);
        stats.addProperty("unique_types", palette.size());
        result.add("stats", stats);

        LOGGER.info("Region scan: {}x{}x{} = {} blocks, {} unique types",
            sizeX, sizeY, sizeZ, totalBlocks, palette.size());

        return result;
    }

    /**
     * Get a heightmap for a region (Y values for each X,Z).
     */
    public static JsonObject getHeightmap(int x1, int z1, int x2, int z2) {
        JsonObject result = new JsonObject();

        MinecraftClient client = MinecraftClient.getInstance();
        ClientWorld world = client.world;

        if (world == null) {
            result.addProperty("error", "Not in a world");
            return result;
        }

        int minX = Math.min(x1, x2);
        int maxX = Math.max(x1, x2);
        int minZ = Math.min(z1, z2);
        int maxZ = Math.max(z1, z2);

        int sizeX = maxX - minX + 1;
        int sizeZ = maxZ - minZ + 1;

        if (sizeX * sizeZ > 256 * 256) {
            result.addProperty("error", "Area too large: " + (sizeX * sizeZ) + " columns (max 65536)");
            return result;
        }

        JsonArray heights = new JsonArray();
        JsonArray surfaceBlocks = new JsonArray();
        BlockPos.Mutable pos = new BlockPos.Mutable();

        int minHeight = Integer.MAX_VALUE;
        int maxHeight = Integer.MIN_VALUE;

        for (int z = minZ; z <= maxZ; z++) {
            JsonArray row = new JsonArray();
            JsonArray surfaceRow = new JsonArray();

            for (int x = minX; x <= maxX; x++) {
                // Find the highest non-air block
                int height = world.getBottomY();
                String surfaceBlock = "minecraft:air";

                for (int y = VersionCompat.getTopYInclusive(world); y >= world.getBottomY(); y--) {
                    pos.set(x, y, z);
                    BlockState state = world.getBlockState(pos);
                    if (!state.isAir()) {
                        height = y;
                        surfaceBlock = Registries.BLOCK.getId(state.getBlock()).toString();
                        break;
                    }
                }

                row.add(height);
                surfaceRow.add(surfaceBlock);

                if (height > maxHeight) maxHeight = height;
                if (height < minHeight) minHeight = height;
            }

            heights.add(row);
            surfaceBlocks.add(surfaceRow);
        }

        JsonArray origin = new JsonArray();
        origin.add(minX);
        origin.add(minZ);
        result.add("origin", origin);

        JsonArray dimensions = new JsonArray();
        dimensions.add(sizeX);
        dimensions.add(sizeZ);
        result.add("dimensions", dimensions);

        result.add("heights", heights);
        result.add("surface_blocks", surfaceBlocks);

        JsonObject stats = new JsonObject();
        stats.addProperty("min_height", minHeight);
        stats.addProperty("max_height", maxHeight);
        stats.addProperty("height_range", maxHeight - minHeight);
        result.add("stats", stats);

        LOGGER.info("Heightmap: {}x{}, heights {} to {}", sizeX, sizeZ, minHeight, maxHeight);

        return result;
    }
}
