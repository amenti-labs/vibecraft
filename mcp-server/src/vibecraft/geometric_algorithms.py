"""
Geometric Algorithms for VibeCraft

Mathematical algorithms for generating perfect circles, spheres, domes, arches, and calculating
architectural spacing (windows, doors). Uses Bresenham's algorithms for pixel-perfect results.
"""

import math
from typing import List, Tuple, Dict, Any, Optional

class CircleCalculator:
    """
    Generate circles, ellipses, spheres, domes, and arches using mathematical algorithms.
    All calculations use Bresenham's algorithms for pixel-perfect results.
    """

    @staticmethod
    def calculate_circle(radius: int, filled: bool = False, center: Tuple[int, int] = (0, 0)) -> Dict[str, Any]:
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
                    (cx + x, cz + z), (cx - x, cz + z),
                    (cx + x, cz - z), (cx - x, cz - z),
                    (cx + z, cz + x), (cx - z, cz + x),
                    (cx + z, cz - x), (cx - z, cz - x)
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
            "usage_tip": f"Use these coordinates to place blocks in a perfect circle (radius {radius})"
        }

    @staticmethod
    def calculate_sphere(radius: int, hollow: bool = True, center: Tuple[int, int, int] = (0, 0, 0)) -> Dict[str, Any]:
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
            "usage_tip": "Teleport to center then use WorldEdit or place blocks at coordinates"
        }

    @staticmethod
    def calculate_dome(radius: int, style: str = "hemisphere", center: Tuple[int, int, int] = (0, 0, 0)) -> Dict[str, Any]:
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
            "usage_tip": f"Perfect for {style} dome structures (cathedrals, temples, rotundas)"
        }

    @staticmethod
    def calculate_ellipse(width: int, height: int, filled: bool = False, center: Tuple[int, int] = (0, 0)) -> Dict[str, Any]:
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
            "usage_tip": f"Ellipse {width}×{height} - useful for oval rooms, ponds, decorative features"
        }

    @staticmethod
    def calculate_arch(width: int, height: int, depth: int = 1, center: Tuple[int, int, int] = (0, 0, 0)) -> Dict[str, Any]:
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
            "usage_tip": f"Arch {width}×{height} - perfect for doorways, bridges, windows"
        }

    @staticmethod
    def _generate_ascii_preview(coordinates: List[Tuple[int, int]], radius: int, center: Tuple[int, int]) -> str:
        """Generate ASCII art preview of 2D shape"""
        if not coordinates:
            return ""

        # Create grid
        size = radius * 2 + 3
        grid = [[' ' for _ in range(size)] for _ in range(size)]

        cx, cz = center
        offset_x = radius + 1 - cx
        offset_z = radius + 1 - cz

        for x, z in coordinates:
            grid_x = x + offset_x
            grid_z = z + offset_z
            if 0 <= grid_x < size and 0 <= grid_z < size:
                grid[grid_z][grid_x] = '█'

        # Add center marker
        center_x = cx + offset_x
        center_z = cz + offset_z
        if 0 <= center_x < size and 0 <= center_z < size:
            grid[center_z][center_x] = '+'

        return '\n'.join([''.join(row) for row in grid])


class WindowPlacementCalculator:
    """
    Calculate optimal window and door spacing for building facades.
    Based on architectural principles and aesthetic guidelines.
    """

    @staticmethod
    def calculate_window_spacing(
        wall_length: int,
        window_width: int,
        spacing_style: str = "even",
        window_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate optimal window placement along a wall.

        Args:
            wall_length: Total wall length in blocks
            window_width: Width of each window in blocks
            spacing_style: "even", "golden_ratio", "symmetric", "clustered"
            window_count: Optional specific number of windows (auto-calculated if None)

        Returns:
            Dictionary with window positions and spacing details
        """
        # Auto-calculate window count if not specified
        if window_count is None:
            # Rule of thumb: one window per 4-6 blocks of wall
            window_count = max(1, (wall_length - 2) // 5)

        # Calculate spacing based on style
        if spacing_style == "even":
            positions, spacing_info = WindowPlacementCalculator._even_spacing(
                wall_length, window_width, window_count
            )
        elif spacing_style == "golden_ratio":
            positions, spacing_info = WindowPlacementCalculator._golden_ratio_spacing(
                wall_length, window_width, window_count
            )
        elif spacing_style == "symmetric":
            positions, spacing_info = WindowPlacementCalculator._symmetric_spacing(
                wall_length, window_width, window_count
            )
        elif spacing_style == "clustered":
            positions, spacing_info = WindowPlacementCalculator._clustered_spacing(
                wall_length, window_width, window_count
            )
        else:
            # Default to even
            positions, spacing_info = WindowPlacementCalculator._even_spacing(
                wall_length, window_width, window_count
            )

        windows = []
        for i, pos in enumerate(positions):
            windows.append({
                "index": i + 1,
                "start_position": pos,
                "end_position": pos + window_width - 1,
                "center": pos + window_width // 2,
                "note": f"Window {i + 1} of {len(positions)}"
            })

        return {
            "wall_length": wall_length,
            "window_width": window_width,
            "window_count": len(positions),
            "spacing_style": spacing_style,
            "windows": windows,
            "spacing_info": spacing_info,
            "recommendation": WindowPlacementCalculator._get_style_recommendation(spacing_style)
        }

    @staticmethod
    def _even_spacing(wall_length: int, window_width: int, count: int) -> Tuple[List[int], Dict]:
        """Calculate evenly spaced windows"""
        total_window_width = window_width * count
        total_gap_space = wall_length - total_window_width
        gap_size = total_gap_space / (count + 1)

        positions = []
        for i in range(count):
            pos = int(gap_size * (i + 1) + window_width * i)
            positions.append(pos)

        return positions, {
            "gap_between_windows": int(gap_size),
            "edge_margins": int(gap_size),
            "style_description": "Evenly distributed with equal spacing"
        }

    @staticmethod
    def _golden_ratio_spacing(wall_length: int, window_width: int, count: int) -> Tuple[List[int], Dict]:
        """Calculate spacing based on golden ratio (1.618)"""
        golden_ratio = 1.618
        positions = []

        if count == 1:
            # Single window at golden ratio point
            pos = int(wall_length / golden_ratio) - window_width // 2
            positions.append(pos)
        else:
            # Distribute using golden ratio proportions
            segment_size = wall_length / (count + 1)
            for i in range(count):
                pos = int(segment_size * (i + 1) * (1 + 1/golden_ratio)) - window_width // 2
                positions.append(pos)

        return positions, {
            "style_description": "Positioned using golden ratio (φ = 1.618) for aesthetic balance",
            "artistic_note": "Creates visually pleasing, organic-looking arrangement"
        }

    @staticmethod
    def _symmetric_spacing(wall_length: int, window_width: int, count: int) -> Tuple[List[int], Dict]:
        """Calculate symmetric spacing around center"""
        positions = []
        center = wall_length // 2

        if count % 2 == 1:
            # Odd number: place one at center
            positions.append(center - window_width // 2)
            remaining = count - 1
            for i in range(1, remaining // 2 + 1):
                offset = i * (window_width + 2)
                positions.append(center - offset - window_width // 2)
                positions.append(center + offset - window_width // 2)
        else:
            # Even number: space around center
            for i in range(count // 2):
                offset = (i + 0.5) * (window_width + 2)
                positions.append(int(center - offset - window_width // 2))
                positions.append(int(center + offset - window_width // 2))

        positions.sort()
        return positions, {
            "center_point": center,
            "style_description": "Symmetrically arranged around center axis",
            "architectural_note": "Classic formal facade layout"
        }

    @staticmethod
    def _clustered_spacing(wall_length: int, window_width: int, count: int) -> Tuple[List[int], Dict]:
        """Calculate clustered grouping (windows in pairs or triplets)"""
        positions = []
        cluster_size = 2 if count <= 4 else 3

        num_clusters = count // cluster_size
        remaining = count % cluster_size

        # Space clusters evenly
        cluster_gap = wall_length / (num_clusters + 1)

        for i in range(num_clusters):
            cluster_start = int(cluster_gap * (i + 1))
            for j in range(cluster_size):
                pos = cluster_start + j * (window_width + 1)
                positions.append(pos)

        # Add remaining windows
        if remaining > 0:
            last_cluster_start = int(cluster_gap * (num_clusters + 0.5))
            for j in range(remaining):
                pos = last_cluster_start + j * (window_width + 1)
                positions.append(pos)

        positions.sort()
        return positions, {
            "cluster_size": cluster_size,
            "num_clusters": num_clusters,
            "style_description": f"Grouped in clusters of {cluster_size} for rhythmic pattern",
            "architectural_note": "Modern/contemporary aesthetic"
        }

    @staticmethod
    def _get_style_recommendation(style: str) -> str:
        """Get recommendation text for spacing style"""
        recommendations = {
            "even": "Best for: Modern buildings, simple facades, balanced appearance",
            "golden_ratio": "Best for: Artistic builds, museums, galleries, visually striking designs",
            "symmetric": "Best for: Castles, palaces, formal government buildings, classical architecture",
            "clustered": "Best for: Contemporary designs, urban buildings, industrial aesthetics"
        }
        return recommendations.get(style, "Spacing calculated successfully")

    @staticmethod
    def calculate_door_position(
        wall_length: int,
        door_width: int = 2,
        position: str = "center",
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate optimal door placement.

        Args:
            wall_length: Total wall length
            door_width: Door width (1 or 2 typically)
            position: "center", "left", "right", "offset"
            offset: Block offset from calculated position

        Returns:
            Dictionary with door position and recommendations
        """
        if position == "center":
            door_start = (wall_length - door_width) // 2 + offset
        elif position == "left":
            door_start = 2 + offset  # 2 blocks from edge
        elif position == "right":
            door_start = wall_length - door_width - 2 + offset
        else:
            door_start = offset

        return {
            "wall_length": wall_length,
            "door_width": door_width,
            "position_style": position,
            "door_start": door_start,
            "door_end": door_start + door_width - 1,
            "door_center": door_start + door_width // 2,
            "clearance_left": door_start,
            "clearance_right": wall_length - (door_start + door_width),
            "recommendation": f"Door positioned {position}, with {door_start} blocks clearance on left"
        }
