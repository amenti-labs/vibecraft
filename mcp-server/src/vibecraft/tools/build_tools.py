"""
Build Tool Handlers

Handles direct Minecraft command execution for building structures.
Supports both direct command lists and code-generated commands.
"""

from typing import Dict, Any, List
from mcp.types import TextContent
import logging
from ..code_sandbox import execute_command_generator, CodeSandboxError

logger = logging.getLogger(__name__)


async def handle_build(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """
    Handle build tool.

    Executes Minecraft commands directly for block placement.

    Args:
        arguments: Tool arguments containing commands list and optional preview_only
        rcon: RCON manager instance
        config: Server configuration
        logger_instance: Logger instance

    Returns:
        List of TextContent with execution results
    """
    # Parse arguments
    commands = arguments.get("commands")
    code = arguments.get("code")
    preview_only = arguments.get("preview_only", False)
    description = arguments.get("description", "Building structure")

    # Determine input mode: commands list OR code
    if code:
        # Code generation mode
        logger_instance.info(f"Processing build via code generation: {description}")

        try:
            commands = execute_command_generator(code)
            logger_instance.info(f"Code generated {len(commands)} commands")
        except CodeSandboxError as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Code validation error: {e}\n\n"
                    f"Your code must:\n"
                    f"  - Create a 'commands' list\n"
                    f"  - Only use loops, math, strings, lists\n"
                    f"  - Not import modules or access files\n\n"
                    f"Example:\n"
                    f"```python\n"
                    f"commands = []\n"
                    f"for x in range(100, 110):\n"
                    f'    commands.append(f"/setblock {{x}} 64 200 stone")\n'
                    f"```",
                )
            ]
        except Exception as e:
            logger_instance.error(f"Code execution failed: {e}", exc_info=True)
            return [
                TextContent(
                    type="text", text=f"❌ Unexpected error executing code: {type(e).__name__}: {e}"
                )
            ]

    elif commands:
        # Direct commands list mode
        if not isinstance(commands, list):
            return [TextContent(type="text", text="❌ Error: commands must be a list of strings")]

    else:
        # No input provided
        return [
            TextContent(
                type="text",
                text="❌ Error: Either 'commands' list or 'code' must be provided\n\n"
                "**Option 1 - Direct commands:**\n"
                "build(commands=[\n"
                "  '/fill 100 64 200 110 64 210 oak_planks',\n"
                "  '/setblock 105 65 205 crafting_table'\n"
                "])\n\n"
                "**Option 2 - Code generation:**\n"
                'build(code="""\n'
                "commands = []\n"
                "for x in range(100, 110):\n"
                "    commands.append(f'/setblock {x} 64 200 stone')\n"
                '""")',
            )
        ]

    # Validate command format
    for i, cmd in enumerate(commands):
        if not isinstance(cmd, str):
            return [
                TextContent(type="text", text=f"❌ Error: command at index {i} is not a string")
            ]

        # Commands should start with / or // (Minecraft or WorldEdit command format)
        if not cmd.startswith("/"):
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error: command at index {i} must start with '/' or '//'\n\nGot: {cmd}\nExpected: /{cmd} or //{cmd}",
                )
            ]

    command_count = len(commands)
    logger_instance.info(f"Processing build: {description} ({command_count} commands)")

    # Preview mode - return commands without executing
    if preview_only:
        result_lines = [
            f"🏗️ Build Preview: {description}",
            "",
            f"**Commands:** {command_count}",
            "",
        ]

        # Show all commands if 20 or less
        if command_count <= 20:
            result_lines.append(f"**All Commands ({command_count}):**")
            result_lines.append("```")
            result_lines.extend(commands)
            result_lines.append("```")
        else:
            result_lines.append(f"**Sample Commands (first 20 of {command_count}):**")
            result_lines.append("```")
            result_lines.extend(commands[:20])
            result_lines.append("...")
            result_lines.append("```")
            result_lines.append("")
            result_lines.append(
                f"💡 Set preview_only=false to execute all {command_count} commands"
            )

        return [TextContent(type="text", text="\n".join(result_lines))]

    # Execute commands
    logger_instance.info(f"Executing {command_count} commands...")

    result_lines = [
        f"🏗️ Building: {description}",
        "",
        f"Commands: {command_count}",
        "",
        "Progress:",
    ]

    errors = []
    commands_executed = 0

    for i, cmd in enumerate(commands):
        try:
            # Execute command via RCON
            result = rcon.send_command(cmd)

            # Check for errors in result
            if result and any(
                err_word in result.lower()
                for err_word in ["error", "unknown", "incorrect", "invalid", "cannot"]
            ):
                errors.append(f"Command {i+1} failed: {cmd}\nResult: {result}")
                logger_instance.warning(f"Command error: {cmd} -> {result}")

            commands_executed += 1

            # Update progress every 50 commands or on last command
            if (i + 1) % 50 == 0 or (i + 1) == command_count:
                progress_pct = (commands_executed / command_count) * 100
                result_lines.append(f"  [{commands_executed}/{command_count}] {progress_pct:.1f}%")

        except Exception as e:
            logger_instance.error(f"Error executing command {i+1}: {e}", exc_info=True)
            errors.append(f"Command {i+1}: {cmd}\nError: {str(e)}")

    # Final result
    result_lines.append("")

    if errors:
        result_lines.append("⚠️ Build completed with errors:")
        result_lines.extend([f"  - {err}" for err in errors[:5]])
        if len(errors) > 5:
            result_lines.append(f"  ... and {len(errors) - 5} more errors")
        result_lines.append("")
        result_lines.append("💡 You may need to use //undo to revert changes.")
    else:
        result_lines.append("✅ Build completed successfully!")

    result_lines.extend(
        [
            "",
            f"📊 Stats: {command_count} commands executed",
        ]
    )

    logger_instance.info(f"Build complete: {description}")

    return [TextContent(type="text", text="\n".join(result_lines))]
