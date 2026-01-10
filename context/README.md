# VibeCraft Context Files

Essential data files and reference guides for AI-powered Minecraft building.

---

## Production Data Files (Loaded by Code)

### minecraft_items_filtered.json
- **Size**: 2,565 items from Minecraft 1.21.11 (138KB)
- **Purpose**: Powers the `search_minecraft_item` MCP tool
- **Used by**: `server.py` - load_minecraft_items()
- **Format**: JSON with id, name, displayName

### minecraft_furniture_layouts.json
- **Size**: 7 furniture pieces with precise coordinates (78KB)
- **Purpose**: Automated furniture placement with WorldEdit
- **Used by**: `server.py` - load_furniture_layouts()
- **Format**: Structured JSON with bounds, placements, materials, clearance
- **Includes**: Simple dining table, corner table, wall cabinet, chair, floor lamp, coffee table, closet

### minecraft_furniture_catalog.json
- **Size**: 60+ furniture designs (115KB)
- **Purpose**: Text-based build instructions for manual furniture construction
- **Used by**: `server.py` - load_furniture_catalog()
- **Format**: JSON with descriptions, content blocks, dimensions
- **Note**: Combines with layouts - 7 automated, 55+ manual instructions

### building_patterns_structured.json
- **Size**: 4 architectural patterns (2.4KB)
- **Purpose**: Automated pattern placement via `place_building_pattern`
- **Used by**: `server.py` - load_structured_patterns()
- **Format**: JSON with palette + layer grids
- **Includes**: Simple stone pillar, 2×2 window, single door, small brick chimney

### building_patterns_complete.json
- **Size**: 29 building patterns (22KB)
- **Purpose**: Pattern metadata for search and discovery
- **Used by**: `tools/patterns.py` - building_pattern_lookup()
- **Format**: JSON with metadata, dimensions, materials, construction notes
- **Categories**: Roofing (18), facades (3), corners (3), details (5)

### terrain_patterns_complete.json
- **Size**: 41 terrain patterns (34KB)
- **Purpose**: Terrain pattern search and discovery
- **Used by**: `tools/patterns.py` - terrain_pattern_lookup()
- **Format**: JSON with metadata, dimensions, construction notes
- **Categories**: Vegetation (24), features (7), paths (4), details (6)

### building_templates.json
- **Size**: 5 parametric building templates (24KB)
- **Purpose**: Fully customizable building templates (height, size, materials)
- **Used by**: `tools/core_tools.py` - building_template()
- **Format**: JSON with parameters, defaults, build sequences
- **Includes**: Medieval round tower, simple cottage, guard tower, wizard tower, simple barn

---

## Reference Guides (AI Context)

### minecraft_scale_reference.md
- **Size**: 15KB
- **Format**: TOON (Token-Oriented Object Notation)
- **Purpose**: Architectural dimensions for realistic builds
- **Content**: Player dimensions, room sizes, furniture dimensions, spacing guidelines, ceiling heights, best practices
- **Usage**: AI reads when planning builds for proper proportions

### worldedit_recipe_book.md
- **Size**: 6.4KB
- **Format**: Markdown
- **Purpose**: Ready-made WorldEdit command sequences
- **Content**: Structure recipes, terrain recipes, brush recipes, snapshot recipes
- **Usage**: Quick reference for common WorldEdit operations

### worldedit_expression_guide.md
- **Size**: ~20KB
- **Format**: Markdown
- **Purpose**: Complete //generate and //deform expression syntax
- **Content**: 
  - All operators, functions, and constants
  - 30+ shape formulas (sphere, torus, helix, heart, etc.)
  - Noise functions (perlin, voronoi, ridgedmulti)
  - Deformation expressions for twists, bulges, waves
  - Expression masks for advanced filtering
- **Usage**: Creating procedural shapes and organic terrain

### minecraft_commands_reference.md
- **Size**: ~15KB
- **Format**: Markdown
- **Purpose**: Vanilla Minecraft commands beyond WorldEdit
- **Content**:
  - /setblock with all block states
  - /fill modes (hollow, outline, replace)
  - /clone for copying regions
  - /execute for conditional building
  - /data for NBT manipulation
  - /structure for templates
  - Complete block state reference
- **Usage**: Precision work where WorldEdit isn't needed

### architectural_styles.md
- **Size**: ~20KB
- **Format**: Markdown
- **Purpose**: Building strategies by architectural style
- **Content**:
  - Medieval European (timber framing, steep roofs)
  - Gothic (pointed arches, flying buttresses)
  - Japanese Traditional (low roofs, sliding doors)
  - Modern/Contemporary (flat roofs, large glass)
  - Castle/Fortress (walls, towers, battlements)
  - Fantasy/Wizard (cylindrical towers, magical elements)
  - Desert/Sandstone (domes, courtyards)
  - Proportions and scale guidelines per style
- **Usage**: Building in specific architectural styles

### block_palette_guide.md
- **Size**: ~15KB
- **Format**: Markdown
- **Purpose**: Color theory and material combinations
- **Content**:
  - 60-30-10 rule for material distribution
  - Color wheel relationships in Minecraft
  - 15+ curated palettes (castle, medieval, modern, etc.)
  - Gradient techniques
  - Contrast principles
  - Common mistakes to avoid
- **Usage**: Choosing materials for professional-looking builds

### voxel_generation_guide.md
- **Size**: ~8KB
- **Format**: Markdown
- **Purpose**: Procedural voxel generation with build() tool
- **Content**: Code patterns for spheres, curves, organic shapes
- **Usage**: Complex procedural builds using code generation

### redstone_contraptions.md
- **Size**: ~25KB
- **Format**: Markdown
- **Purpose**: Complete redstone mechanism reference
- **Content**:
  - Logic gates (NOT, OR, AND, NAND, XOR, NOR)
  - Memory circuits (RS latch, T flip-flop, D flip-flop, counters)
  - Timing circuits (clocks, pulse extenders/limiters, edge detectors)
  - Piston contraptions (doors, extenders, flying machines)
  - Automatic farms (sugar cane, pumpkin, chicken, iron)
  - Traps (arrow, lava, TNT, pitfall)
  - Advanced (combination locks, item sorters, elevators)
  - Block state reference for all redstone components
- **Usage**: Building redstone mechanisms and automation

### procedural_generation_guide.md
- **Size**: ~20KB
- **Format**: Markdown
- **Purpose**: Algorithms for procedural generation with build() tool
- **Content**:
  - Basic shapes (sphere, dome, cylinder, cone, pyramid, torus)
  - Organic shapes (trees, boulders, vines)
  - Terrain generation (hills, mountains, valleys)
  - Architectural algorithms (spiral stairs, arches, rose windows)
  - Pattern generation (checkerboard, gradient, radial, brick)
  - Complex structures (towers, bridges, spirals)
  - Performance tips and integration with WorldEdit
- **Usage**: Procedural/algorithmic building using code generation

---

## File Organization

**Total files**: 17
- **Production**: 7 JSON files loaded by Python code
- **Reference**: 9 markdown files used as AI context
- **Documentation**: 1 README

**Total size**: ~600KB

---

## How These Files Are Used

### By Production Code
The 7 production JSON files are loaded at server startup by `server.py` and `tools/*.py`:
- Item search tool loads minecraft_items_filtered.json
- Furniture tools load furniture layouts + catalog
- Pattern tools load patterns (building + terrain)
- Template tool loads building templates

### By AI Assistant
The 9 reference files are read on-demand when planning builds:
- **Scale reference** — Proper room dimensions and proportions
- **Recipe book** — WorldEdit command sequences
- **Expression guide** — //generate formulas for shapes
- **Commands reference** — Vanilla /setblock and /fill workflows
- **Architectural styles** — Style-specific building strategies
- **Block palette guide** — Color and material combinations
- **Voxel generation** — Code-based procedural building
- **Redstone contraptions** — Logic gates, circuits, automation
- **Procedural generation** — Algorithms for shapes, terrain, structures

---

## File Formats

**JSON**: Machine-readable structured data
- Used for all production data files
- Loaded at server startup
- Fast access via Python dictionaries

**TOON**: Token-efficient human-readable format
- Used for scale reference (YAML-like)
- Optimized for AI context windows
- Easy to read and maintain

**Markdown**: Documentation format
- Used for all reference guides
- Human and AI readable
- Standard formatting with code examples

---

## Quick Reference by Task

| Task | Primary Reference | Secondary Reference |
|------|-------------------|---------------------|
| Building structure | minecraft_scale_reference.md | architectural_styles.md |
| Choosing materials | block_palette_guide.md | architectural_styles.md |
| Procedural shapes | procedural_generation_guide.md | worldedit_expression_guide.md |
| Precision placement | minecraft_commands_reference.md | worldedit_recipe_book.md |
| Furniture | minecraft_furniture_catalog.json | minecraft_scale_reference.md |
| Terrain | procedural_generation_guide.md | worldedit_expression_guide.md |
| Specific style | architectural_styles.md | block_palette_guide.md |
| Redstone circuits | redstone_contraptions.md | minecraft_commands_reference.md |
| Organic shapes | procedural_generation_guide.md | voxel_generation_guide.md |
| Automation/farms | redstone_contraptions.md | - |

---

## Maintenance

### Adding New Items
1. Update minecraft_items_filtered.json with new items
2. Update item count in this README

### Adding New Patterns
1. Add to building_patterns_complete.json (metadata)
2. If automated, add to building_patterns_structured.json (blueprint)
3. Update pattern count in this README

### Adding New Furniture
1. Add description to minecraft_furniture_catalog.json
2. If automated, add layout to minecraft_furniture_layouts.json
3. Update furniture count in this README

### Adding New Templates
1. Add to building_templates.json
2. Include parameters, defaults, and build_sequence
3. Update template count in this README

### Adding New Reference Guides
1. Create markdown file with clear structure
2. Add to this README with size, purpose, content summary
3. Update file counts and total size

---

**Comprehensive knowledge base for AI Minecraft building!** ✨
