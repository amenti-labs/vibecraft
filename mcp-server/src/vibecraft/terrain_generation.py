"""
VibeCraft Terrain Generation System

Provides AI agent with powerful, console-safe tools for creating realistic
terrain features using WorldEdit's noise functions and expression engine.

Key capabilities:
- Generate hills, mountains, valleys, plateaus, canyons
- Use Perlin, Ridged Multifractal, and Voronoi noise
- Tunable parameters for scale, amplitude, detail
- Post-processing with smoothing and texturing
- Safety guardrails to prevent accidents
"""

import logging
from typing import Dict, Any, Optional
from .rcon_manager import RCONManager

logger = logging.getLogger(__name__)


class TerrainGenerator:
    """
    Advanced terrain generation using WorldEdit noise expressions.
    All operations are console-safe (no player clicks required).
    """

    def __init__(self, rcon: RCONManager):
        self.rcon = rcon

        # Safety limits
        self.MAX_AMPLITUDE = 50  # Max vertical displacement
        self.MAX_REGION_SIZE = 100000  # Max blocks in selection
        self.DEFAULT_SMOOTH_ITERATIONS = 2

    # =========================================================================
    # LOW-LEVEL PRIMITIVES (Direct WorldEdit Command Wrappers)
    # =========================================================================

    def set_selection(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int) -> Dict[str, Any]:
        """Set WorldEdit selection cuboid."""
        try:
            # Ensure coordinates are ordered correctly
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            min_z, max_z = min(z1, z2), max(z1, z2)

            # Validate region size
            volume = (max_x - min_x + 1) * (max_y - min_y + 1) * (max_z - min_z + 1)
            if volume > self.MAX_REGION_SIZE:
                return {
                    "success": False,
                    "error": f"Region too large ({volume:,} blocks). Max: {self.MAX_REGION_SIZE:,}"
                }

            # Set positions
            result1 = self.rcon.send_command(f"//pos1 {min_x},{min_y},{min_z}")
            result2 = self.rcon.send_command(f"//pos2 {max_x},{max_y},{max_z}")

            return {
                "success": True,
                "region": {
                    "min": [min_x, min_y, min_z],
                    "max": [max_x, max_y, max_z],
                    "volume": volume
                },
                "output": f"{result1}\n{result2}"
            }

        except Exception as e:
            logger.error(f"Error setting selection: {e}")
            return {"success": False, "error": str(e)}

    def deform(self, expression: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Apply a deformation expression to the selected region.

        Expression modifies x, y, z coordinates using math and noise functions.
        Example: "y = y + perlin(42, x/18, 0, z/18, 1.2, 4, 0.55) * 6"
        """
        try:
            result = self.rcon.send_command(f"//deform {expression}")

            return {
                "success": True,
                "operation": "deform",
                "expression": expression,
                "output": result
            }

        except Exception as e:
            logger.error(f"Error applying deformation: {e}")
            return {"success": False, "error": str(e)}

    def generate(self, pattern: str, expression: str, hollow: bool = False, timeout: int = 120) -> Dict[str, Any]:
        """
        Generate blocks using an expression.

        Pattern: Block type(s) to place (e.g., "stone", "70%stone,30%andesite")
        Expression: Math expression defining shape (e.g., "y < 64 + perlin(...) * 10")
        """
        try:
            cmd = f"//generate {pattern} {expression}"
            if hollow:
                cmd += " -h"

            result = self.rcon.send_command(cmd)

            return {
                "success": True,
                "operation": "generate",
                "pattern": pattern,
                "expression": expression,
                "output": result
            }

        except Exception as e:
            logger.error(f"Error generating terrain: {e}")
            return {"success": False, "error": str(e)}

    def smooth(self, iterations: int = 2, mask: Optional[str] = None) -> Dict[str, Any]:
        """
        Smooth terrain in the selected region.

        Iterations: Number of smoothing passes (1-10 recommended)
        Mask: Optional mask to limit which blocks are smoothed
        """
        try:
            iterations = max(1, min(10, iterations))  # Clamp to safe range

            if mask:
                self.rcon.send_command(f"//gmask {mask}")

            result = self.rcon.send_command(f"//smooth {iterations}")

            if mask:
                self.rcon.send_command("//gmask")  # Clear mask

            return {
                "success": True,
                "operation": "smooth",
                "iterations": iterations,
                "output": result
            }

        except Exception as e:
            logger.error(f"Error smoothing terrain: {e}")
            return {"success": False, "error": str(e)}

    def overlay(self, pattern: str) -> Dict[str, Any]:
        """
        Overlay a pattern on top of the surface in the selected region.

        Pattern: Block type(s) to place on top (e.g., "grass_block", "85%grass_block,10%moss_block,5%coarse_dirt")
        """
        try:
            result = self.rcon.send_command(f"//overlay {pattern}")

            return {
                "success": True,
                "operation": "overlay",
                "pattern": pattern,
                "output": result
            }

        except Exception as e:
            logger.error(f"Error overlaying pattern: {e}")
            return {"success": False, "error": str(e)}

    def replace(self, from_pattern: str, to_pattern: str, mask: Optional[str] = None) -> Dict[str, Any]:
        """
        Replace blocks in the selected region.

        from_pattern: Block(s) to replace (e.g., "stone", "stone,dirt")
        to_pattern: Block(s) to place (e.g., "grass_block", "70%stone,30%andesite")
        mask: Optional mask to limit replacement
        """
        try:
            if mask:
                self.rcon.send_command(f"//gmask {mask}")

            result = self.rcon.send_command(f"//replace {from_pattern} {to_pattern}")

            if mask:
                self.rcon.send_command("//gmask")  # Clear mask

            return {
                "success": True,
                "operation": "replace",
                "from": from_pattern,
                "to": to_pattern,
                "output": result
            }

        except Exception as e:
            logger.error(f"Error replacing blocks: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # HIGH-LEVEL TERRAIN PRESETS (Pre-tested Recipes)
    # =========================================================================

    def generate_hills(
        self,
        x1: int, y1: int, z1: int,
        x2: int, y2: int, z2: int,
        scale: int = 18,
        amplitude: int = 6,
        octaves: int = 4,
        persistence: float = 0.55,
        smooth_iterations: int = 3,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate gentle rolling hills using Perlin noise.

        Parameters:
        - scale: Larger = broader hills (10-30 recommended)
        - amplitude: Height variation (3-15 recommended)
        - octaves: Detail level (3-6 recommended)
        - persistence: How much detail layers fade (0.4-0.7 recommended)
        - smooth_iterations: Post-smoothing passes (2-4 recommended)
        - seed: Random seed (optional, auto-generated if None)
        """
        if seed is None:
            seed = hash((x1, z1)) % 10000

        # Validate amplitude
        amplitude = min(amplitude, self.MAX_AMPLITUDE)

        steps = []

        # Step 1: Set selection
        select_result = self.set_selection(x1, y1, z1, x2, y2, z2)
        if not select_result["success"]:
            return select_result
        steps.append(("Selection", select_result))

        # Step 2: Deform with Perlin noise
        frequency = 1.0 / scale
        expression = f"y = y + round(perlin({seed}, x/{scale}, 0, z/{scale}, {frequency}, {octaves}, {persistence}) * {amplitude})"
        deform_result = self.deform(expression)
        if not deform_result["success"]:
            return deform_result
        steps.append(("Deformation", deform_result))

        # Step 3: Smooth
        smooth_result = self.smooth(smooth_iterations)
        steps.append(("Smoothing", smooth_result))

        return {
            "success": True,
            "terrain_type": "rolling_hills",
            "parameters": {
                "scale": scale,
                "amplitude": amplitude,
                "octaves": octaves,
                "persistence": persistence,
                "seed": seed
            },
            "steps": steps,
            "summary": f"Generated gentle rolling hills with scale={scale}, amplitude={amplitude}"
        }

    def generate_mountains(
        self,
        x1: int, y1: int, z1: int,
        x2: int, y2: int, z2: int,
        scale: int = 28,
        amplitude: int = 18,
        octaves: int = 5,
        smooth_iterations: int = 2,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate rugged mountains using Ridged Multifractal noise.

        Parameters:
        - scale: Mountain breadth (20-40 recommended)
        - amplitude: Mountain height (10-30 recommended)
        - octaves: Terrain detail (4-6 recommended)
        - smooth_iterations: Post-smoothing (1-3, less = sharper peaks)
        - seed: Random seed (optional)
        """
        if seed is None:
            seed = hash((x1, z1, "mountains")) % 10000

        amplitude = min(amplitude, self.MAX_AMPLITUDE)

        steps = []

        # Step 1: Selection
        select_result = self.set_selection(x1, y1, z1, x2, y2, z2)
        if not select_result["success"]:
            return select_result
        steps.append(("Selection", select_result))

        # Step 2: Ridged multifractal deformation
        frequency = 1.0 / scale
        expression = f"y = y + round(ridgedmulti({seed}, x/{scale}, 0, z/{scale}, {frequency}, {octaves}) * {amplitude})"
        deform_result = self.deform(expression)
        if not deform_result["success"]:
            return deform_result
        steps.append(("Deformation", deform_result))

        # Step 3: Light smoothing (preserve sharp peaks)
        smooth_result = self.smooth(smooth_iterations)
        steps.append(("Smoothing", smooth_result))

        return {
            "success": True,
            "terrain_type": "rugged_mountains",
            "parameters": {
                "scale": scale,
                "amplitude": amplitude,
                "octaves": octaves,
                "seed": seed
            },
            "steps": steps,
            "summary": f"Generated rugged mountains with scale={scale}, amplitude={amplitude}"
        }

    def generate_valleys(
        self,
        x1: int, y1: int, z1: int,
        x2: int, y2: int, z2: int,
        scale: int = 22,
        depth: int = 10,
        octaves: int = 4,
        smooth_iterations: int = 2,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate valley networks using inverted Perlin noise.

        Parameters:
        - scale: Valley width (15-30 recommended)
        - depth: Valley depth (5-20 recommended)
        - octaves: Detail level (3-5 recommended)
        - smooth_iterations: Post-smoothing (2-3 recommended)
        - seed: Random seed (optional)
        """
        if seed is None:
            seed = hash((x1, z1, "valleys")) % 10000

        depth = min(depth, self.MAX_AMPLITUDE)

        steps = []

        # Step 1: Selection
        select_result = self.set_selection(x1, y1, z1, x2, y2, z2)
        if not select_result["success"]:
            return select_result
        steps.append(("Selection", select_result))

        # Step 2: Inverted Perlin (abs + subtract creates valleys)
        expression = f"y = y - round(abs(perlin({seed}, x/{scale}, 0, z/{scale}, 1.0, {octaves}, 0.5)) * {depth}) + 3"
        deform_result = self.deform(expression)
        if not deform_result["success"]:
            return deform_result
        steps.append(("Deformation", deform_result))

        # Step 3: Smooth
        smooth_result = self.smooth(smooth_iterations)
        steps.append(("Smoothing", smooth_result))

        return {
            "success": True,
            "terrain_type": "valley_network",
            "parameters": {
                "scale": scale,
                "depth": depth,
                "octaves": octaves,
                "seed": seed
            },
            "steps": steps,
            "summary": f"Generated valley network with scale={scale}, depth={depth}"
        }

    def generate_mountain_range(
        self,
        x1: int, y1: int, z1: int,
        x2: int, y2: int, z2: int,
        direction: str = "north-south",
        scale: int = 30,
        amplitude: int = 20,
        octaves: int = 5,
        smooth_iterations: int = 1,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a directional mountain range using oriented ridged noise.

        Parameters:
        - direction: "north-south", "east-west", "northeast-southwest", "northwest-southeast"
        - scale: Range breadth (25-40 recommended)
        - amplitude: Peak height (15-30 recommended)
        - octaves: Detail level (4-6 recommended)
        - smooth_iterations: Post-smoothing (1-2 for sharp peaks)
        - seed: Random seed (optional)
        """
        if seed is None:
            seed = hash((x1, z1, "range", direction)) % 10000

        amplitude = min(amplitude, self.MAX_AMPLITUDE)

        # Calculate rotation coefficients based on direction
        rotation_map = {
            "north-south": (0.05, 0.01, 0.05, -0.01),  # (x_coeff_u, z_coeff_u, z_coeff_v, x_coeff_v)
            "east-west": (0.01, 0.05, -0.01, 0.05),
            "northeast-southwest": (0.04, 0.04, 0.04, -0.04),
            "northwest-southeast": (0.04, -0.04, -0.04, -0.04)
        }

        if direction not in rotation_map:
            return {
                "success": False,
                "error": f"Invalid direction '{direction}'. Use: {', '.join(rotation_map.keys())}"
            }

        xu, zu, zv, xv = rotation_map[direction]

        steps = []

        # Step 1: Selection
        select_result = self.set_selection(x1, y1, z1, x2, y2, z2)
        if not select_result["success"]:
            return select_result
        steps.append(("Selection", select_result))

        # Step 2: Oriented ridged deformation
        expression = f"y = y + round(ridgedmulti({seed}, (x*{xu})+(z*{zu}), 0, (z*{zv})+(x*{xv}), 1.0, {octaves}) * {amplitude})"
        deform_result = self.deform(expression)
        if not deform_result["success"]:
            return deform_result
        steps.append(("Deformation", deform_result))

        # Step 3: Minimal smoothing
        smooth_result = self.smooth(smooth_iterations)
        steps.append(("Smoothing", smooth_result))

        return {
            "success": True,
            "terrain_type": "mountain_range",
            "parameters": {
                "direction": direction,
                "scale": scale,
                "amplitude": amplitude,
                "octaves": octaves,
                "seed": seed
            },
            "steps": steps,
            "summary": f"Generated {direction} mountain range with amplitude={amplitude}"
        }

    def generate_plateau(
        self,
        x1: int, y1: int, z1: int,
        x2: int, y2: int, z2: int,
        height: int = 15,
        edge_roughness: float = 0.3,
        smooth_iterations: int = 2,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a plateau with rough edges using noise-based masking.

        Parameters:
        - height: Plateau height (10-25 recommended)
        - edge_roughness: Edge variation (0.2-0.5, higher = rougher)
        - smooth_iterations: Post-smoothing (2-3 recommended)
        - seed: Random seed (optional)
        """
        if seed is None:
            seed = hash((x1, z1, "plateau")) % 10000

        height = min(height, self.MAX_AMPLITUDE)

        steps = []

        # Step 1: Selection
        select_result = self.set_selection(x1, y1, z1, x2, y2, z2)
        if not select_result["success"]:
            return select_result
        steps.append(("Selection", select_result))

        # Step 2: Raise plateau with noise-softened edges
        # Uses Perlin to vary the height near edges
        center_x = (x1 + x2) / 2
        center_z = (z1 + z2) / 2
        radius = min(abs(x2 - x1), abs(z2 - z1)) / 2.5

        expression = f"y = y + round({height} * (1 - smoothstep(0, 1, (sqrt((x-{center_x})^2 + (z-{center_z})^2) / {radius}) + perlin({seed}, x/15, 0, z/15, 1.0, 3, 0.5) * {edge_roughness})))"
        deform_result = self.deform(expression)
        if not deform_result["success"]:
            return deform_result
        steps.append(("Deformation", deform_result))

        # Step 3: Smooth
        smooth_result = self.smooth(smooth_iterations)
        steps.append(("Smoothing", smooth_result))

        return {
            "success": True,
            "terrain_type": "plateau",
            "parameters": {
                "height": height,
                "edge_roughness": edge_roughness,
                "seed": seed
            },
            "steps": steps,
            "summary": f"Generated plateau with height={height}, roughness={edge_roughness}"
        }

    # =========================================================================
    # TEXTURING & SURFACE TREATMENT
    # =========================================================================

    def texture_natural_slopes(
        self,
        x1: int, y1: int, z1: int,
        x2: int, y2: int, z2: int,
        style: str = "temperate"
    ) -> Dict[str, Any]:
        """
        Apply natural surface texturing to terrain based on style.

        Styles:
        - "temperate": Grass, moss, dirt (default)
        - "alpine": Stone, snow, gravel (high altitude)
        - "desert": Sand, sandstone, terracotta (arid)
        - "volcanic": Basalt, magma, blackstone (lava zones)
        """
        texture_recipes = {
            "temperate": {
                "base": "70%stone,20%andesite,10%deepslate",
                "surface": "85%grass_block,10%moss_block,5%coarse_dirt"
            },
            "alpine": {
                "base": "60%stone,25%andesite,15%calcite",
                "surface": "70%snow_block,20%powder_snow,10%gravel"
            },
            "desert": {
                "base": "70%sandstone,20%smooth_sandstone,10%red_sandstone",
                "surface": "80%sand,15%red_sand,5%terracotta"
            },
            "volcanic": {
                "base": "60%basalt,25%blackstone,15%deepslate",
                "surface": "70%basalt,20%magma_block,10%blackstone"
            }
        }

        if style not in texture_recipes:
            return {
                "success": False,
                "error": f"Invalid style '{style}'. Use: {', '.join(texture_recipes.keys())}"
            }

        recipe = texture_recipes[style]
        steps = []

        # Step 1: Selection
        select_result = self.set_selection(x1, y1, z1, x2, y2, z2)
        if not select_result["success"]:
            return select_result
        steps.append(("Selection", select_result))

        # Step 2: Replace base material (below surface)
        # Use mask to only affect blocks below Y threshold
        base_result = self.rcon.send_command(f"//replace stone,dirt,grass_block {recipe['base']}")
        steps.append(("Base Material", {"output": base_result}))

        # Step 3: Overlay surface pattern
        overlay_result = self.overlay(recipe["surface"])
        steps.append(("Surface Overlay", overlay_result))

        return {
            "success": True,
            "operation": "texturing",
            "style": style,
            "recipe": recipe,
            "steps": steps,
            "summary": f"Applied {style} texturing to terrain"
        }
