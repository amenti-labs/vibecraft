"""
Workflow management tool handlers.

This module contains handlers for build workflow management including
status tracking, phase advancement, and workflow reset.
"""

from typing import Dict, Any, List
from mcp.types import TextContent


async def handle_workflow_status(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle workflow_status tool."""
    from ..server import workflow

    status = workflow.get_status()
    current = workflow.current_phase()

    output = [
        "🗂️ **Build Workflow Status**",
        "",
        f"**Current Phase:** {current.name} (`{current.identifier}`)",
        "",
    ]

    for phase_info in status["phases"]:
        emoji = {
            "completed": "✅",
            "in_progress": "🟡",
            "pending": "⚪",
        }.get(phase_info["status"], "⚪")

        line = f"{emoji} {phase_info['name']} (`{phase_info['id']}`)"
        if phase_info["required_validations"]:
            completed = phase_info["completed_validations"]
            requirements = ", ".join(
                f"{req} ({completed.get(req, 0)})" for req in phase_info["required_validations"]
            )
            line += f" – validations: {requirements}"
        output.append(line)

    output.append("")
    output.append("Recorded validations:")
    validations = status.get("validations", {})
    if validations:
        for vtype, entries in validations.items():
            output.append(f"- {vtype}: {len(entries)} run(s)")
    else:
        output.append("- none yet")

    logger_instance.info("Workflow status queried")
    return [TextContent(type="text", text="\n".join(output))]


async def handle_workflow_advance(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle workflow_advance tool."""
    from ..server import workflow

    advance_result = workflow.advance()

    if advance_result.get("advanced"):
        next_phase = workflow.current_phase()
        message = [
            "✅ **Workflow advanced**",
            f"Next phase: {next_phase.name} (`{next_phase.identifier}`)",
        ]
        logger_instance.info(f"Workflow advanced to {next_phase.identifier}")
        return [TextContent(type="text", text="\n".join(message))]

    missing = advance_result.get("missing")
    if missing:
        message = [
            "⚠️ **Cannot advance yet**",
            f"Phase `{advance_result.get('phase')}` still requires: {', '.join(missing)}",
            "Run the required validations and try again.",
        ]
        logger_instance.info(f"Workflow advance blocked: missing {missing}")
    else:
        message = [
            "ℹ️ Workflow advance skipped",
            advance_result.get("reason", "No additional information"),
        ]
        logger_instance.info("Workflow advance skipped")
    return [TextContent(type="text", text="\n".join(message))]


async def handle_workflow_reset(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle workflow_reset tool."""
    from ..server import workflow

    if not arguments.get("confirm", False):
        return [
            TextContent(
                type="text",
                text="⚠️ Reset not confirmed. Pass `confirm=true` to reset the workflow.",
            )
        ]

    workflow.reset()
    logger_instance.info("Workflow reset to planning phase")
    return [TextContent(type="text", text="✅ Workflow reset to planning phase.")]
