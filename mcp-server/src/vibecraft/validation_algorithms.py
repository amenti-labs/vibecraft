"""
Validation Algorithms for VibeCraft

Algorithms for analyzing structure symmetry, lighting levels, and structural integrity.
Provides QA validation tools for professional-quality builds.
"""

import logging
from typing import List, Tuple, Dict, Any, Optional

from .block_utils import fetch_block_state, block_is_air

logger = logging.getLogger(__name__)


class SymmetryChecker:
    """
    Analyze structure symmetry across different axes.
    Detects asymmetries and provides correction recommendations.
    """

    def __init__(self, rcon_manager):
        """
        Initialize the symmetry checker.

        Args:
            rcon_manager: RCONManager instance for querying world blocks
        """
        self.rcon = rcon_manager

    def check_symmetry(
        self,
        x1: int,
        y1: int,
        z1: int,
        x2: int,
        y2: int,
        z2: int,
        axis: str = "x",
        tolerance: int = 0,
        resolution: int = 1,
    ) -> Dict[str, Any]:
        """
        Check symmetry of a structure across a specified axis.

        Args:
            x1, y1, z1: First corner of region
            x2, y2, z2: Second corner of region
            axis: Axis to check ("x", "z", "y", "diagonal")
            tolerance: Number of allowed asymmetric blocks (0 = perfect symmetry required)
            resolution: Sampling resolution (1 = every block, 2 = every other block)

        Returns:
            Dictionary with symmetry score, asymmetric blocks, and recommendations
        """
        # Normalize coordinates
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        min_z, max_z = min(z1, z2), max(z1, z2)

        logger.info(
            f"Checking symmetry on {axis} axis for region ({min_x},{min_y},{min_z}) to ({max_x},{max_y},{max_z})"
        )

        # Calculate center plane based on axis
        if axis == "x":
            center = (min_x + max_x) // 2
        elif axis == "z":
            center = (min_z + max_z) // 2
        elif axis == "y":
            center = (min_y + max_y) // 2
        else:
            return {"error": f"Invalid axis '{axis}'. Must be 'x', 'y', or 'z'."}

        # Sample blocks in region
        differences = []
        total_checked = 0

        for x in range(min_x, max_x + 1, resolution):
            for y in range(min_y, max_y + 1, resolution):
                for z in range(min_z, max_z + 1, resolution):
                    # Get mirror position based on axis
                    if axis == "x":
                        mirror_x = 2 * center - x
                        mirror_y, mirror_z = y, z
                        # Skip if mirror position is out of bounds or same as original
                        if mirror_x < min_x or mirror_x > max_x or mirror_x == x:
                            continue
                    elif axis == "z":
                        mirror_x, mirror_y = x, y
                        mirror_z = 2 * center - z
                        if mirror_z < min_z or mirror_z > max_z or mirror_z == z:
                            continue
                    elif axis == "y":
                        mirror_x, mirror_z = x, z
                        mirror_y = 2 * center - y
                        if mirror_y < min_y or mirror_y > max_y or mirror_y == y:
                            continue

                    # Get blocks at both positions
                    block1 = fetch_block_state(self.rcon, x, y, z)
                    block2 = fetch_block_state(self.rcon, mirror_x, mirror_y, mirror_z)

                    if block_is_air(block1) and block_is_air(block2):
                        continue

                    total_checked += 1

                    # Compare blocks
                    key1 = block1.get("key") if block1 else None
                    key2 = block2.get("key") if block2 else None

                    if key1 != key2:
                        display_block1 = key1 or "air"
                        display_block2 = key2 or "air"
                        differences.append(
                            {
                                "position1": [x, y, z],
                                "block1": display_block1,
                                "position2": [mirror_x, mirror_y, mirror_z],
                                "block2": display_block2,
                                "recommendation": f"Replace {display_block2} at ({mirror_x},{mirror_y},{mirror_z}) with {display_block1} for symmetry",
                            }
                        )

        # Calculate symmetry score
        symmetric_count = total_checked - len(differences)
        symmetry_score = (symmetric_count / total_checked * 100) if total_checked > 0 else 0

        # Determine verdict
        if len(differences) <= tolerance:
            verdict = "SYMMETRIC"
        elif symmetry_score >= 90:
            verdict = "MOSTLY_SYMMETRIC"
        elif symmetry_score >= 70:
            verdict = "PARTIALLY_SYMMETRIC"
        else:
            verdict = "ASYMMETRIC"

        logger.info(
            f"Symmetry check complete: {symmetry_score:.1f}% symmetric ({len(differences)} differences)"
        )

        return {
            "symmetry_score": round(symmetry_score, 2),
            "axis": axis,
            "center_plane": center,
            "total_blocks_checked": total_checked,
            "symmetric_blocks": symmetric_count,
            "asymmetric_blocks": len(differences),
            "tolerance": tolerance,
            "verdict": verdict,
            "differences": differences[:50],  # Limit to first 50 differences
            "total_differences": len(differences),
            "summary": self._generate_symmetry_summary(
                symmetry_score, verdict, len(differences), axis
            ),
        }

    def _generate_symmetry_summary(
        self, score: float, verdict: str, diff_count: int, axis: str
    ) -> str:
        """Generate natural language summary of symmetry check."""
        if verdict == "SYMMETRIC":
            return f"Structure is perfectly symmetric across {axis} axis (within tolerance)"
        elif verdict == "MOSTLY_SYMMETRIC":
            return (
                f"Structure is mostly symmetric ({score:.1f}%) with {diff_count} minor differences"
            )
        elif verdict == "PARTIALLY_SYMMETRIC":
            return f"Structure has significant asymmetries ({score:.1f}%) - {diff_count} differences found"
        else:
            return f"Structure is highly asymmetric ({score:.1f}%) - major reconstruction needed"


class LightingAnalyzer:
    """
    Analyze lighting levels in a region and suggest optimal light source placement.
    Identifies dark spots where mobs can spawn (light level < 8).
    """

    LIGHT_SOURCE_ALWAYS = {
        "torch",
        "wall_torch",
        "soul_torch",
        "soul_wall_torch",
        "lantern",
        "soul_lantern",
        "redstone_torch",
        "redstone_wall_torch",
        "glowstone",
        "sea_lantern",
        "shroomlight",
        "jack_o_lantern",
        "end_rod",
        "amethyst_cluster",
        "ochre_froglight",
        "pearlescent_froglight",
        "verdant_froglight",
        "beacon",
        "sea_pickle",
    }

    LIGHT_SOURCE_REQUIRES_LIT = {
        "campfire",
        "soul_campfire",
        "redstone_lamp",
        "furnace",
        "blast_furnace",
        "smoker",
        "candle",
        "candle_cake",
        "white_candle",
        "orange_candle",
        "magenta_candle",
        "light_blue_candle",
        "yellow_candle",
        "lime_candle",
        "pink_candle",
        "gray_candle",
        "light_gray_candle",
        "cyan_candle",
        "purple_candle",
        "blue_candle",
        "brown_candle",
        "green_candle",
        "red_candle",
        "black_candle",
    }

    TRANSPARENT_BLOCKS = {
        "air",
        "glass",
        "glass_pane",
        "white_stained_glass",
        "light_gray_stained_glass",
        "gray_stained_glass",
        "black_stained_glass",
        "red_stained_glass",
        "blue_stained_glass",
        "green_stained_glass",
        "yellow_stained_glass",
        "lime_stained_glass",
        "brown_stained_glass",
        "cyan_stained_glass",
        "purple_stained_glass",
        "pink_stained_glass",
        "orange_stained_glass",
        "magenta_stained_glass",
        "light_blue_stained_glass",
        "iron_bars",
        "chain",
        "vine",
        "ladder",
        "scaffolding",
    }

    LIGHT_OFFSETS = [
        (dx, dy, dz)
        for dx in range(-4, 5)
        for dy in range(-2, 3)
        for dz in range(-4, 5)
        if abs(dx) + abs(dy) + abs(dz) <= 4
    ]

    SKY_CHECK_MAX = 40
    MAX_WORLD_HEIGHT = 319

    def __init__(self, rcon_manager):
        """
        Initialize the lighting analyzer.

        Args:
            rcon_manager: RCONManager instance for querying world data
        """
        self.rcon = rcon_manager

    def analyze_lighting(
        self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, resolution: int = 2
    ) -> Dict[str, Any]:
        """
        Analyze lighting in a region.

        Args:
            x1, y1, z1: First corner of region
            x2, y2, z2: Second corner of region
            resolution: Sampling resolution (1 = every block, 2 = every other)

        Returns:
            Dictionary with light analysis and placement recommendations
        """
        # Normalize coordinates
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        min_z, max_z = min(z1, z2), max(z1, z2)

        logger.info(
            f"Analyzing lighting for region ({min_x},{min_y},{min_z}) to ({max_x},{max_y},{max_z})"
        )

        # Sample light levels
        light_samples = []
        dark_spots = []
        block_cache = {}  # Cache for block queries to improve performance

        for x in range(min_x, max_x + 1, resolution):
            for y in range(min_y, max_y + 1, resolution):
                for z in range(min_z, max_z + 1, resolution):
                    light_level = self._get_light_level(x, y, z, block_cache)

                    if light_level is not None:
                        light_samples.append({"position": [x, y, z], "light_level": light_level})

                        # Dark spot detection (< 8 allows mob spawning)
                        if light_level < 8:
                            dark_spots.append({"position": [x, y, z], "light_level": light_level})

        if not light_samples:
            return {"error": "No light data collected from region"}

        # Calculate statistics
        light_levels = [s["light_level"] for s in light_samples]
        avg_light = sum(light_levels) / len(light_levels)

        well_lit = sum(1 for l in light_levels if l >= 12)
        dim = sum(1 for l in light_levels if 8 <= l < 12)
        dark = sum(1 for l in light_levels if l < 8)

        # Determine mob spawn risk
        dark_percentage = (dark / len(light_levels)) * 100
        if dark_percentage > 30:
            mob_risk = "HIGH"
        elif dark_percentage > 10:
            mob_risk = "MEDIUM"
        else:
            mob_risk = "LOW"

        # Calculate optimal light placements
        optimal_placements = self._calculate_light_placements(dark_spots, resolution, block_cache)

        logger.info(
            f"Lighting analysis complete: {len(light_samples)} samples, {len(dark_spots)} dark spots"
        )

        return {
            "region": {"min": [min_x, min_y, min_z], "max": [max_x, max_y, max_z]},
            "average_light_level": round(avg_light, 2),
            "total_samples": len(light_samples),
            "dark_spots_count": len(dark_spots),
            "mob_spawn_risk": mob_risk,
            "light_distribution": {
                "well_lit": well_lit,
                "dim": dim,
                "dark": dark,
                "well_lit_percentage": round(well_lit / len(light_levels) * 100, 1),
                "dim_percentage": round(dim / len(light_levels) * 100, 1),
                "dark_percentage": round(dark / len(light_levels) * 100, 1),
            },
            "dark_spots": dark_spots[:20],  # First 20 dark spots
            "optimal_placements": optimal_placements,
            "summary": self._generate_lighting_summary(avg_light, mob_risk, len(dark_spots)),
        }

    def _get_light_level(
        self, x: int, y: int, z: int, cache: Dict[Tuple[int, int, int], Optional[Dict[str, Any]]]
    ) -> Optional[int]:
        block = self._get_cached_block(x, y, z, cache)

        if block is None:
            return None

        if self._is_light_source(block):
            return 15

        if self._is_open_to_sky(x, y, z, cache):
            return 15

        nearest = self._nearest_light_source(x, y, z, cache)
        if nearest is not None:
            light_level = max(1, 15 - nearest)
        else:
            light_level = 8 if block.get("id") == "air" else 5

        return max(0, min(15, light_level))

    def _get_cached_block(
        self, x: int, y: int, z: int, cache: Dict[Tuple[int, int, int], Optional[Dict[str, Any]]]
    ) -> Optional[Dict[str, Any]]:
        key = (x, y, z)
        if key not in cache:
            cache[key] = fetch_block_state(self.rcon, x, y, z)
        return cache[key]

    def _is_light_source(self, block: Optional[Dict[str, Any]]) -> bool:
        if not block:
            return False

        block_id = block.get("id")
        if block_id in self.LIGHT_SOURCE_ALWAYS:
            return True

        if block_id in self.LIGHT_SOURCE_REQUIRES_LIT:
            lit = block.get("properties", {}).get("lit", "false")
            if lit.lower() == "true":
                return True

        if block_id == "sea_pickle":
            count = block.get("properties", {}).get("pickles", "1")
            return count not in {"0", "1"}

        return False

    def _nearest_light_source(
        self, x: int, y: int, z: int, cache: Dict[Tuple[int, int, int], Optional[Dict[str, Any]]]
    ) -> Optional[int]:
        nearest: Optional[int] = None

        for dx, dy, dz in self.LIGHT_OFFSETS:
            block = self._get_cached_block(x + dx, y + dy, z + dz, cache)
            if self._is_light_source(block):
                distance = abs(dx) + abs(dy) + abs(dz)
                if nearest is None or distance < nearest:
                    nearest = distance
                    if nearest == 0:
                        break

        return nearest

    def _is_open_to_sky(
        self, x: int, y: int, z: int, cache: Dict[Tuple[int, int, int], Optional[Dict[str, Any]]]
    ) -> bool:
        check_y = y + 1
        steps = 0

        while steps < self.SKY_CHECK_MAX and check_y <= self.MAX_WORLD_HEIGHT:
            block = self._get_cached_block(x, check_y, z, cache)
            if block and block.get("id") not in self.TRANSPARENT_BLOCKS:
                return False
            check_y += 1
            steps += 1

        return check_y > self.MAX_WORLD_HEIGHT or steps >= self.SKY_CHECK_MAX

    def _calculate_light_placements(
        self,
        dark_spots: List[Dict],
        resolution: int,
        cache: Dict[Tuple[int, int, int], Optional[Dict[str, Any]]],
    ) -> List[Dict]:
        """Calculate optimal positions for light sources based on dark spots."""
        if not dark_spots:
            return []

        # Group dark spots into clusters
        # Place one light source per cluster (roughly every 10-12 blocks)
        placements = []
        used_positions = set()

        for spot in dark_spots:
            pos = tuple(spot["position"])

            # Check if we already have a light source nearby
            nearby = False
            for used_pos in used_positions:
                distance = sum((a - b) ** 2 for a, b in zip(pos, used_pos)) ** 0.5
                if distance < 10:  # Within 10 blocks
                    nearby = True
                    break

            if not nearby:
                x, y, z = spot["position"]
                open_sky = self._is_open_to_sky(x, y, z, cache)
                block_here = self._get_cached_block(x, y, z, cache)
                suggested = (
                    "lantern"
                    if open_sky or (block_here and block_here.get("id") not in {"air", "water"})
                    else "torch"
                )

                placements.append(
                    {
                        "position": spot["position"],
                        "current_light": spot["light_level"],
                        "suggested_source": suggested,
                        "reason": f"Dark spot (light={spot['light_level']}) - needs illumination",
                    }
                )
                used_positions.add(pos)

                # Limit to reasonable number of suggestions
                if len(placements) >= 30:
                    break

        return placements

    def _generate_lighting_summary(self, avg_light: float, mob_risk: str, dark_count: int) -> str:
        """Generate natural language summary of lighting analysis."""
        if mob_risk == "HIGH":
            return f"Poor lighting ({avg_light:.1f} avg) - {dark_count} dark spots with HIGH mob spawn risk"
        elif mob_risk == "MEDIUM":
            return f"Adequate lighting ({avg_light:.1f} avg) - {dark_count} dark spots with MEDIUM spawn risk"
        else:
            return (
                f"Good lighting ({avg_light:.1f} avg) - {dark_count} dark spots with LOW spawn risk"
            )


class StructureValidator:
    """
    Validate structural integrity of builds.
    Detects floating blocks, unsupported regions, and physics violations.
    """

    # Blocks affected by gravity
    GRAVITY_BLOCKS = {
        "sand",
        "red_sand",
        "gravel",
        "concrete_powder",
        "white_concrete_powder",
        "orange_concrete_powder",
        "magenta_concrete_powder",
        "light_blue_concrete_powder",
        "yellow_concrete_powder",
        "lime_concrete_powder",
        "pink_concrete_powder",
        "gray_concrete_powder",
        "light_gray_concrete_powder",
        "cyan_concrete_powder",
        "purple_concrete_powder",
        "blue_concrete_powder",
        "brown_concrete_powder",
        "green_concrete_powder",
        "red_concrete_powder",
        "black_concrete_powder",
        "anvil",
        "chipped_anvil",
        "damaged_anvil",
        "dragon_egg",
        "scaffolding",
    }

    # Blocks that provide support
    SUPPORT_BLOCKS = {
        "stone",
        "dirt",
        "grass_block",
        "cobblestone",
        "planks",
        "log",
        "wood",
        "stone_bricks",
        "bricks",
        "obsidian",
        "bedrock",
        "concrete",
        "terracotta",
        "wool",
        "glass",
        "iron_block",
        "gold_block",
        "diamond_block",
        "emerald_block",
        # Add more solid blocks as needed
    }

    def __init__(self, rcon_manager):
        """
        Initialize the structure validator.

        Args:
            rcon_manager: RCONManager instance for querying world blocks
        """
        self.rcon = rcon_manager

    def validate_structure(
        self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, resolution: int = 1
    ) -> Dict[str, Any]:
        """
        Validate structural integrity of a build.

        Args:
            x1, y1, z1: First corner of region
            x2, y2, z2: Second corner of region
            resolution: Sampling resolution

        Returns:
            Dictionary with validation results and issues found
        """
        # Normalize coordinates
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        min_z, max_z = min(z1, z2), max(z1, z2)

        logger.info(
            f"Validating structure integrity for ({min_x},{min_y},{min_z}) to ({max_x},{max_y},{max_z})"
        )

        floating_blocks = []
        gravity_violations = []
        total_blocks = 0

        for x in range(min_x, max_x + 1, resolution):
            for y in range(min_y, max_y + 1, resolution):
                for z in range(min_z, max_z + 1, resolution):
                    block = fetch_block_state(self.rcon, x, y, z)

                    if block_is_air(block):
                        continue

                    total_blocks += 1

                    # Check if block is affected by gravity
                    if block and block["id"] in self.GRAVITY_BLOCKS:
                        # Check if there's support below
                        block_below = fetch_block_state(self.rcon, x, y - 1, z)

                        if block_is_air(block_below):
                            gravity_violations.append(
                                {
                                    "position": [x, y, z],
                                    "block": block.get("key"),
                                    "issue": f"No support below (air at Y={y-1})",
                                    "severity": "HIGH",
                                    "recommendation": "Add support column or replace with non-gravity block",
                                }
                            )

                    # Check for floating non-supported blocks (simple heuristic)
                    # A block is "floating" if it has no solid neighbors (simplified check)
                    if y > min_y:  # Skip bottom layer
                        neighbors = [
                            fetch_block_state(self.rcon, x, y - 1, z),  # Below
                            fetch_block_state(self.rcon, x + 1, y, z),  # Adjacent blocks
                            fetch_block_state(self.rcon, x - 1, y, z),
                            fetch_block_state(self.rcon, x, y, z + 1),
                            fetch_block_state(self.rcon, x, y, z - 1),
                        ]

                        solid_neighbors = sum(1 for n in neighbors if not block_is_air(n))

                        # If no solid neighbors at all, likely floating
                        if solid_neighbors == 0:
                            floating_blocks.append(
                                {
                                    "position": [x, y, z],
                                    "block": block.get("key"),
                                    "issue": "No adjacent solid blocks detected",
                                    "severity": "MEDIUM",
                                    "recommendation": "Connect to main structure or add supports",
                                }
                            )

        # Combine all issues
        all_issues = gravity_violations + floating_blocks
        structure_valid = len(all_issues) == 0

        logger.info(
            f"Validation complete: {total_blocks} blocks checked, {len(all_issues)} issues found"
        )

        return {
            "structure_valid": structure_valid,
            "total_blocks_checked": total_blocks,
            "issues_found": len(all_issues),
            "gravity_violations": gravity_violations,
            "floating_blocks": floating_blocks[:20],  # First 20
            "total_floating": len(floating_blocks),
            "summary": self._generate_validation_summary(structure_valid, len(all_issues)),
        }

    def _generate_validation_summary(self, valid: bool, issue_count: int) -> str:
        """Generate natural language summary of validation."""
        if valid:
            return "Structure passed validation - no physics violations detected"
        elif issue_count < 5:
            return f"Structure has {issue_count} minor issues that should be fixed"
        elif issue_count < 20:
            return f"Structure has {issue_count} issues requiring attention"
        else:
            return (
                f"Structure has {issue_count} significant issues - major reconstruction recommended"
            )
