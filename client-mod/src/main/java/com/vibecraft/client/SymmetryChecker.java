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
 * Checks structural symmetry across an axis using client-side block data.
 * Efficient implementation that reads directly from client chunk cache.
 */
public final class SymmetryChecker {
    private static final Logger LOGGER = LoggerFactory.getLogger("vibecraft-symmetry");
    private static final int MAX_BLOCKS = 128 * 128 * 128;
    private static final int MAX_DIFFERENCES_STORED = 100;

    private SymmetryChecker() {}

    /**
     * Check symmetry of a region across an axis.
     *
     * @param x1, y1, z1 First corner
     * @param x2, y2, z2 Second corner
     * @param axis "x", "y", or "z" - axis of symmetry
     * @param tolerance Number of blocks difference allowed (0 = perfect symmetry)
     * @param resolution Sample every N blocks for large regions
     */
    public static JsonObject checkSymmetry(
            int x1, int y1, int z1,
            int x2, int y2, int z2,
            String axis, int tolerance, int resolution
    ) {
        JsonObject result = new JsonObject();

        MinecraftClient client = MinecraftClient.getInstance();
        ClientWorld world = client.world;

        if (world == null) {
            result.addProperty("error", "Not in a world");
            return result;
        }

        // Normalize axis
        axis = axis.toLowerCase();
        if (!axis.equals("x") && !axis.equals("y") && !axis.equals("z")) {
            result.addProperty("error", "Invalid axis: " + axis + ". Use 'x', 'y', or 'z'.");
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

        // Apply resolution
        if (resolution < 1) resolution = 1;
        if (resolution > 4) resolution = 4;

        int effectiveVolume = ((sizeX + resolution - 1) / resolution) *
                              ((sizeY + resolution - 1) / resolution) *
                              ((sizeZ + resolution - 1) / resolution);

        if (effectiveVolume > MAX_BLOCKS) {
            result.addProperty("error", "Region too large: " + effectiveVolume +
                " blocks (max " + MAX_BLOCKS + "). Try higher resolution.");
            return result;
        }

        // Calculate center plane
        double centerPlane;
        switch (axis) {
            case "x" -> centerPlane = (minX + maxX) / 2.0;
            case "y" -> centerPlane = (minY + maxY) / 2.0;
            case "z" -> centerPlane = (minZ + maxZ) / 2.0;
            default -> centerPlane = 0;
        }

        // Compare blocks across the axis
        List<JsonObject> differences = new ArrayList<>();
        int totalBlocksChecked = 0;
        int symmetricBlocks = 0;
        int asymmetricBlocks = 0;

        BlockPos.Mutable pos1 = new BlockPos.Mutable();
        BlockPos.Mutable pos2 = new BlockPos.Mutable();

        // Iterate through half the region and compare with mirror
        for (int y = minY; y <= maxY; y += resolution) {
            for (int z = minZ; z <= maxZ; z += resolution) {
                for (int x = minX; x <= maxX; x += resolution) {
                    // Calculate mirrored position
                    int mx, my, mz;
                    switch (axis) {
                        case "x" -> {
                            // Only check one half
                            if (x > centerPlane) continue;
                            mx = (int) (2 * centerPlane - x);
                            my = y;
                            mz = z;
                        }
                        case "y" -> {
                            if (y > centerPlane) continue;
                            mx = x;
                            my = (int) (2 * centerPlane - y);
                            mz = z;
                        }
                        case "z" -> {
                            if (z > centerPlane) continue;
                            mx = x;
                            my = y;
                            mz = (int) (2 * centerPlane - z);
                        }
                        default -> {
                            mx = x; my = y; mz = z;
                        }
                    }

                    // Skip if mirror is outside bounds
                    if (mx < minX || mx > maxX || my < minY || my > maxY || mz < minZ || mz > maxZ) {
                        continue;
                    }

                    // Get both block states
                    pos1.set(x, y, z);
                    pos2.set(mx, my, mz);

                    BlockState state1 = world.getBlockState(pos1);
                    BlockState state2 = world.getBlockState(pos2);

                    totalBlocksChecked++;

                    String block1 = Registries.BLOCK.getId(state1.getBlock()).toString();
                    String block2 = Registries.BLOCK.getId(state2.getBlock()).toString();

                    // Check for match (comparing block type, not states like facing)
                    boolean isMatch = block1.equals(block2);

                    // For stairs/slabs, also check if they're mirrored properly
                    // (this is a simplification - full state comparison would be more complex)
                    if (isMatch && (block1.contains("stairs") || block1.contains("slab"))) {
                        // Simple check - states should be different if properly mirrored
                        // For now, count as match if same block type
                    }

                    if (isMatch) {
                        symmetricBlocks++;
                    } else {
                        asymmetricBlocks++;

                        // Store difference details (up to limit)
                        if (differences.size() < MAX_DIFFERENCES_STORED) {
                            JsonObject diff = new JsonObject();

                            JsonArray position1 = new JsonArray();
                            position1.add(x);
                            position1.add(y);
                            position1.add(z);
                            diff.add("position1", position1);

                            JsonArray position2 = new JsonArray();
                            position2.add(mx);
                            position2.add(my);
                            position2.add(mz);
                            diff.add("position2", position2);

                            diff.addProperty("block1", block1);
                            diff.addProperty("block2", block2);

                            // Generate recommendation
                            String recommendation;
                            if (state1.isAir() && !state2.isAir()) {
                                recommendation = "Add " + block2.replace("minecraft:", "") +
                                    " at (" + x + "," + y + "," + z + ")";
                            } else if (!state1.isAir() && state2.isAir()) {
                                recommendation = "Add " + block1.replace("minecraft:", "") +
                                    " at (" + mx + "," + my + "," + mz + ")";
                            } else {
                                recommendation = "Replace one side to match";
                            }
                            diff.addProperty("recommendation", recommendation);

                            differences.add(diff);
                        }
                    }
                }
            }
        }

        // Calculate symmetry score
        double symmetryScore = totalBlocksChecked > 0
            ? Math.round((double) symmetricBlocks / totalBlocksChecked * 1000) / 10.0
            : 100.0;

        // Determine verdict based on tolerance
        String verdict;
        if (asymmetricBlocks <= tolerance) {
            if (asymmetricBlocks == 0) {
                verdict = "PERFECT";
            } else {
                verdict = "PASS (within tolerance)";
            }
        } else if (symmetryScore >= 95) {
            verdict = "GOOD (minor asymmetries)";
        } else if (symmetryScore >= 80) {
            verdict = "FAIR (noticeable asymmetries)";
        } else {
            verdict = "POOR (significant asymmetries)";
        }

        // Build result
        result.addProperty("axis", axis);
        result.addProperty("center_plane", centerPlane);
        result.addProperty("symmetry_score", symmetryScore);
        result.addProperty("verdict", verdict);
        result.addProperty("total_blocks_checked", totalBlocksChecked);
        result.addProperty("symmetric_blocks", symmetricBlocks);
        result.addProperty("asymmetric_blocks", asymmetricBlocks);
        result.addProperty("tolerance", tolerance);
        result.addProperty("total_differences", asymmetricBlocks);

        // Add differences array
        JsonArray diffsArray = new JsonArray();
        for (JsonObject diff : differences) {
            diffsArray.add(diff);
        }
        result.add("differences", diffsArray);

        // Summary
        String summary;
        if (asymmetricBlocks == 0) {
            summary = "Perfect " + axis.toUpperCase() + "-axis symmetry! All " +
                totalBlocksChecked + " block pairs match.";
        } else if (asymmetricBlocks <= tolerance) {
            summary = "Symmetry within tolerance. " + asymmetricBlocks +
                " differences found (tolerance: " + tolerance + ").";
        } else {
            summary = "Found " + asymmetricBlocks + " asymmetric blocks out of " +
                totalBlocksChecked + " checked. See differences for details.";
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

        LOGGER.info("Symmetry check ({}): {}% symmetric, {} differences",
            axis, symmetryScore, asymmetricBlocks);

        return result;
    }
}
