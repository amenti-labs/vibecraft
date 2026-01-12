"""
Core/fundamental tool handlers.

This module contains handlers for core operations including command execution,
server info, schematics, templates, and generic WorldEdit commands.
"""

from typing import Dict, Any, List
from mcp.types import TextContent
import json

from ..paths import get_data_file


# WorldEdit tool prefixes - maps tool names to command prefixes
WORLD_EDIT_TOOL_PREFIXES = {
    "worldedit_selection": "//",
    "worldedit_region": "//",
    "worldedit_generation": "//",
    "worldedit_clipboard": "//",
    "worldedit_schematic": "//",
    "worldedit_history": "//",
    "worldedit_utility": "//",
    "worldedit_biome": "//",
    "worldedit_brush": "//",
    "worldedit_general": "//",
    "worldedit_navigation": "//",
    "worldedit_chunk": "//",
    "worldedit_snapshot": "//",
    "worldedit_scripting": "//",
    "worldedit_reference": "//",
    "worldedit_tools": "//",
}


def prepare_worldedit_command(tool_name: str, command: str) -> str:
    """Prepare a WorldEdit command with appropriate prefix."""
    # Normalize command (remove leading slashes if present)
    normalized = command.lstrip("/")

    # worldedit_tools: Different commands use different prefixes
    if tool_name == "worldedit_tools":
        # Super pickaxe shorthand uses /sp, other tools use /tool, /mask, etc.
        # Use // for WorldEdit commands sent via the client bridge
        if normalized.startswith("sp ") or normalized.startswith("superpickaxe"):
            return "//" + normalized
        return "//" + normalized

    prefix = WORLD_EDIT_TOOL_PREFIXES.get(tool_name)
    if prefix:
        # Build the command with prefix (//)
        return prefix + normalized

    return command


async def handle_rcon_command(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle rcon_command tool - base command execution."""
    from ..sanitizer import (
        sanitize_command,
        validate_coordinates_in_bounds,
        check_player_context_warning,
    )

    command = arguments.get("command", "").strip()

    # Validate command
    if config.enable_safety_checks:
        validation = sanitize_command(
            command,
            allow_dangerous=config.allow_dangerous_commands,
            max_length=config.max_command_length,
        )

        if not validation.is_valid:
            return [
                TextContent(
                    type="text", text=f"❌ Command validation failed: {validation.error_message}"
                )
            ]

        command = validation.sanitized_command

        # Check coordinate bounds if configured
        bounds_validation = validate_coordinates_in_bounds(
            command,
            config.build_min_x,
            config.build_max_x,
            config.build_min_y,
            config.build_max_y,
            config.build_min_z,
            config.build_max_z,
        )

        if not bounds_validation.is_valid:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Coordinate validation failed: {bounds_validation.error_message}",
                )
            ]

    # Check for player context warning
    warning = check_player_context_warning(command)

    # Execute command (using async method to avoid blocking event loop)
    try:
        response = await rcon.execute_command_async(command)
        result = f"✅ Command executed: {command}\n\nResponse: {response}"

        if warning:
            result = f"⚠️ {warning}\n\n{result}"

        logger_instance.info(f"Command executed: {command[:50]}...")
        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger_instance.error(f"Error executing command: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error executing command: {str(e)}")]


async def handle_worldedit_generic(
    arguments: Dict[str, Any], rcon, config, logger_instance, tool_name: str
) -> List[TextContent]:
    """Handle generic WorldEdit commands (20 tools via WORLD_EDIT_TOOL_PREFIXES)."""
    command = arguments.get("command", "").strip()

    if not command:
        return [TextContent(type="text", text="❌ Command cannot be empty")]

    command = prepare_worldedit_command(tool_name, command)

    # Execute via rcon_command handler
    return await handle_rcon_command({"command": command}, rcon, config, logger_instance)


async def handle_get_server_info(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle get_server_info tool."""
    info = rcon.get_server_info()

    # Try to detect WorldEdit version if enabled
    worldedit_version = "Unknown"
    if config.enable_version_detection:
        detected = rcon.detect_worldedit_version()
        if detected:
            worldedit_version = detected

    result = [
        "🖥️ Server Information:",
        "",
        f"Players: {info.get('players', 'Unknown')}",
        f"Time: {info.get('time', 'Unknown')}",
        f"Difficulty: {info.get('difficulty', 'Unknown')}",
        f"WorldEdit Version: {worldedit_version}",
        "",
        f"Client Bridge: ws://{config.client_host}:{config.client_port}{config.client_path}",
        f"Safety Checks: {'Enabled' if config.enable_safety_checks else 'Disabled'}",
    ]

    logger_instance.info("Server info retrieved")
    return [TextContent(type="text", text="\n".join(result))]


async def handle_building_template(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle building_template tool."""
    action = arguments.get("action")
    if not action:
        return [TextContent(type="text", text="❌ Error: 'action' parameter is required")]

    # Load templates from JSON file
    templates_file = get_data_file("building_templates.json")

    try:
        with open(templates_file, "r") as f:
            templates_data = json.load(f)
            templates = templates_data.get("templates", {})
    except FileNotFoundError:
        return [TextContent(type="text", text=f"❌ Templates file not found: {templates_file}")]
    except json.JSONDecodeError as e:
        return [TextContent(type="text", text=f"❌ Error parsing templates JSON: {e}")]

    if action == "list":
        # List all templates with brief info
        result_text = f"📚 **Building Templates Library** ({len(templates)} templates)\n\n"

        # Group by category
        by_category = {}
        for tid, tmpl in templates.items():
            cat = tmpl["metadata"]["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tmpl)

        for category, tmpls in sorted(by_category.items()):
            result_text += f"**{category.title()}** ({len(tmpls)}):\n"
            for tmpl in tmpls:
                meta = tmpl["metadata"]
                diff_emoji = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
                emoji = diff_emoji.get(meta["difficulty"], "⚪")
                result_text += (
                    f"  {emoji} **{tmpl['template_id']}** - {meta['name']} ({meta['difficulty']})\n"
                )
                result_text += f"     {meta['description']}\n"
            result_text += "\n"

        result_text += (
            "\n💡 Use building_template(action='get', template_id='<id>') to view full details\n"
        )
        result_text += (
            "💡 Use building_template(action='search', category='<cat>') to filter by category"
        )

        logger_instance.info(f"Listed {len(templates)} building templates")
        return [TextContent(type="text", text=result_text)]

    elif action == "search":
        # Search templates
        category_filter = arguments.get("category")
        difficulty_filter = arguments.get("difficulty")
        style_tags_filter = arguments.get("style_tags", [])

        results = []
        for tid, tmpl in templates.items():
            meta = tmpl["metadata"]

            # Apply filters
            if category_filter and meta["category"] != category_filter:
                continue
            if difficulty_filter and meta["difficulty"] != difficulty_filter:
                continue
            if style_tags_filter:
                tmpl_tags = meta.get("style_tags", [])
                if not any(tag in tmpl_tags for tag in style_tags_filter):
                    continue

            results.append(tmpl)

        if not results:
            return [TextContent(type="text", text="❌ No templates found matching your criteria")]

        result_text = f"🔍 **Search Results** ({len(results)} found)\n\n"
        for tmpl in results:
            meta = tmpl["metadata"]
            diff_emoji = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
            emoji = diff_emoji.get(meta["difficulty"], "⚪")
            result_text += f"{emoji} **{tmpl['template_id']}** - {meta['name']}\n"
            result_text += f"   Category: {meta['category']} | Difficulty: {meta['difficulty']}\n"
            result_text += f"   {meta['description']}\n"
            tags = ", ".join(meta.get("style_tags", []))
            if tags:
                result_text += f"   Tags: {tags}\n"
            result_text += "\n"

        result_text += (
            "\n💡 Use building_template(action='get', template_id='<id>') to view full template"
        )

        logger_instance.info(f"Template search: {len(results)} results")
        return [TextContent(type="text", text=result_text)]

    elif action == "get":
        # Get full template details
        template_id = arguments.get("template_id")
        if not template_id:
            return [
                TextContent(type="text", text="❌ Error: 'template_id' required for get action")
            ]

        if template_id not in templates:
            available = ", ".join(templates.keys())
            return [
                TextContent(
                    type="text",
                    text=f"❌ Template '{template_id}' not found. Available: {available}",
                )
            ]

        tmpl = templates[template_id]
        meta = tmpl["metadata"]
        params = tmpl["parameters"]
        components = tmpl["components"]
        build_seq = tmpl["build_sequence"]
        dims = tmpl.get("dimensions", {})

        result_text = f"🏗️ **{meta['name']}**\n\n"
        result_text += f"**Description**: {meta['description']}\n"
        result_text += f"**Category**: {meta['category']} | **Difficulty**: {meta['difficulty']}\n"
        result_text += f"**Estimated Time**: ~{meta.get('estimated_time_seconds', 60)} seconds\n"
        tags = ", ".join(meta.get("style_tags", []))
        if tags:
            result_text += f"**Style Tags**: {tags}\n"
        result_text += "\n"

        # Dimensions
        result_text += "📐 **Dimensions**:\n"
        result_text += f"   Footprint: {dims.get('footprint', 'Varies by parameters')}\n"
        result_text += f"   Height: {dims.get('total_height', 'Varies by parameters')}\n"
        if "interior_space" in dims:
            result_text += f"   Interior: {dims['interior_space']}\n"
        result_text += "\n"

        # Parameters
        result_text += "⚙️ **Customizable Parameters**:\n"
        for param_name, param_def in params.items():
            ptype = param_def["type"]
            default = param_def["default"]
            desc = param_def.get("description", "")

            if ptype == "integer":
                min_val = param_def.get("min", "")
                max_val = param_def.get("max", "")
                result_text += (
                    f"   • {param_name}: {min_val}-{max_val} blocks (default: {default}) - {desc}\n"
                )
            elif ptype == "enum":
                options = ", ".join(param_def.get("options", []))
                result_text += f"   • {param_name}: {options} (default: {default}) - {desc}\n"
            elif ptype == "boolean":
                result_text += f"   • {param_name}: true/false (default: {default}) - {desc}\n"
        result_text += "\n"

        # Build sequence
        result_text += "🔨 **Build Sequence** ({} components):\n".format(len(build_seq))
        for i, step in enumerate(build_seq, 1):
            comp_id = step["component_id"]
            comp = components.get(comp_id, {})
            checkpoint = " 🛑 [CHECKPOINT]" if step.get("checkpoint") else ""
            result_text += f"   {i}. **{comp_id}**{checkpoint}\n"
            result_text += f"      {comp.get('description', 'No description')}\n"

            # Show first step of component as example
            steps = comp.get("steps", [])
            if steps:
                first_step = steps[0]
                result_text += f"      Example: {first_step.get('action', '')} (tool: {first_step.get('tool', '')})\n"
                if "command" in first_step:
                    result_text += f"      Command: {first_step['command']}\n"

        result_text += "\n"

        # Material palette reference
        if "material_palette" in tmpl:
            result_text += f"🎨 **Material Palette**: {tmpl['material_palette']}\n"
            result_text += "   (See context/minecraft_material_palettes.json for details)\n\n"

        result_text += "💡 **Usage**:\n"
        result_text += "1. Customize parameters based on user preferences\n"
        result_text += "2. Follow build_sequence in order\n"
        result_text += "3. For each component, execute steps using specified tools\n"
        result_text += "4. Replace {{parameter}} placeholders with actual values\n"
        result_text += "5. Use checkpoints to verify progress with user\n"

        logger_instance.info(f"Template retrieved: {template_id}")
        return [TextContent(type="text", text=result_text)]

    elif action == "customize":
        # Show customization guide for a template
        template_id = arguments.get("template_id")
        if not template_id:
            return [
                TextContent(
                    type="text", text="❌ Error: 'template_id' required for customize action"
                )
            ]

        if template_id not in templates:
            return [TextContent(type="text", text=f"❌ Template '{template_id}' not found")]

        tmpl = templates[template_id]
        meta = tmpl["metadata"]
        params = tmpl["parameters"]

        result_text = f"🎨 **Customization Guide: {meta['name']}**\n\n"
        result_text += "**How to Customize**:\n"
        result_text += "1. Review parameters below\n"
        result_text += "2. Ask user for preferences (or use defaults)\n"
        result_text += "3. Validate values are within min/max ranges\n"
        result_text += "4. Substitute {{parameter}} in component commands\n\n"

        result_text += "**Available Parameters**:\n\n"
        for param_name, param_def in params.items():
            ptype = param_def["type"]
            default = param_def["default"]
            desc = param_def.get("description", "")

            result_text += f"**{param_name}**\n"
            result_text += f"  Type: {ptype}\n"
            result_text += f"  Default: {default}\n"

            if ptype == "integer":
                min_val = param_def.get("min")
                max_val = param_def.get("max")
                result_text += f"  Range: {min_val} to {max_val}\n"
            elif ptype == "enum":
                options = param_def.get("options", [])
                result_text += f"  Options: {', '.join(options)}\n"

            result_text += f"  Description: {desc}\n\n"

        result_text += "**Example Customization**:\n"
        result_text += "User: 'Make it taller and use dark materials'\n"
        result_text += "Agent: Sets parameters:\n"

        # Show example customization based on first few parameters
        for param_name, param_def in list(params.items())[:3]:
            ptype = param_def["type"]
            if ptype == "integer" and "height" in param_name.lower():
                max_val = param_def.get("max")
                result_text += f"  {param_name} = {max_val} (max height)\n"
            elif ptype == "enum" and "material" in param_name.lower():
                options = param_def.get("options", [])
                dark_option = next((opt for opt in options if "dark" in opt.lower()), options[0])
                result_text += f"  {param_name} = '{dark_option}' (dark material)\n"

        logger_instance.info(f"Template customization guide: {template_id}")
        return [TextContent(type="text", text=result_text)]

    else:
        return [
            TextContent(
                type="text",
                text=f"❌ Unknown action: {action}. Use 'list', 'search', 'get', or 'customize'",
            )
        ]
