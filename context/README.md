# VibeCraft Context Files

Essential data files for AI-powered Minecraft building.

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

## Reference Files (Not Loaded, Used as Context)

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

---

## File Organization

**Total files**: 10 (down from 18!)
- **Production**: 7 JSON files loaded by Python code
- **Reference**: 2 files used as AI context
- **Documentation**: 1 README

**Total size**: ~435KB

---

## How These Files Are Used

### By Production Code
The 7 production JSON files are loaded at server startup by `server.py` and `tools/*.py`:
- Item search tool loads minecraft_items_filtered.json
- Furniture tools load furniture layouts + catalog
- Pattern tools load patterns (building + terrain)
- Template tool loads building templates

### By AI Assistant
The 2 reference files are read on-demand when planning builds:
- Scale reference for proper room dimensions
- Recipe book for WorldEdit command sequences

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
- Used for recipe book
- Human and AI readable
- Standard formatting

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

---

**Clean, organized, and every file has a purpose!** ✨
