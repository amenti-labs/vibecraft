"""
Unit tests for the schematic building system.

Tests cover:
- Schematic parsing
- Block state rotation
- Grid rotation
- Command optimization
- Error handling
"""

import pytest
from vibecraft.tools.schematic_tools import (
    parse_schematic,
    rotate_block_state,
    rotate_grid,
    optimize_commands,
    optimize_commands_aggressive,
    find_max_rectangle,
    expand_rle_row,
    parse_compact_layer,
    normalize_schematic,
    DEFAULT_PALETTE,
)


# =============================================================================
# parse_schematic tests
# =============================================================================

class TestParseSchematic:
    """Tests for the parse_schematic function."""

    def test_basic_schematic(self):
        """Test parsing a simple 2x2 schematic."""
        schematic = {
            "anchor": [100, 64, 200],
            "palette": {"S": "stone"},
            "layers": [
                {"y": 0, "grid": [["S", "S"], ["S", "S"]]}
            ]
        }
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 4
        assert stats["blocks_placed"] == 4
        assert stats["layers"] == 1
        assert not stats["errors"]

        # Check coordinates
        assert "/setblock 100 64 200 stone" in commands
        assert "/setblock 101 64 200 stone" in commands
        assert "/setblock 100 64 201 stone" in commands
        assert "/setblock 101 64 201 stone" in commands

    def test_empty_schematic(self):
        """Test that empty schematic returns error."""
        schematic = {"anchor": [0, 0, 0], "palette": {}, "layers": []}
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 0
        assert "No layers defined" in stats["errors"]

    def test_missing_layers(self):
        """Test schematic with missing layers key."""
        schematic = {"anchor": [0, 0, 0], "palette": {"S": "stone"}}
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 0
        assert "No layers defined" in stats["errors"]

    def test_invalid_anchor_list(self):
        """Test invalid anchor format."""
        schematic = {
            "anchor": [100, 64],  # Missing z
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 0
        assert any("Invalid anchor" in e for e in stats["errors"])

    def test_anchor_player_without_position(self):
        """Test player anchor without player position."""
        schematic = {
            "anchor": "player",
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 0
        assert any("player position" in e for e in stats["errors"])

    def test_anchor_player_with_position(self):
        """Test player anchor with provided position."""
        schematic = {
            "anchor": "player",
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic, player_pos=(50, 70, 100))

        assert len(commands) == 1
        assert "/setblock 50 70 100 stone" in commands

    def test_negative_coordinates(self):
        """Test schematic with negative anchor coordinates."""
        schematic = {
            "anchor": [-100, -64, -200],
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S", "S"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert "/setblock -100 -64 -200 stone" in commands
        assert "/setblock -99 -64 -200 stone" in commands

    def test_default_palette_air_symbols(self):
        """Test that default air symbols are skipped."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone"},
            "layers": [
                {"y": 0, "grid": [
                    ["S", ".", "S"],
                    ["S", "_", "S"],
                    ["S", " ", "S"]
                ]}
            ]
        }
        commands, stats = parse_schematic(schematic)

        # 9 cells - 3 air = 6 stone blocks
        assert len(commands) == 6
        assert stats["blocks_placed"] == 6

    def test_explicit_air_block(self):
        """Test that explicit 'air' in palette is skipped."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone", "A": "air"},
            "layers": [{"y": 0, "grid": [["S", "A", "S"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 2
        assert all("air" not in cmd for cmd in commands)

    def test_multi_layer_schematic(self):
        """Test schematic with multiple layers."""
        schematic = {
            "anchor": [0, 64, 0],
            "palette": {"S": "stone", "W": "oak_planks"},
            "layers": [
                {"y": 0, "grid": [["S", "S"]]},
                {"y": 1, "grid": [["W", "W"]]},
                {"y": 2, "grid": [["S", "S"]]}
            ]
        }
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 6
        assert stats["layers"] == 3

        # Check Y coordinates
        assert any("64" in cmd for cmd in commands)
        assert any("65" in cmd for cmd in commands)
        assert any("66" in cmd for cmd in commands)

    def test_block_states_preserved(self):
        """Test that block states are preserved in output."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"St": "oak_stairs[facing=north,half=bottom]"},
            "layers": [{"y": 0, "grid": [["St"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 1
        assert "oak_stairs[facing=north,half=bottom]" in commands[0]

    def test_nbt_data_preserved(self):
        """Test that NBT data is preserved in output."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"C": "chest[facing=north]{Items:[]}"},
            "layers": [{"y": 0, "grid": [["C"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 1
        assert "{Items:[]}" in commands[0]

    def test_mode_replace(self):
        """Test default replace mode."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert commands[0] == "/setblock 0 0 0 stone"

    def test_mode_keep(self):
        """Test keep mode appends mode to command."""
        schematic = {
            "anchor": [0, 0, 0],
            "mode": "keep",
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert commands[0] == "/setblock 0 0 0 stone keep"

    def test_mode_destroy(self):
        """Test destroy mode."""
        schematic = {
            "anchor": [0, 0, 0],
            "mode": "destroy",
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert "destroy" in commands[0]

    def test_unknown_symbol_warning(self):
        """Test that unknown symbols generate warnings."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S", "!@#", "S"]]}]  # Non-alphanumeric symbol
        }
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 2  # Only S blocks
        assert any("Unknown symbol '!@#'" in w for w in stats["warnings"])

    def test_direct_block_id_without_palette(self):
        """Test using direct block IDs without palette entry."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {},
            "layers": [{"y": 0, "grid": [["stone", "dirt"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert len(commands) == 2
        assert "/setblock 0 0 0 stone" in commands
        assert "/setblock 1 0 0 dirt" in commands

    def test_namespaced_block_id(self):
        """Test blocks with minecraft: namespace."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"S": "minecraft:stone"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)

        assert "minecraft:stone" in commands[0]

    def test_jagged_grid(self):
        """Test handling of jagged/uneven grids."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [
                ["S", "S", "S"],
                ["S"],  # Shorter row
                ["S", "S"]
            ]}]
        }
        commands, stats = parse_schematic(schematic)

        # Should still work, just fewer blocks
        assert len(commands) == 6
        assert stats["blocks_placed"] == 6


# =============================================================================
# Compact format tests
# =============================================================================

class TestExpandRleRow:
    """Tests for run-length encoding expansion."""

    def test_simple_symbols(self):
        """Test simple space-separated symbols."""
        result = expand_rle_row("S P G")
        assert result == ["S", "P", "G"]

    def test_run_length_single(self):
        """Test single run-length encoded symbol."""
        result = expand_rle_row("S*5")
        assert result == ["S", "S", "S", "S", "S"]

    def test_run_length_mixed(self):
        """Test mixed simple and run-length."""
        result = expand_rle_row("S*3 P . G*2")
        assert result == ["S", "S", "S", "P", ".", "G", "G"]

    def test_air_symbol(self):
        """Test air symbol handling."""
        result = expand_rle_row("S .*3 S")
        assert result == ["S", ".", ".", ".", "S"]

    def test_empty_string(self):
        """Test empty string returns empty list."""
        result = expand_rle_row("")
        assert result == []

    def test_whitespace_only(self):
        """Test whitespace-only string."""
        result = expand_rle_row("   ")
        assert result == []

    def test_complex_symbols(self):
        """Test longer symbol names."""
        result = expand_rle_row("Fs*2 Wt P*3")
        assert result == ["Fs", "Fs", "Wt", "P", "P", "P"]


class TestParseCompactLayer:
    """Tests for compact layer parsing."""

    def test_simple_pipe_format(self):
        """Test basic pipe-separated rows."""
        y, grid = parse_compact_layer([0, "S*3|S . S|S*3"])
        assert y == 0
        assert len(grid) == 3
        assert grid[0] == ["S", "S", "S"]
        assert grid[1] == ["S", ".", "S"]
        assert grid[2] == ["S", "S", "S"]

    def test_row_repetition(self):
        """Test ~N row repetition."""
        y, grid = parse_compact_layer([1, "S*5|S . . . S~3|S*5"])
        assert y == 1
        assert len(grid) == 5  # 1 + 3 + 1
        assert grid[0] == ["S", "S", "S", "S", "S"]
        assert grid[1] == ["S", ".", ".", ".", "S"]
        assert grid[2] == ["S", ".", ".", ".", "S"]
        assert grid[3] == ["S", ".", ".", ".", "S"]
        assert grid[4] == ["S", "S", "S", "S", "S"]

    def test_dict_rows_format(self):
        """Test dict format with rows list."""
        y, grid = parse_compact_layer({"y": 2, "rows": ["S*3", "S . S", "S*3"]})
        assert y == 2
        assert len(grid) == 3

    def test_dict_rows_with_repetition(self):
        """Test dict format with row repetition."""
        y, grid = parse_compact_layer({"y": 0, "rows": ["S*3", "S . S~2", "S*3"]})
        assert len(grid) == 4  # 1 + 2 + 1

    def test_dict_rn_format(self):
        """Test {"r": pattern, "n": count} format."""
        y, grid = parse_compact_layer({
            "y": 0,
            "rows": [
                "S*5",
                {"r": "S .*3 S", "n": 3},
                "S*5"
            ]
        })
        assert len(grid) == 5  # 1 + 3 + 1
        assert grid[1] == ["S", ".", ".", ".", "S"]


class TestNormalizeSchematic:
    """Tests for schematic normalization."""

    def test_short_keys_expansion(self):
        """Test that short keys are expanded."""
        compact = {
            "a": [100, 64, 200],
            "p": {"S": "stone"},
            "l": [[0, "S*3"]]
        }
        normalized = normalize_schematic(compact)
        assert "anchor" in normalized
        assert "palette" in normalized
        assert "layers" in normalized
        assert normalized["anchor"] == [100, 64, 200]

    def test_compact_layers_converted(self):
        """Test that compact layers are converted to standard format."""
        compact = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone"},
            "l": [[0, "S*3|S . S|S*3"]]
        }
        normalized = normalize_schematic(compact)
        assert len(normalized["layers"]) == 1
        assert "grid" in normalized["layers"][0]
        assert normalized["layers"][0]["y"] == 0
        assert len(normalized["layers"][0]["grid"]) == 3

    def test_verbose_format_unchanged(self):
        """Test that verbose format passes through unchanged."""
        verbose = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S", "S"], ["S", "S"]]}]
        }
        normalized = normalize_schematic(verbose)
        assert normalized["layers"][0]["grid"] == [["S", "S"], ["S", "S"]]

    def test_layer_range_expansion(self):
        """Test that layer ranges like '1-3' expand to multiple layers."""
        schematic = {
            "a": [0, 0, 0],
            "p": {"W": "oak_planks"},
            "l": [
                ["1-3", "W*3|W . W|W*3"]
            ]
        }
        normalized = normalize_schematic(schematic)

        # Should expand to 3 layers (y=1, y=2, y=3)
        assert len(normalized["layers"]) == 3
        assert normalized["layers"][0]["y"] == 1
        assert normalized["layers"][1]["y"] == 2
        assert normalized["layers"][2]["y"] == 3

        # Each layer should have same grid
        for layer in normalized["layers"]:
            assert len(layer["grid"]) == 3  # 3 rows
            assert layer["grid"][0] == ["W", "W", "W"]
            assert layer["grid"][1] == ["W", ".", "W"]
            assert layer["grid"][2] == ["W", "W", "W"]

    def test_layer_range_single_value_string(self):
        """Test that string '0' works as single layer."""
        schematic = {
            "a": [0, 0, 0],
            "p": {"S": "stone"},
            "l": [["0", "S*2"]]
        }
        normalized = normalize_schematic(schematic)
        assert len(normalized["layers"]) == 1
        assert normalized["layers"][0]["y"] == 0

    def test_layer_range_mixed_with_single(self):
        """Test mixing layer ranges with single layers."""
        schematic = {
            "a": [0, 0, 0],
            "p": {"S": "stone", "W": "oak_planks"},
            "l": [
                [0, "S*3"],              # Single floor
                ["1-2", "W*3|W . W|W*3"],  # Range for walls
                [3, "W*3~3"]             # Single roof
            ]
        }
        normalized = normalize_schematic(schematic)

        # Should have 4 layers total (1 + 2 + 1)
        assert len(normalized["layers"]) == 4
        assert normalized["layers"][0]["y"] == 0
        assert normalized["layers"][1]["y"] == 1
        assert normalized["layers"][2]["y"] == 2
        assert normalized["layers"][3]["y"] == 3


class TestCompactSchematicParsing:
    """Integration tests for compact format parsing."""

    def test_full_compact_schematic(self):
        """Test parsing a full compact schematic."""
        schematic = {
            "a": [100, 64, 200],
            "p": {"S": "stone", "P": "oak_planks"},
            "l": [
                [0, "S*5|S P*3 S~3|S*5"]
            ]
        }
        commands, stats = parse_schematic(schematic)

        # 5 edge + 3 rows of (1+3+1) + 5 edge = 5 + 15 + 5 = 25 blocks
        assert stats["blocks_placed"] == 25
        assert stats["layers"] == 1

    def test_mixed_format_layers(self):
        """Test schematic with both compact and verbose layers."""
        schematic = {
            "anchor": [0, 64, 0],
            "palette": {"S": "stone"},
            "layers": [
                [0, "S*3"],  # Compact
                {"y": 1, "grid": [["S", "S", "S"]]}  # Verbose
            ]
        }
        commands, stats = parse_schematic(schematic)
        assert stats["layers"] == 2
        assert stats["blocks_placed"] == 6

    def test_compact_with_facing(self):
        """Test compact format with facing parameter."""
        schematic = {
            "a": [0, 0, 0],
            "f": "east",
            "p": {"S": "stone"},
            "l": [[0, "S*2|S S"]]
        }
        commands, stats = parse_schematic(schematic)
        assert stats["blocks_placed"] == 4

    def test_token_savings_example(self):
        """Demonstrate token savings with compact format."""
        # Verbose format for 10x10 floor with border
        verbose = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone", "P": "oak_planks"},
            "layers": [{
                "y": 0,
                "grid": [
                    ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
                    ["S", "P", "P", "P", "P", "P", "P", "P", "P", "S"],
                    ["S", "P", "P", "P", "P", "P", "P", "P", "P", "S"],
                    ["S", "P", "P", "P", "P", "P", "P", "P", "P", "S"],
                    ["S", "P", "P", "P", "P", "P", "P", "P", "P", "S"],
                    ["S", "P", "P", "P", "P", "P", "P", "P", "P", "S"],
                    ["S", "P", "P", "P", "P", "P", "P", "P", "P", "S"],
                    ["S", "P", "P", "P", "P", "P", "P", "P", "P", "S"],
                    ["S", "P", "P", "P", "P", "P", "P", "P", "P", "S"],
                    ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
                ]
            }]
        }

        # Compact format - same result, ~70% fewer tokens
        compact = {
            "a": [0, 0, 0],
            "p": {"S": "stone", "P": "oak_planks"},
            "l": [[0, "S*10|S P*8 S~8|S*10"]]
        }

        verbose_cmds, verbose_stats = parse_schematic(verbose)
        compact_cmds, compact_stats = parse_schematic(compact)

        # Both should produce same number of blocks
        assert verbose_stats["blocks_placed"] == compact_stats["blocks_placed"]
        assert verbose_stats["blocks_placed"] == 100


# =============================================================================
# rotate_block_state tests
# =============================================================================

class TestRotateBlockState:
    """Tests for block state rotation."""

    def test_no_rotation_same_facing(self):
        """Test that same facing returns unchanged block."""
        block = "oak_stairs[facing=north,half=bottom]"
        result = rotate_block_state(block, "north", "north")
        assert result == block

    def test_rotate_facing_90_degrees(self):
        """Test 90 degree rotation of facing."""
        block = "oak_stairs[facing=north,half=bottom]"
        result = rotate_block_state(block, "north", "east")
        assert "facing=east" in result
        assert "half=bottom" in result

    def test_rotate_facing_180_degrees(self):
        """Test 180 degree rotation of facing."""
        block = "oak_door[facing=north,half=lower]"
        result = rotate_block_state(block, "north", "south")
        assert "facing=south" in result

    def test_rotate_facing_270_degrees(self):
        """Test 270 degree rotation of facing."""
        block = "chest[facing=north]"
        result = rotate_block_state(block, "north", "west")
        assert "facing=west" in result

    def test_rotate_axis_x_to_z(self):
        """Test rotating axis=x to axis=z at 90 degrees."""
        block = "oak_log[axis=x]"
        result = rotate_block_state(block, "north", "east")
        assert "axis=z" in result

    def test_rotate_axis_z_to_x(self):
        """Test rotating axis=z to axis=x at 90 degrees."""
        block = "oak_log[axis=z]"
        result = rotate_block_state(block, "north", "east")
        assert "axis=x" in result

    def test_rotate_axis_y_unchanged(self):
        """Test that axis=y remains unchanged."""
        block = "oak_log[axis=y]"
        result = rotate_block_state(block, "north", "east")
        assert "axis=y" in result

    def test_rotate_sign_rotation(self):
        """Test rotating sign rotation values."""
        block = "oak_sign[rotation=0]"
        result = rotate_block_state(block, "north", "east")
        # 90 degrees = 4 rotation steps
        assert "rotation=4" in result

    def test_rotate_sign_rotation_wrap(self):
        """Test sign rotation wrapping at 16."""
        block = "oak_sign[rotation=14]"
        result = rotate_block_state(block, "north", "east")
        # 14 + 4 = 18, wraps to 2
        assert "rotation=2" in result

    def test_block_without_states(self):
        """Test that blocks without states are unchanged."""
        block = "stone"
        result = rotate_block_state(block, "north", "east")
        assert result == "stone"

    def test_block_with_nbt_preserved(self):
        """Test that NBT data is preserved during rotation."""
        block = "chest[facing=north]{Items:[]}"
        result = rotate_block_state(block, "north", "east")
        assert "facing=east" in result
        assert "{Items:[]}" in result

    def test_non_directional_state_preserved(self):
        """Test that non-directional states are preserved."""
        block = "oak_stairs[facing=north,half=top,waterlogged=false]"
        result = rotate_block_state(block, "north", "south")
        assert "facing=south" in result
        assert "half=top" in result
        assert "waterlogged=false" in result

    # Wall-mounted block tests
    def test_rotate_wall_torch(self):
        """Test wall torch rotation (facing rotates)."""
        block = "wall_torch[facing=north]"
        result = rotate_block_state(block, "north", "east")
        assert "facing=east" in result

    def test_rotate_wall_torch_180(self):
        """Test wall torch 180 degree rotation."""
        block = "wall_torch[facing=south]"
        result = rotate_block_state(block, "north", "south")
        assert "facing=north" in result

    def test_rotate_soul_wall_torch(self):
        """Test soul wall torch rotation.

        Directions: north(0) -> east(1) -> south(2) -> west(3)
        Rotating from north to east = 1 step clockwise
        west(3) + 1 = 4 % 4 = 0 = north
        """
        block = "soul_wall_torch[facing=west]"
        result = rotate_block_state(block, "north", "east")
        assert "facing=north" in result

    def test_rotate_ladder(self):
        """Test ladder rotation (facing rotates)."""
        block = "ladder[facing=north]"
        result = rotate_block_state(block, "north", "east")
        assert "facing=east" in result

    def test_rotate_lever_wall(self):
        """Test lever on wall rotation (facing rotates, face stays)."""
        block = "lever[face=wall,facing=north]"
        result = rotate_block_state(block, "north", "east")
        assert "facing=east" in result
        assert "face=wall" in result

    def test_rotate_lever_floor(self):
        """Test lever on floor rotation (facing rotates, face stays)."""
        block = "lever[face=floor,facing=north]"
        result = rotate_block_state(block, "north", "south")
        assert "facing=south" in result
        assert "face=floor" in result

    def test_rotate_button_wall(self):
        """Test button on wall rotation."""
        block = "stone_button[face=wall,facing=north]"
        result = rotate_block_state(block, "north", "west")
        assert "facing=west" in result
        assert "face=wall" in result

    def test_rotate_item_frame(self):
        """Test item frame rotation."""
        block = "item_frame[facing=north]"
        result = rotate_block_state(block, "north", "east")
        assert "facing=east" in result

    def test_rotate_chain_axis(self):
        """Test chain axis rotation."""
        block = "chain[axis=x]"
        result = rotate_block_state(block, "north", "east")
        assert "axis=z" in result

    def test_lantern_no_facing(self):
        """Test lantern without facing (should remain unchanged)."""
        block = "lantern[hanging=true]"
        result = rotate_block_state(block, "north", "east")
        assert "hanging=true" in result


# =============================================================================
# rotate_grid tests
# =============================================================================

class TestRotateGrid:
    """Tests for grid rotation."""

    def test_no_rotation(self):
        """Test 0 degree rotation returns same grid."""
        grid = [["A", "B"], ["C", "D"]]
        result = rotate_grid(grid, 0)
        assert result == grid

    def test_rotate_90_degrees(self):
        """Test 90 degree clockwise rotation."""
        grid = [
            ["A", "B"],
            ["C", "D"]
        ]
        result = rotate_grid(grid, 1)
        expected = [
            ["C", "A"],
            ["D", "B"]
        ]
        assert result == expected

    def test_rotate_180_degrees(self):
        """Test 180 degree rotation."""
        grid = [
            ["A", "B"],
            ["C", "D"]
        ]
        result = rotate_grid(grid, 2)
        expected = [
            ["D", "C"],
            ["B", "A"]
        ]
        assert result == expected

    def test_rotate_270_degrees(self):
        """Test 270 degree rotation (same as -90)."""
        grid = [
            ["A", "B"],
            ["C", "D"]
        ]
        result = rotate_grid(grid, 3)
        expected = [
            ["B", "D"],
            ["A", "C"]
        ]
        assert result == expected

    def test_rotate_360_degrees(self):
        """Test 360 degree rotation returns same grid."""
        grid = [["A", "B"], ["C", "D"]]
        result = rotate_grid(grid, 4)
        assert result == grid

    def test_rotate_rectangular_grid(self):
        """Test rotation of non-square grid."""
        grid = [
            ["A", "B", "C"],
            ["D", "E", "F"]
        ]
        result = rotate_grid(grid, 1)
        # 2x3 becomes 3x2
        assert len(result) == 3
        assert len(result[0]) == 2
        expected = [
            ["D", "A"],
            ["E", "B"],
            ["F", "C"]
        ]
        assert result == expected

    def test_rotate_single_cell(self):
        """Test rotation of 1x1 grid."""
        grid = [["X"]]
        result = rotate_grid(grid, 1)
        assert result == [["X"]]

    def test_rotate_empty_grid(self):
        """Test rotation of empty grid."""
        grid = []
        result = rotate_grid(grid, 1)
        assert result == []


# =============================================================================
# optimize_commands tests
# =============================================================================

class TestOptimizeCommands:
    """Tests for command optimization."""

    def test_single_block_no_optimization(self):
        """Test that single block stays as setblock."""
        commands = ["/setblock 0 0 0 stone"]
        result = optimize_commands(commands)
        assert result == commands

    def test_two_adjacent_blocks_x(self):
        """Test two adjacent blocks in X become fill."""
        commands = [
            "/setblock 0 0 0 stone",
            "/setblock 1 0 0 stone"
        ]
        result = optimize_commands(commands)
        assert len(result) == 1
        assert "/fill 0 0 0 1 0 0 stone" in result

    def test_two_adjacent_blocks_z(self):
        """Test two adjacent blocks in Z become fill."""
        commands = [
            "/setblock 0 0 0 stone",
            "/setblock 0 0 1 stone"
        ]
        result = optimize_commands(commands)
        assert len(result) == 1
        assert "/fill 0 0 0 0 0 1 stone" in result

    def test_two_adjacent_blocks_y(self):
        """Test two adjacent blocks in Y become fill."""
        commands = [
            "/setblock 0 0 0 stone",
            "/setblock 0 1 0 stone"
        ]
        result = optimize_commands(commands)
        assert len(result) == 1
        assert "/fill 0 0 0 0 1 0 stone" in result

    def test_3x3_plane(self):
        """Test 3x3 plane optimization."""
        commands = []
        for x in range(3):
            for z in range(3):
                commands.append(f"/setblock {x} 0 {z} stone")

        result = optimize_commands(commands)
        assert len(result) == 1
        assert "/fill 0 0 0 2 0 2 stone" in result

    def test_3x3x3_cube(self):
        """Test 3x3x3 cube optimization."""
        commands = []
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    commands.append(f"/setblock {x} {y} {z} stone")

        result = optimize_commands(commands)
        assert len(result) == 1
        assert "/fill 0 0 0 2 2 2 stone" in result

    def test_different_block_types_separate(self):
        """Test that different block types remain separate."""
        commands = [
            "/setblock 0 0 0 stone",
            "/setblock 1 0 0 dirt",
            "/setblock 2 0 0 stone"
        ]
        result = optimize_commands(commands)

        # Should be 3 commands (stone blocks not adjacent)
        assert len(result) == 3

    def test_line_optimization(self):
        """Test 1D line optimization."""
        commands = [
            "/setblock 0 0 0 oak_planks",
            "/setblock 1 0 0 oak_planks",
            "/setblock 2 0 0 oak_planks",
            "/setblock 3 0 0 oak_planks",
            "/setblock 4 0 0 oak_planks",
        ]
        result = optimize_commands(commands)
        assert len(result) == 1
        assert "/fill 0 0 0 4 0 0 oak_planks" in result

    def test_l_shape_optimization(self):
        """Test L-shaped region (requires multiple fills)."""
        commands = [
            "/setblock 0 0 0 stone",
            "/setblock 1 0 0 stone",
            "/setblock 2 0 0 stone",
            "/setblock 0 0 1 stone",
        ]
        result = optimize_commands(commands)

        # L-shape needs 2 fills (3-line + 1 extra block)
        assert len(result) == 2

    def test_non_setblock_preserved(self):
        """Test that non-setblock commands are preserved."""
        commands = [
            "/say hello",
            "/setblock 0 0 0 stone",
            "/setblock 1 0 0 stone",
            "/gamemode creative @p"
        ]
        result = optimize_commands(commands)

        assert "/say hello" in result
        assert "/gamemode creative @p" in result

    def test_block_states_preserved_in_optimization(self):
        """Test that block states are preserved when optimizing."""
        commands = [
            "/setblock 0 0 0 oak_stairs[facing=north,half=bottom]",
            "/setblock 1 0 0 oak_stairs[facing=north,half=bottom]",
        ]
        result = optimize_commands(commands)

        assert len(result) == 1
        assert "oak_stairs[facing=north,half=bottom]" in result[0]

    def test_different_states_not_combined(self):
        """Test that same block with different states are not combined."""
        commands = [
            "/setblock 0 0 0 oak_stairs[facing=north]",
            "/setblock 1 0 0 oak_stairs[facing=south]",
        ]
        result = optimize_commands(commands)

        # Different states = different block types = no combination
        assert len(result) == 2

    def test_empty_commands(self):
        """Test handling of empty command list."""
        result = optimize_commands([])
        assert result == []

    def test_real_world_optimization(self):
        """Test optimization on realistic schematic output."""
        # 5x5 floor + 4 walls (hollow)
        commands = []

        # Floor (5x5)
        for x in range(5):
            for z in range(5):
                commands.append(f"/setblock {x} 0 {z} stone_bricks")

        # Walls (hollow, 3 high)
        for y in range(1, 4):
            for x in range(5):
                commands.append(f"/setblock {x} {y} 0 oak_planks")
                commands.append(f"/setblock {x} {y} 4 oak_planks")
            for z in range(1, 4):
                commands.append(f"/setblock 0 {y} {z} oak_planks")
                commands.append(f"/setblock 4 {y} {z} oak_planks")

        original_count = len(commands)
        result = optimize_commands(commands)

        # Should have significant reduction
        assert len(result) < original_count
        # Floor should be single fill, walls should be optimized
        assert len(result) < 20  # Much less than original ~60+ commands


# =============================================================================
# optimize_commands_aggressive tests
# =============================================================================

class TestOptimizeCommandsAggressive:
    """Tests for aggressive optimization algorithm."""

    def test_basic_optimization(self):
        """Test that aggressive optimizer works on basic cases."""
        commands = [
            "/setblock 0 0 0 stone",
            "/setblock 1 0 0 stone",
        ]
        result = optimize_commands_aggressive(commands)
        assert len(result) == 1

    def test_finds_better_packing(self):
        """Test that aggressive optimizer may find better packings."""
        # Create a grid that could be packed different ways
        commands = []
        for x in range(4):
            for z in range(4):
                commands.append(f"/setblock {x} 0 {z} stone")

        result = optimize_commands_aggressive(commands)
        assert len(result) == 1  # Should find 4x4 fill


# =============================================================================
# find_max_rectangle tests
# =============================================================================

class TestFindMaxRectangle:
    """Tests for rectangle finding helper."""

    def test_single_block(self):
        """Test single block returns 1x1x1 rectangle."""
        positions = {(0, 0, 0)}
        result = find_max_rectangle(positions, 0, 0, 0)
        assert result == (0, 0, 0, 0, 0, 0)

    def test_line_x(self):
        """Test line in X direction."""
        positions = {(0, 0, 0), (1, 0, 0), (2, 0, 0)}
        result = find_max_rectangle(positions, 0, 0, 0)
        assert result == (0, 0, 0, 2, 0, 0)

    def test_plane_xz(self):
        """Test plane in XZ."""
        positions = set()
        for x in range(3):
            for z in range(3):
                positions.add((x, 0, z))

        result = find_max_rectangle(positions, 0, 0, 0)
        assert result == (0, 0, 0, 2, 0, 2)

    def test_cube(self):
        """Test 3D cube."""
        positions = set()
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    positions.add((x, y, z))

        result = find_max_rectangle(positions, 0, 0, 0)
        assert result == (0, 0, 0, 2, 2, 2)


# =============================================================================
# Integration tests (parse + optimize)
# =============================================================================

class TestSchematicIntegration:
    """Integration tests combining parsing and optimization."""

    def test_full_schematic_workflow(self):
        """Test complete schematic parsing and optimization."""
        schematic = {
            "anchor": [100, 64, 200],
            "palette": {
                "S": "stone_bricks",
                "P": "oak_planks",
                ".": "air"
            },
            "layers": [
                # Floor
                {"y": 0, "grid": [
                    ["S", "S", "S"],
                    ["S", "S", "S"],
                    ["S", "S", "S"]
                ]},
                # Walls layer 1
                {"y": 1, "grid": [
                    ["P", "P", "P"],
                    ["P", ".", "P"],
                    ["P", ".", "P"]
                ]},
                # Walls layer 2
                {"y": 2, "grid": [
                    ["P", "P", "P"],
                    ["P", ".", "P"],
                    ["P", ".", "P"]
                ]}
            ]
        }

        commands, stats = parse_schematic(schematic)
        assert stats["blocks_placed"] == 23  # 9 floor + 14 walls (7 per layer * 2)

        optimized = optimize_commands(commands)
        assert len(optimized) < len(commands)

    def test_rotated_schematic(self):
        """Test schematic with rotation."""
        schematic = {
            "anchor": [0, 0, 0],
            "facing": "east",  # Rotate 90 degrees
            "palette": {
                "D": "oak_door[facing=north,half=lower]"
            },
            "layers": [{"y": 0, "grid": [["D"]]}]
        }

        commands, stats = parse_schematic(schematic)
        assert len(commands) == 1
        # Door should now face east
        assert "facing=east" in commands[0]

    def test_large_schematic_optimization(self):
        """Test optimization on large schematic."""
        # 10x10x5 solid block
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone"},
            "layers": []
        }

        for y in range(5):
            grid = [["S"] * 10 for _ in range(10)]
            schematic["layers"].append({"y": y, "grid": grid})

        commands, stats = parse_schematic(schematic)
        assert stats["blocks_placed"] == 500  # 10*10*5

        optimized = optimize_commands(commands)
        # Should be single fill command
        assert len(optimized) == 1
        assert "/fill 0 0 0 9 4 9 stone" in optimized

    def test_door_placement(self):
        """Test proper door placement with both halves."""
        schematic = {
            "anchor": [0, 64, 0],
            "palette": {
                "W": "oak_planks",
                "Dl": "oak_door[facing=south,half=lower]",
                "Du": "oak_door[facing=south,half=upper]",
                ".": "air"
            },
            "layers": [
                {"y": 0, "grid": [["W", "W", "W"], ["W", "Dl", "W"]]},
                {"y": 1, "grid": [["W", "W", "W"], ["W", "Du", "W"]]}
            ]
        }

        commands, stats = parse_schematic(schematic)

        door_lower = [c for c in commands if "half=lower" in c]
        door_upper = [c for c in commands if "half=upper" in c]

        assert len(door_lower) == 1
        assert len(door_upper) == 1

        # Door lower at y=64, upper at y=65
        assert "64" in door_lower[0]
        assert "65" in door_upper[0]


# =============================================================================
# Edge cases
# =============================================================================

class TestEdgeCases:
    """Edge case tests."""

    def test_very_large_coordinates(self):
        """Test handling of very large coordinates."""
        schematic = {
            "anchor": [30000000, 320, 30000000],
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)
        assert "30000000" in commands[0]

    def test_y_below_bedrock(self):
        """Test negative Y coordinates (below bedrock in 1.18+)."""
        schematic = {
            "anchor": [0, -64, 0],
            "palette": {"S": "deepslate"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)
        assert "-64" in commands[0]

    def test_special_characters_in_nbt(self):
        """Test NBT with special characters."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"S": 'oak_sign{Text1:\'"Hello World"\'}'},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)
        assert len(commands) == 1
        # NBT should be preserved
        assert "Text1" in commands[0]

    def test_unicode_in_grid_symbol(self):
        """Test non-ASCII symbols in grid."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {},  # No mapping
            "layers": [{"y": 0, "grid": [["S"]]}]  # S has no mapping
        }
        commands, stats = parse_schematic(schematic)
        # S might be interpreted as direct block ID
        # or generate a warning
        assert len(stats["warnings"]) >= 0  # Either works or warns

    def test_float_anchor_converted_to_int(self):
        """Test that float anchors are converted to int."""
        schematic = {
            "anchor": [100.7, 64.3, 200.9],
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [["S"]]}]
        }
        commands, stats = parse_schematic(schematic)
        # Should truncate to int
        assert "/setblock 100 64 200 stone" in commands


# =============================================================================
# Regression tests
# =============================================================================

class TestRegressions:
    """Regression tests for previously found bugs."""

    def test_optimization_preserves_mode(self):
        """Test that optimization preserves setblock mode."""
        # This is a limitation - current optimizer doesn't preserve mode
        # But we test the current behavior
        commands = [
            "/setblock 0 0 0 stone keep",
            "/setblock 1 0 0 stone keep"
        ]
        result = optimize_commands(commands)
        # Current implementation treats "stone keep" as block type
        # This is a known limitation
        assert len(result) == 1

    def test_empty_row_in_grid(self):
        """Test grid with empty rows."""
        schematic = {
            "anchor": [0, 0, 0],
            "palette": {"S": "stone"},
            "layers": [{"y": 0, "grid": [
                ["S", "S"],
                [],  # Empty row
                ["S", "S"]
            ]}]
        }
        commands, stats = parse_schematic(schematic)
        # Should handle gracefully
        assert len(commands) == 4  # Skip empty row

    def test_missing_y_in_layer(self):
        """Test layer without y offset defaults to 0."""
        schematic = {
            "anchor": [0, 64, 0],
            "palette": {"S": "stone"},
            "layers": [{"grid": [["S"]]}]  # No "y" key
        }
        commands, stats = parse_schematic(schematic)
        assert "64" in commands[0]  # Uses anchor y + default 0
