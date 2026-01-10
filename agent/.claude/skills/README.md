# VibeCraft Skills

Agent Skills for Minecraft building with VibeCraft MCP tools. Claude Code automatically loads these skills when relevant tasks are detected.

## Available Skills

| Skill | Lines | Triggers | Description |
|-------|-------|----------|-------------|
| **building-structures** | 66+43 | "build house", "castle", "cottage" | Floor placement, walls, roofs, architectural styles |
| **building-redstone** | 106+65+128 | "redstone", "circuit", "farm" | Logic gates, memory, timing, farms |
| **generating-terrain** | 92 | "terrain", "mountains", "hills" | Procedural landscapes, biome texturing |
| **placing-furniture** | 97 | "furniture", "interior", "decorate" | Spatial scanning, room layouts |
| **choosing-materials** | 66 | "palette", "materials", "colors" | 60-30-10 rule, 10 palettes |
| **using-worldedit** | 134 | "worldedit", "//set", "//replace" | Commands, patterns, masks, expressions |
| **creating-shapes** | 139 | "sphere", "dome", "pyramid" | build() code, shape formulas |

**Total**: ~936 lines (compressed from ~2,500 lines - 63% reduction)

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

## Compression Stats

| File | Before | After | Reduction |
|------|--------|-------|-----------|
| building-redstone/SKILL.md | 245 | 106 | 57% |
| building-redstone/gates.md | 170 | 65 | 62% |
| building-redstone/farms.md | 229 | 128 | 44% |
| building-structures/styles.md | 218 | 43 | 80% |
| choosing-materials/SKILL.md | 256 | 66 | 74% |
| creating-shapes/SKILL.md | 347 | 139 | 60% |
| generating-terrain/SKILL.md | 277 | 92 | 67% |
| placing-furniture/SKILL.md | 331 | 97 | 71% |
| using-worldedit/SKILL.md | 320 | 134 | 58% |
| SYSTEM_PROMPT.md | 1529 | 200 | 87% |

**Total prompt reduction**: ~3,900 lines → ~1,100 lines (72% reduction)
