# VibeCraft Skills

Agent Skills for Minecraft building with VibeCraft MCP tools. Claude Code automatically loads these skills when relevant tasks are detected.

## Available Skills

| Skill | Triggers | Description |
|-------|----------|-------------|
| **building-structures** | "build house", "castle", "cottage" | Architectural structures with proper floor placement, walls, roofs |
| **building-redstone** | "redstone", "circuit", "farm" | Logic gates, memory circuits, automation, contraptions |
| **generating-terrain** | "terrain", "mountains", "hills" | Procedural landscapes, terrain texturing |
| **placing-furniture** | "furniture", "interior", "decorate" | Room layouts, furniture placement, interior design |
| **choosing-materials** | "palette", "materials", "colors" | Block selection, color theory, style palettes |
| **using-worldedit** | "worldedit", "//set", "//replace" | WorldEdit commands, patterns, masks, expressions |
| **creating-shapes** | "sphere", "dome", "pyramid" | Procedural geometry, organic shapes, complex forms |

## How Skills Work

1. **Discovery**: Claude reads skill names and descriptions at startup
2. **Activation**: When your request matches a skill's description, Claude loads it
3. **Execution**: Claude follows the skill's instructions and uses MCP tools

## Skill Structure

```
skill-name/
├── SKILL.md        # Required - main instructions
├── reference.md    # Optional - detailed docs
└── scripts/        # Optional - utility scripts
```

## Using Skills

Skills are automatic. Just describe what you want:

```
"Build a medieval castle"     → building-structures skill
"Create a redstone door"      → building-redstone skill
"Generate mountain terrain"   → generating-terrain skill
"Furnish the bedroom"         → placing-furniture skill
"Choose materials for gothic" → choosing-materials skill
```

## MCP Tools Available

All skills have access to VibeCraft's 46 MCP tools:

- **Location**: `get_player_position`, `get_surface_level`
- **WorldEdit**: `worldedit_selection`, `worldedit_region`, `worldedit_generation`
- **Building**: `build()`, `building_template`, `place_building_pattern`
- **Furniture**: `furniture_lookup`, `place_furniture`
- **Terrain**: `generate_terrain`, `texture_terrain`, `smooth_terrain`
- **Analysis**: `spatial_awareness_scan`, `search_minecraft_item`

## Creating New Skills

1. Create directory: `.claude/skills/my-skill/`
2. Create `SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill
description: What it does and when to use it
---

# Instructions here
```

3. Skills are auto-discovered by Claude Code

## Best Practices

- **Concise**: Keep SKILL.md under 500 lines
- **Task-oriented**: Skills should do things, not just describe topics
- **Progressive disclosure**: Put detailed docs in reference files
- **MCP-aware**: Reference VibeCraft tools in instructions
