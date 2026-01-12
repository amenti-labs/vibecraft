"""
Geometric Algorithms for VibeCraft

Mathematical algorithms for generating perfect circles, spheres, domes, and arches.
Uses Bresenham's algorithms for pixel-perfect results.
"""

import math
from typing import List, Tuple, Dict, Any


class CircleCalculator:
    """
    Generate circles, ellipses, spheres, domes, and arches using mathematical algorithms.
    All calculations use Bresenham's algorithms for pixel-perfect results.
    """

    @staticmethod
    def calculate_circle(
        radius: int, filled: bool = False, center: Tuple[int, int] = (0, 0)
    ) -> Dict[str, Any]:
        """
        Calculate a 2D circle using Bresenham's circle algorithm.

        Args:
            radius: Circle radius in blocks
            filled: If True, returns all interior points; if False, only perimeter
            center: Center coordinates (x, z)

        Returns:
            Dictionary with coordinates, block count, and WorldEdit commands
        """
        cx, cz = center
        coordinates = set()

        if filled:
            # Filled circle: use all points within radius
            for x in range(-radius, radius + 1):
                for z in range(-radius, radius + 1):
                    if x * x + z * z <= radius * radius:
                        coordinates.add((cx + x, cz + z))
        else:
            # Hollow circle: Bresenham's algorithm
            x = 0
            z = radius
            d = 3 - 2 * radius

            def add_circle_points(cx, cz, x, z):
                """Add 8-way symmetric points"""
                points = [
                    (cx + x, cz + z),
                    (cx - x, cz + z),
                    (cx + x, cz - z),
                    (cx - x, cz - z),
                    (cx + z, cz + x),
                    (cx - z, cz + x),
                    (cx + z, cz - x),
                    (cx - z, cz - x),
                ]
                return points

            while x <= z:
                coordinates.update(add_circle_points(cx, cz, x, z))
                if d < 0:
                    d = d + 4 * x + 6
                else:
                    d = d + 4 * (x - z) + 10
                    z -= 1
                x += 1

        coords_list = sorted(list(coordinates))

        # Generate ASCII preview
        ascii_preview = CircleCalculator._generate_ascii_preview(coords_list, radius, center)

        return {
            "shape": "circle",
            "center": list(center),
            "radius": radius,
            "filled": filled,
            "blocks_count": len(coords_list),
            "coordinates": coords_list,
            "ascii_preview": ascii_preview,
            "usage_tip": f"Use these coordinates to place blocks in a perfect circle (radius {radius})",
        }

    @staticmethod
    def calculate_sphere(
        radius: int, hollow: bool = True, center: Tuple[int, int, int] = (0, 0, 0)
    ) -> Dict[str, Any]:
        """
        Calculate a 3D sphere.

        Args:
            radius: Sphere radius in blocks
            hollow: If True, only outer shell; if False, filled solid
            center: Center coordinates (x, y, z)

        Returns:
            Dictionary with 3D coordinates, block count, and WorldEdit commands
        """
        cx, cy, cz = center
        coordinates = set()

        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                for z in range(-radius, radius + 1):
                    distance_sq = x * x + y * y + z * z

                    if hollow:
                        # Only outer shell (distance very close to radius)
                        if abs(math.sqrt(distance_sq) - radius) < 0.7:
                            coordinates.add((cx + x, cy + y, cz + z))
                    else:
                        # Filled sphere
                        if distance_sq <= radius * radius:
                            coordinates.add((cx + x, cy + y, cz + z))

        coords_list = sorted(list(coordinates))

        return {
            "shape": "sphere",
            "center": list(center),
            "radius": radius,
            "hollow": hollow,
            "blocks_count": len(coords_list),
            "coordinates": coords_list,
            "worldedit_command": f"//sphere {'h' if hollow else ''} <block> {radius}",
            "usage_tip": "Teleport to center then use WorldEdit or place blocks at coordinates",
        }

    @staticmethod
    def calculate_dome(
        radius: int, style: str = "hemisphere", center: Tuple[int, int, int] = (0, 0, 0)
    ) -> Dict[str, Any]:
        """
        Calculate a dome (half-sphere or partial sphere).

        Args:
            radius: Dome radius in blocks
            style: "hemisphere" (half), "three_quarter" (3/4 sphere), "low" (1/4 sphere)
            center: Center coordinates (x, y, z)

        Returns:
            Dictionary with 3D coordinates for dome structure
        """
        cx, cy, cz = center
        coordinates = set()

        # Determine Y cutoff based on style
        if style == "hemisphere":
            y_min = 0
        elif style == "three_quarter":
            y_min = -radius // 2
        elif style == "low":
            y_min = radius // 2
        else:
            y_min = 0  # Default to hemisphere

        for x in range(-radius, radius + 1):
            for y in range(y_min, radius + 1):
                for z in range(-radius, radius + 1):
                    distance_sq = x * x + y * y + z * z

                    # Only outer shell
                    if abs(math.sqrt(distance_sq) - radius) < 0.7:
                        coordinates.add((cx + x, cy + y, cz + z))

        coords_list = sorted(list(coordinates))

        return {
            "shape": "dome",
            "style": style,
            "center": list(center),
            "radius": radius,
            "blocks_count": len(coords_list),
            "coordinates": coords_list,
            "usage_tip": f"Perfect for {style} dome structures (cathedrals, temples, rotundas)",
        }

    @staticmethod
    def calculate_ellipse(
        width: int, height: int, filled: bool = False, center: Tuple[int, int] = (0, 0)
    ) -> Dict[str, Any]:
        """
        Calculate a 2D ellipse.

        Args:
            width: Width (X axis diameter)
            height: Height (Z axis diameter)
            filled: If True, returns all interior points
            center: Center coordinates (x, z)

        Returns:
            Dictionary with coordinates and metadata
        """
        cx, cz = center
        a = width // 2  # Semi-major axis
        b = height // 2  # Semi-minor axis
        coordinates = set()

        if filled:
            # Filled ellipse
            for x in range(-a, a + 1):
                for z in range(-b, b + 1):
                    if (x * x) / (a * a) + (z * z) / (b * b) <= 1:
                        coordinates.add((cx + x, cz + z))
        else:
            # Hollow ellipse (perimeter only)
            for angle in range(0, 360, 1):
                rad = math.radians(angle)
                x = int(a * math.cos(rad))
                z = int(b * math.sin(rad))
                coordinates.add((cx + x, cz + z))

        coords_list = sorted(list(coordinates))

        return {
            "shape": "ellipse",
            "center": list(center),
            "width": width,
            "height": height,
            "filled": filled,
            "blocks_count": len(coords_list),
            "coordinates": coords_list,
            "usage_tip": f"Ellipse {width}×{height} - useful for oval rooms, ponds, decorative features",
        }

    @staticmethod
    def calculate_arch(
        width: int, height: int, depth: int = 1, center: Tuple[int, int, int] = (0, 0, 0)
    ) -> Dict[str, Any]:
        """
        Calculate an arch shape (semi-circular or pointed).

        Args:
            width: Arch width in blocks
            height: Arch height in blocks
            depth: Arch depth (thickness)
            center: Center bottom coordinates (x, y, z)

        Returns:
            Dictionary with 3D coordinates for arch structure
        """
        cx, cy, cz = center
        coordinates = set()

        # Use semi-circle formula for the arch curve
        radius = width // 2

        for x in range(-radius, radius + 1):
            # Calculate Y height at this X position (semi-circle)
            y_offset = int(math.sqrt(radius * radius - x * x))

            # Limit to specified height
            if y_offset > height:
                y_offset = height

            # Add blocks for arch thickness (depth)
            for d in range(depth):
                for y in range(y_offset):
                    # Only add blocks on the perimeter (hollow arch)
                    if abs(x) >= radius - 1 or y == y_offset - 1:
                        coordinates.add((cx + x, cy + y, cz + d))

        coords_list = sorted(list(coordinates))

        return {
            "shape": "arch",
            "center": list(center),
            "width": width,
            "height": height,
            "depth": depth,
            "blocks_count": len(coords_list),
            "coordinates": coords_list,
            "usage_tip": f"Arch {width}×{height} - perfect for doorways, bridges, windows",
        }

    @staticmethod
    def _generate_ascii_preview(
        coordinates: List[Tuple[int, int]], radius: int, center: Tuple[int, int]
    ) -> str:
        """Generate ASCII art preview of 2D shape"""
        if not coordinates:
            return ""

        # Create grid
        size = radius * 2 + 3
        grid = [[" " for _ in range(size)] for _ in range(size)]

        cx, cz = center
        offset_x = radius + 1 - cx
        offset_z = radius + 1 - cz

        for x, z in coordinates:
            grid_x = x + offset_x
            grid_z = z + offset_z
            if 0 <= grid_x < size and 0 <= grid_z < size:
                grid[grid_z][grid_x] = "█"

        # Add center marker
        center_x = cx + offset_x
        center_z = cz + offset_z
        if 0 <= center_x < size and 0 <= center_z < size:
            grid[center_z][center_x] = "+"

        return "\n".join(["".join(row) for row in grid])
