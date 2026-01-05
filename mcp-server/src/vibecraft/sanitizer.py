"""Command sanitization and validation for VibeCraft"""

import re
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of command validation"""

    is_valid: bool
    error_message: Optional[str] = None
    sanitized_command: Optional[str] = None


# Dangerous command patterns - pre-compiled for performance
_DANGEROUS_PATTERN_STRS = [
    r"//regen\s",  # World regeneration - can destroy builds
    r"//delchunks",  # Chunk deletion
    r"/stop\s",  # Stop server
    r"/restart\s",  # Restart server
    r"//limit\s+\d{7,}",  # Extremely high limits
    r"//timeout\s+\d{7,}",  # Extremely high timeouts
]
DANGEROUS_PATTERNS: List[re.Pattern] = [
    re.compile(p, re.IGNORECASE) for p in _DANGEROUS_PATTERN_STRS
]

# Pre-compiled coordinate extraction patterns
COORD_COMMA_PATTERN = re.compile(r"(-?\d+),(-?\d+),(-?\d+)")
COORD_SPACE_PATTERN = re.compile(r"\s(-?\d+)\s+(-?\d+)\s+(-?\d+)")

# Player-context commands that may not work from console
PLAYER_CONTEXT_COMMANDS = [
    "jumpto",
    "thru",
    "ascend",
    "descend",
    "ceil",
    "unstuck",
    "hpos1",
    "hpos2",
]


def sanitize_command(
    command: str, allow_dangerous: bool = False, max_length: int = 1000
) -> ValidationResult:
    """
    Sanitize and validate a Minecraft/WorldEdit command.

    Args:
        command: The command to validate
        allow_dangerous: Whether to allow potentially dangerous commands
        max_length: Maximum allowed command length

    Returns:
        ValidationResult with validation status and sanitized command
    """
    # Strip whitespace
    command = command.strip()

    # Check for empty command
    if not command:
        return ValidationResult(is_valid=False, error_message="Command cannot be empty")

    # Check command length
    if len(command) > max_length:
        return ValidationResult(
            is_valid=False,
            error_message=f"Command exceeds maximum length of {max_length} characters",
        )

    # Remove leading slash if present (RCON doesn't need it)
    sanitized = command
    if sanitized.startswith("/"):
        sanitized = sanitized[1:]

    # Check for null bytes or other control characters
    if "\x00" in sanitized or any(ord(c) < 32 and c not in "\t\n\r" for c in sanitized):
        return ValidationResult(
            is_valid=False, error_message="Command contains invalid control characters"
        )

    # Check for command injection attempts (chaining with ; or &&)
    # BUT: WorldEdit expression commands (//generate, //deform) legitimately use &&, ||, <, >
    worldedit_expression_commands = ["generate", "deform", "calc"]
    is_expression_command = any(sanitized.startswith(cmd) for cmd in worldedit_expression_commands)

    if not is_expression_command:
        if ";" in sanitized or "&&" in sanitized or "||" in sanitized:
            return ValidationResult(
                is_valid=False,
                error_message="Command chaining is not allowed (found ';', '&&', or '||')",
            )

    # Check for dangerous commands if safety is enabled
    if not allow_dangerous:
        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(sanitized):
                return ValidationResult(
                    is_valid=False,
                    error_message="Potentially dangerous command blocked. "
                    "Set VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=true to enable.",
                )

    return ValidationResult(is_valid=True, sanitized_command=sanitized)


def extract_coordinates(command: str) -> list[Tuple[int, int, int]]:
    """
    Extract coordinates from a command for bounds checking.

    Returns list of (x, y, z) tuples found in the command.
    """
    coords = []

    # Pattern for X,Y,Z format (WorldEdit console syntax)
    for match in COORD_COMMA_PATTERN.finditer(command):
        coords.append((int(match.group(1)), int(match.group(2)), int(match.group(3))))

    # Pattern for X Y Z format (vanilla Minecraft syntax)
    for match in COORD_SPACE_PATTERN.finditer(command):
        coords.append((int(match.group(1)), int(match.group(2)), int(match.group(3))))

    return coords


def validate_coordinates_in_bounds(
    command: str,
    min_x: Optional[int] = None,
    max_x: Optional[int] = None,
    min_y: Optional[int] = None,
    max_y: Optional[int] = None,
    min_z: Optional[int] = None,
    max_z: Optional[int] = None,
) -> ValidationResult:
    """
    Validate that all coordinates in a command are within specified bounds.

    Args:
        command: The command to check
        min_x, max_x, min_y, max_y, min_z, max_z: Coordinate bounds (None = no limit)

    Returns:
        ValidationResult indicating if coordinates are within bounds
    """
    # If no bounds are set, skip validation
    if all(
        bound is None for bound in [min_x, max_x, min_y, max_y, min_z, max_z]
    ):
        return ValidationResult(is_valid=True, sanitized_command=command)

    coords = extract_coordinates(command)

    if not coords:
        # No coordinates found, allow command
        return ValidationResult(is_valid=True, sanitized_command=command)

    # Check each coordinate against bounds
    for x, y, z in coords:
        if min_x is not None and x < min_x:
            return ValidationResult(
                is_valid=False, error_message=f"X coordinate {x} is below minimum {min_x}"
            )
        if max_x is not None and x > max_x:
            return ValidationResult(
                is_valid=False, error_message=f"X coordinate {x} exceeds maximum {max_x}"
            )
        if min_y is not None and y < min_y:
            return ValidationResult(
                is_valid=False, error_message=f"Y coordinate {y} is below minimum {min_y}"
            )
        if max_y is not None and y > max_y:
            return ValidationResult(
                is_valid=False, error_message=f"Y coordinate {y} exceeds maximum {max_y}"
            )
        if min_z is not None and z < min_z:
            return ValidationResult(
                is_valid=False, error_message=f"Z coordinate {z} is below minimum {min_z}"
            )
        if max_z is not None and z > max_z:
            return ValidationResult(
                is_valid=False, error_message=f"Z coordinate {z} exceeds maximum {max_z}"
            )

    return ValidationResult(is_valid=True, sanitized_command=command)


def check_player_context_warning(command: str) -> Optional[str]:
    """
    Check if command requires player context and return warning if so.

    Returns:
        Warning message if command needs player context, None otherwise
    """
    cmd_lower = command.lower().lstrip("/")
    for player_cmd in PLAYER_CONTEXT_COMMANDS:
        if cmd_lower.startswith(player_cmd.lower()):
            return (
                f"Warning: Command '{player_cmd}' typically requires player context. "
                f"It may not work from console/RCON. "
                f"Consider using teleport or coordinate-based alternatives."
            )
    return None
