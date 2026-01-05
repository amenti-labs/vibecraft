"""Pattern placement helpers for building templates."""

from typing import Dict, List, Optional

from .furniture_placer import FurniturePlacer


class PatternPlacer:
    """Convert structured building pattern layouts into executable commands."""

    SKIP_CHARS = {" ", ".", "_"}

    @staticmethod
    def get_placement_commands(
        pattern: Dict,
        origin_x: int,
        origin_y: int,
        origin_z: int,
        facing: Optional[str] = None,
    ) -> List[str]:
        commands: List[str] = []

        palette = pattern.get("palette", {})
        bounds = pattern.get("bounds") or pattern.get("dimensions")
        if not bounds:
            raise ValueError("Pattern is missing 'bounds' or 'dimensions' definition")

        width = bounds.get("width")
        depth = bounds.get("depth")
        if width is None or depth is None:
            raise ValueError("Pattern bounds must include 'width' and 'depth'")

        origin = pattern.get("origin", {})
        pattern_facing = origin.get("facing", "north")
        target_facing = facing or pattern_facing

        layout_rotation = FurniturePlacer.ROTATIONS.get(pattern_facing, 0)
        target_rotation = FurniturePlacer.ROTATIONS.get(target_facing, 0)
        rotation = (target_rotation - layout_rotation) % 360

        commands.append(
            f"# Placing pattern {pattern.get('name', pattern.get('id', 'unknown'))} at ({origin_x},{origin_y},{origin_z}) facing {target_facing}"
        )

        for layer in pattern.get("layers", []):
            y = layer.get("y")
            rows = layer.get("rows", [])
            if y is None:
                raise ValueError(f"Layer in pattern {pattern.get('id')} is missing 'y'")

            if len(rows) != depth:
                raise ValueError(
                    f"Pattern {pattern.get('id')} layer at y={y} expected {depth} rows, found {len(rows)}"
                )

            for local_z, row in enumerate(rows):
                if len(row) != width:
                    raise ValueError(
                        f"Pattern {pattern.get('id')} layer y={y} expected row length {width}, got {len(row)}"
                    )

                for local_x, symbol in enumerate(row):
                    if symbol in PatternPlacer.SKIP_CHARS:
                        continue

                    block_spec = palette.get(symbol)
                    if not block_spec:
                        raise ValueError(
                            f"Pattern {pattern.get('id')} uses undefined palette symbol '{symbol}'"
                        )

                    x, y_rot, z = local_x, y, local_z
                    if rotation:
                        x, y_rot, z = FurniturePlacer.rotate_coordinates(
                            x,
                            y,
                            z,
                            rotation,
                            {
                                "width": width,
                                "height": bounds.get("height", y + 1),
                                "depth": depth,
                            },
                        )

                    abs_x = origin_x + x
                    abs_y = origin_y + y_rot
                    abs_z = origin_z + z

                    commands.append(f"setblock {abs_x} {abs_y} {abs_z} {block_spec}")

        return commands

    @staticmethod
    def get_command_summary(commands: List[str]) -> str:
        return FurniturePlacer.get_command_summary(commands)
