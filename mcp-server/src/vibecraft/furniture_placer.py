"""
Furniture Placement Helper

Converts furniture layout definitions into executable WorldEdit commands.
Handles coordinate transformation, rotation, and command generation.
"""

from collections import OrderedDict
from typing import Dict, List, Tuple, Optional


class FurniturePlacer:
    """
    Helper class to place furniture layouts in the Minecraft world.

    Handles:
    - Coordinate transformation (relative to absolute)
    - Rotation (facing direction conversion)
    - WorldEdit command generation
    """

    # Rotation mappings for cardinal directions
    ROTATIONS = {
        "north": 0,   # -Z direction (default)
        "east": 90,   # +X direction
        "south": 180, # +Z direction
        "west": 270,  # -X direction
    }

    # Inverse rotation mapping
    ROTATION_TO_DIRECTION = {
        0: "north",
        90: "east",
        180: "south",
        270: "west",
    }

    @staticmethod
    def rotate_coordinates(x: int, y: int, z: int, rotation: int, bounds: Dict) -> Tuple[int, int, int]:
        """
        Rotate coordinates around the origin based on rotation angle.

        Args:
            x, y, z: Relative coordinates
            rotation: Rotation angle (0, 90, 180, 270)
            bounds: Furniture bounds (width, height, depth)

        Returns:
            Rotated (x, y, z) coordinates
        """
        width = bounds['width']
        depth = bounds['depth']

        if rotation == 0:
            # North (no rotation)
            return x, y, z
        elif rotation == 90:
            # East (90° clockwise)
            # X becomes -Z, Z becomes X
            return depth - 1 - z, y, x
        elif rotation == 180:
            # South (180°)
            # X becomes -X, Z becomes -Z
            return width - 1 - x, y, depth - 1 - z
        elif rotation == 270:
            # West (270° clockwise = 90° counter-clockwise)
            # X becomes Z, Z becomes -X
            return z, y, width - 1 - x
        else:
            raise ValueError(f"Invalid rotation angle: {rotation}. Must be 0, 90, 180, or 270.")

    @staticmethod
    def rotate_block_state(state: str, rotation: int) -> str:
        """
        Rotate block state properties based on rotation angle.

        Handles facing, axis, and other directional properties.

        Args:
            state: Block state string (e.g., "[facing=north,half=bottom]")
            rotation: Rotation angle (0, 90, 180, 270)

        Returns:
            Rotated block state string
        """
        if not state or rotation == 0:
            return state

        # Parse state properties
        import re
        properties: OrderedDict[str, str] = OrderedDict()
        order: List[str] = []
        if state:
            # Extract properties from [key=value,key2=value2] format
            state_content = state.strip('[]')
            if state_content:
                for prop in state_content.split(','):
                    if '=' in prop:
                        key, value = prop.split('=', 1)
                        key = key.strip()
                        properties[key] = value.strip()
                        order.append(key)

        def rotate_facing(value: str) -> str:
            facing_rotation = {
                'north': ['north', 'east', 'south', 'west'],
                'east': ['east', 'south', 'west', 'north'],
                'south': ['south', 'west', 'north', 'east'],
                'west': ['west', 'north', 'east', 'south'],
                'up': ['up', 'up', 'up', 'up'],
                'down': ['down', 'down', 'down', 'down'],
            }
            steps = (rotation // 90) % 4
            rotated = facing_rotation.get(value)
            return rotated[steps] if rotated else value

        # Rotate facing direction
        if 'facing' in properties:
            properties['facing'] = rotate_facing(properties['facing'])

        # Rotate axis (for logs, pillars, etc.)
        if 'axis' in properties:
            axis = properties['axis']
            if rotation in [90, 270]:
                # Swap X and Z axes
                axis_rotation = {'x': 'z', 'y': 'y', 'z': 'x'}
                properties['axis'] = axis_rotation.get(axis, axis)

        # Rotate rails and similar directional shapes
        if 'shape' in properties:
            shape = properties['shape']
            properties['shape'] = FurniturePlacer._rotate_shape_property(shape, rotation)

        # Rotate sign and item frame rotation values (0-15 compass increments)
        if 'rotation' in properties:
            try:
                current = int(re.sub(r'[^0-9]', '', properties['rotation']))
                offset = (rotation // 90) * 4
                properties['rotation'] = str((current + offset) % 16)
            except ValueError:
                pass

        # Button/lever facing uses "face" or "lever_direction"
        if 'face' in properties and properties['face'] in {'floor', 'ceiling'}:
            # Floor/ceiling don't rotate around horizontal axes
            pass
        if 'lever_direction' in properties:
            properties['lever_direction'] = FurniturePlacer._rotate_lever_direction(
                properties['lever_direction'], rotation
            )

        if 'hinge' in properties:
            # Door hinge is relative to facing; rotation keeps left/right
            properties['hinge'] = properties['hinge']

        # Rebuild state string
        if properties:
            props_str = ','.join(f"{key}={properties[key]}" for key in order if key in properties)
            return f"[{props_str}]"
        return ""

    @staticmethod
    def _rotate_shape_property(shape: str, rotation: int) -> str:
        """Rotate directional shape values (rails, corners, etc.)."""
        if rotation % 360 == 0:
            return shape

        steps = (rotation // 90) % 4
        if steps == 0:
            return shape

        rot90 = {
            'north_south': 'east_west',
            'east_west': 'north_south',
            'ascending_north': 'ascending_east',
            'ascending_east': 'ascending_south',
            'ascending_south': 'ascending_west',
            'ascending_west': 'ascending_north',
            'north_east': 'south_east',
            'south_east': 'south_west',
            'south_west': 'north_west',
            'north_west': 'north_east',
        }

        rotated = shape
        for _ in range(steps):
            rotated = rot90.get(rotated, rotated)
        return rotated

    @staticmethod
    def _rotate_lever_direction(direction: str, rotation: int) -> str:
        if rotation % 360 == 0:
            return direction

        steps = (rotation // 90) % 4
        sequence = ['north', 'east', 'south', 'west']
        if direction in sequence:
            idx = sequence.index(direction)
            return sequence[(idx + steps) % 4]
        return direction

    @staticmethod
    def get_placement_commands(
        layout: Dict,
        origin_x: int,
        origin_y: int,
        origin_z: int,
        facing: Optional[str] = None,
        place_on_surface: bool = True
    ) -> List[str]:
        """
        Generate WorldEdit commands to place furniture at specified location.

        Args:
            layout: Furniture layout dictionary
            origin_x, origin_y, origin_z: World coordinates for furniture origin
            facing: Override facing direction (north/south/east/west), or None to use layout default
            place_on_surface: If True (default), origin_y is treated as the floor level and furniture
                            is placed ON TOP (origin_y + 1). If False, furniture is placed exactly
                            at origin_y (advanced use - may replace floor blocks).

        Returns:
            List of WorldEdit command strings ready for execution
        """
        commands = []

        # Determine rotation
        layout_facing = layout.get('origin', {}).get('facing', 'north')
        target_facing = facing or layout_facing

        # Calculate rotation angle
        layout_rotation = FurniturePlacer.ROTATIONS.get(layout_facing, 0)
        target_rotation = FurniturePlacer.ROTATIONS.get(target_facing, 0)
        rotation = (target_rotation - layout_rotation) % 360

        # Auto-adjust Y coordinate if placing on surface
        # This prevents furniture from replacing floor blocks
        if place_on_surface:
            origin_y = origin_y + 1
            placement_note = f"on surface at Y={origin_y-1}"
        else:
            placement_note = f"at exact Y={origin_y}"

        bounds = layout['bounds']
        placements = layout.get('placements', [])

        # Add header comment
        commands.append(f"# Placing {layout['name']} {placement_note}, facing {target_facing}")

        # Process each placement
        for placement in placements:
            ptype = placement.get('type')

            if ptype == 'block':
                # Single block placement
                pos = placement['pos']
                x, y, z = pos['x'], pos['y'], pos['z']

                # Rotate coordinates if needed
                if rotation != 0:
                    x, y, z = FurniturePlacer.rotate_coordinates(x, y, z, rotation, bounds)

                # Calculate absolute coordinates
                abs_x = origin_x + x
                abs_y = origin_y + y
                abs_z = origin_z + z

                block = placement['block']
                state = placement.get('state', '')

                # Rotate block state if needed
                if rotation != 0 and state:
                    state = FurniturePlacer.rotate_block_state(state, rotation)

                # Generate setblock command
                block_spec = f"{block}{state}" if state else block
                cmd = f"setblock {abs_x} {abs_y} {abs_z} {block_spec}"

                # Add NBT data if present
                if 'nbt' in placement:
                    cmd += f" {placement['nbt']}"

                commands.append(cmd)

            elif ptype == 'fill':
                # Fill region
                from_pos = placement['from']
                to_pos = placement['to']

                # Rotate both positions
                from_x, from_y, from_z = from_pos['x'], from_pos['y'], from_pos['z']
                to_x, to_y, to_z = to_pos['x'], to_pos['y'], to_pos['z']

                if rotation != 0:
                    from_x, from_y, from_z = FurniturePlacer.rotate_coordinates(from_x, from_y, from_z, rotation, bounds)
                    to_x, to_y, to_z = FurniturePlacer.rotate_coordinates(to_x, to_y, to_z, rotation, bounds)

                # Calculate absolute coordinates
                abs_from_x = origin_x + from_x
                abs_from_y = origin_y + from_y
                abs_from_z = origin_z + from_z
                abs_to_x = origin_x + to_x
                abs_to_y = origin_y + to_y
                abs_to_z = origin_z + to_z

                block = placement['block']
                state = placement.get('state', '')

                if rotation != 0 and state:
                    state = FurniturePlacer.rotate_block_state(state, rotation)

                block_spec = f"{block}{state}" if state else block
                cmd = f"fill {abs_from_x} {abs_from_y} {abs_from_z} {abs_to_x} {abs_to_y} {abs_to_z} {block_spec}"
                commands.append(cmd)

            elif ptype == 'line':
                # Line placement (using WorldEdit //line command)
                from_pos = placement['from']
                to_pos = placement['to']

                from_x, from_y, from_z = from_pos['x'], from_pos['y'], from_pos['z']
                to_x, to_y, to_z = to_pos['x'], to_pos['y'], to_pos['z']

                if rotation != 0:
                    from_x, from_y, from_z = FurniturePlacer.rotate_coordinates(from_x, from_y, from_z, rotation, bounds)
                    to_x, to_y, to_z = FurniturePlacer.rotate_coordinates(to_x, to_y, to_z, rotation, bounds)

                abs_from_x = origin_x + from_x
                abs_from_y = origin_y + from_y
                abs_from_z = origin_z + from_z
                abs_to_x = origin_x + to_x
                abs_to_y = origin_y + to_y
                abs_to_z = origin_z + to_z

                block = placement['block']
                state = placement.get('state', '')

                if rotation != 0 and state:
                    state = FurniturePlacer.rotate_block_state(state, rotation)

                block_spec = f"{block}{state}" if state else block

                # Use WorldEdit line command
                commands.append(f"//pos1 {abs_from_x},{abs_from_y},{abs_from_z}")
                commands.append(f"//pos2 {abs_to_x},{abs_to_y},{abs_to_z}")
                commands.append(f"//line {block_spec}")

            elif ptype == 'layer':
                # Layer placement
                y = placement['y']
                pattern = placement['pattern']
                layer_bounds = placement.get('bounds')

                # Default to full furniture bounds if not specified
                if not layer_bounds:
                    layer_from = {'x': 0, 'z': 0}
                    layer_to = {'x': bounds['width'] - 1, 'z': bounds['depth'] - 1}
                else:
                    layer_from = layer_bounds['from']
                    layer_to = layer_bounds['to']

                # Rotate layer bounds
                from_x, from_z = layer_from['x'], layer_from['z']
                to_x, to_z = layer_to['x'], layer_to['z']

                if rotation != 0:
                    from_x, from_y_temp, from_z = FurniturePlacer.rotate_coordinates(from_x, 0, from_z, rotation, bounds)
                    to_x, to_y_temp, to_z = FurniturePlacer.rotate_coordinates(to_x, 0, to_z, rotation, bounds)

                # Calculate absolute coordinates
                abs_from_x = origin_x + from_x
                abs_from_z = origin_z + from_z
                abs_to_x = origin_x + to_x
                abs_to_z = origin_z + to_z
                abs_y = origin_y + y

                # Use WorldEdit fill for layer
                commands.append(f"//pos1 {abs_from_x},{abs_y},{abs_from_z}")
                commands.append(f"//pos2 {abs_to_x},{abs_y},{abs_to_z}")
                commands.append(f"//set {pattern}")

        return commands

    @staticmethod
    def get_command_summary(commands: List[str]) -> str:
        """
        Generate a human-readable summary of placement commands.

        Args:
            commands: List of WorldEdit commands

        Returns:
            Formatted summary string
        """
        # Count command types
        setblock_count = sum(1 for cmd in commands if cmd.startswith('setblock'))
        fill_count = sum(1 for cmd in commands if cmd.startswith('fill'))
        worldedit_count = sum(1 for cmd in commands if cmd.startswith('//'))

        summary = "**Placement Summary:**\n"
        summary += f"- Total commands: {len([c for c in commands if not c.startswith('#')])}\n"
        if setblock_count:
            summary += f"- Single blocks: {setblock_count}\n"
        if fill_count:
            summary += f"- Fill regions: {fill_count}\n"
        if worldedit_count:
            summary += f"- WorldEdit commands: {worldedit_count}\n"

        return summary
