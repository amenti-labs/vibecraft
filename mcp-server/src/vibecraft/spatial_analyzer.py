"""
Spatial Analysis V3 - Ultra-Fast Floor/Ceiling Detection

GOAL: Be FAST. 2-5 seconds, not 30+ seconds.

Strategy: Use minimal command execution
- Binary search for floor (~12 commands: 4 iterations × 3 commands)
- Linear scan for ceiling (~9-15 commands: stops at first solid)
- One //distr for materials (3 commands, optional)

Total: ~25-30 commands instead of 100+
Performance: 3-5 seconds typical (was 30+ seconds)
"""

import logging
import re
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class SpatialAnalyzerV2:
    """
    Ultra-fast spatial analysis.

    Performance target: <2 seconds for any detail level.
    """

    def __init__(self, rcon_manager):
        """Initialize with command executor."""
        self.rcon = rcon_manager

    def analyze_area(
        self,
        center_x: int,
        center_y: int,
        center_z: int,
        radius: int = 5,
        detail_level: str = "medium",
    ) -> Dict[str, Any]:
        """
        Fast spatial analysis.

        Args:
            center_x, center_y, center_z: Center coordinates
            radius: Scan radius (default 5)
            detail_level: "low", "medium", or "high" (all fast now!)

        Returns:
            Analysis with floor_y, ceiling_y, and recommendations.
        """
        logger.info(f"Fast spatial scan at ({center_x},{center_y},{center_z})")

        result = {
            "center": [center_x, center_y, center_z],
            "radius": radius,
            "detail_level": detail_level,
            "version": 3,
        }

        # 1. Find floor using binary search (5-6 commands)
        floor_y = self._find_floor_fast(center_x, center_y, center_z, radius)
        result["floor_y"] = floor_y

        # 2. Find ceiling using linear scan (stops at first solid)
        ceiling_y = self._find_ceiling_fast(center_x, center_y, center_z, radius)
        result["ceiling_y"] = ceiling_y

        # 3. Get materials if medium/high (1 command)
        if detail_level in ["medium", "high"]:
            materials = self._get_materials_fast(center_x, center_y, center_z, radius)
            result["material_summary"] = materials

        # 4. Generate recommendations (no commands)
        result["recommendations"] = self._generate_recommendations(floor_y, ceiling_y, center_y)

        # 5. Summary
        result["summary"] = self._generate_summary(result)

        logger.info(f"Scan complete: floor={floor_y}, ceiling={ceiling_y}")
        return result

    def _find_floor_fast(
        self, center_x: int, center_y: int, center_z: int, radius: int
    ) -> Optional[int]:
        """
        Find floor Y using binary search.

        Strategy: Check if Y level is mostly solid (>50% non-air).
        Binary search from center_y down to find highest solid layer.

        ~5-6 commands total.
        """
        # Search range: center_y down to center_y - 10
        low = center_y - 10
        high = center_y

        floor_y = None

        # Binary search for highest solid layer
        while low <= high:
            mid = (low + high) // 2

            is_solid = self._is_layer_solid(center_x, mid, center_z, radius)

            if is_solid:
                floor_y = mid  # This could be the floor
                low = mid + 1  # Look higher for a higher floor
            else:
                high = mid - 1  # Look lower

        return floor_y

    def _find_ceiling_fast(
        self, center_x: int, center_y: int, center_z: int, radius: int
    ) -> Optional[int]:
        """
        Find ceiling Y using linear scan upward.

        Note: Binary search doesn't work for ceiling because the solid
        pattern is not monotonic (air below, solid ceiling, air above).
        Linear scan finds first solid layer going up.

        ~10-15 commands (3 per layer checked, stops at first solid).
        """
        # Linear scan upward to find first solid layer
        for y in range(center_y, center_y + 11):
            if self._is_layer_solid(center_x, y, center_z, radius):
                return y

        return None  # No ceiling found in range

    def _is_layer_solid(self, center_x: int, y: int, center_z: int, radius: int) -> bool:
        """
        Check if a horizontal layer at Y is mostly solid (>50% non-air).

        Uses 3 commands: pos1, pos2, count.
        """
        try:
            # Select thin horizontal slice
            x1, z1 = center_x - radius, center_z - radius
            x2, z2 = center_x + radius, center_z + radius

            # Use single command with selection inline
            self.rcon.send_command(f"//pos1 {x1},{y},{z1}")
            self.rcon.send_command(f"//pos2 {x2},{y},{z2}")
            result = self.rcon.send_command("//count !air")

            # Parse count
            count = 0
            if result:
                match = re.search(r"(\d+)\s+block", str(result), re.IGNORECASE)
                if match:
                    count = int(match.group(1))

            # Calculate if >50% solid
            total_possible = (radius * 2 + 1) ** 2
            density = count / total_possible if total_possible > 0 else 0

            return density > 0.5

        except Exception as e:
            logger.debug(f"Layer check failed at Y={y}: {e}")
            return False

    def _get_materials_fast(
        self, center_x: int, center_y: int, center_z: int, radius: int
    ) -> Dict[str, Any]:
        """
        Get material summary with ONE //distr command.
        """
        try:
            # Select region
            self.rcon.send_command(
                f"//pos1 {center_x - radius},{center_y - radius},{center_z - radius}"
            )
            self.rcon.send_command(
                f"//pos2 {center_x + radius},{center_y + radius},{center_z + radius}"
            )

            result = self.rcon.send_command("//distr")

            # Parse distribution
            blocks = {}
            if result:
                for line in str(result).split("\n"):
                    match = re.search(r"([\d.]+)%\s+([a-z_:]+)\s+\((\d+)", line, re.IGNORECASE)
                    if match:
                        block = match.group(2)
                        count = int(match.group(3))
                        if ":" in block:
                            block = block.split(":", 1)[1]
                        if block != "air":
                            blocks[block] = count

            # Get top materials
            sorted_blocks = sorted(blocks.items(), key=lambda x: x[1], reverse=True)
            top_materials = [b for b, c in sorted_blocks[:5]]
            dominant = top_materials[0] if top_materials else "air"

            return {
                "dominant_material": dominant,
                "all_materials": top_materials,
                "material_counts": dict(sorted_blocks[:5]),
            }

        except Exception as e:
            logger.debug(f"Material scan failed: {e}")
            return {"dominant_material": "unknown", "all_materials": [], "material_counts": {}}

    def _generate_recommendations(
        self, floor_y: Optional[int], ceiling_y: Optional[int], center_y: int
    ) -> Dict[str, Any]:
        """Generate placement recommendations."""
        recs = {}
        warnings = []

        if floor_y is not None:
            recs["floor_placement_y"] = floor_y + 1  # ON TOP of floor
            recs["floor_block_y"] = floor_y
            recs["FURNITURE_Y"] = floor_y + 1
        else:
            recs["floor_placement_y"] = center_y
            warnings.append("No floor detected")

        if ceiling_y is not None:
            recs["ceiling_placement_y"] = ceiling_y
            recs["ceiling_block_y"] = ceiling_y
        else:
            recs["ceiling_placement_y"] = center_y + 4

        # Ceiling height
        if floor_y and ceiling_y:
            height = ceiling_y - floor_y - 1
            recs["ceiling_height"] = height
            if height < 3:
                warnings.append(f"Low ceiling ({height} blocks)")

        recs["clear_for_placement"] = True
        recs["warnings"] = warnings

        return recs

    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate quick summary."""
        lines = []

        floor_y = analysis.get("floor_y")
        ceiling_y = analysis.get("ceiling_y")
        recs = analysis.get("recommendations", {})

        lines.append("**Spatial Scan Results:**")

        if floor_y is not None:
            lines.append(f"- Floor at Y={floor_y}")
            lines.append(f"- Place furniture at Y={floor_y + 1} (ON floor)")
        else:
            lines.append("- No floor detected")

        if ceiling_y is not None:
            lines.append(f"- Ceiling at Y={ceiling_y}")
            if floor_y:
                height = ceiling_y - floor_y - 1
                lines.append(f"- Room height: {height} blocks")

        # Materials
        mats = analysis.get("material_summary", {})
        if mats.get("all_materials"):
            lines.append(f"- Materials: {', '.join(mats['all_materials'][:3])}")

        # Warnings
        if recs.get("warnings"):
            for w in recs["warnings"]:
                lines.append(f"- ⚠️ {w}")

        return "\n".join(lines)
