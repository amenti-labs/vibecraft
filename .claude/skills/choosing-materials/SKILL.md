---
name: choosing-materials
description: Chooses Minecraft block materials, color palettes, and textures using VibeCraft MCP tools. Use when selecting materials for builds, creating color schemes, matching architectural styles, or asking about block combinations and palettes.
---

# Choosing Materials

Select professional block palettes using VibeCraft MCP tools.

## MCP Tools

- `search_minecraft_item(query)` - Search 1,375 blocks by name
- `buildscript_palettes` - 10 curated material palettes

## The 60-30-10 Rule

Professional builds use three material tiers:

| Tier | Percentage | Use |
|------|------------|-----|
| **Primary** | 60% | Walls, main surfaces |
| **Secondary** | 30% | Roof, accents, trim |
| **Detail** | 10% | Decorations, contrast |

**Example:**
```
Stone Castle:
- 60% stone_bricks (walls)
- 30% deepslate_bricks (roof, towers)
- 10% polished_andesite (trim, windows)
```

## Curated Palettes

### Medieval Oak
```
Primary:   oak_planks
Secondary: cobblestone
Accent:    stripped_oak_log
Roof:      dark_oak_stairs
Details:   oak_fence, lantern
```

### Stone Castle
```
Primary:   stone_bricks
Secondary: cobblestone
Accent:    polished_andesite
Roof:      deepslate_tile_stairs
Details:   iron_bars, chains
```

### Modern
```
Primary:   white_concrete
Secondary: light_gray_concrete
Accent:    black_concrete
Windows:   glass_pane
Details:   iron_bars, sea_lantern
```

### Japanese
```
Primary:   spruce_planks
Secondary: white_wool (shoji)
Accent:    dark_oak_log
Roof:      deepslate_tile_stairs
Details:   bamboo, lantern
```

### Gothic
```
Primary:   deepslate_bricks
Secondary: stone_bricks
Accent:    polished_blackstone
Windows:   black_stained_glass
Details:   chains, soul_lantern
```

### Desert
```
Primary:   smooth_sandstone
Secondary: cut_sandstone
Accent:    orange_terracotta
Roof:      sandstone_stairs
Details:   terracotta patterns
```

### Fantasy
```
Primary:   prismarine_bricks
Secondary: purpur_block
Accent:    amethyst_block
Lighting:  end_rod, sea_lantern
Details:   crying_obsidian
```

### Nether
```
Primary:   blackstone
Secondary: nether_bricks
Accent:    crimson_planks
Lighting:  shroomlight, soul_lantern
Details:   chains, gilded_blackstone
```

### Rustic
```
Primary:   spruce_planks
Secondary: cobblestone
Accent:    stripped_spruce_log
Roof:      spruce_stairs
Details:   barrel, lantern
```

### Cherry Blossom
```
Primary:   cherry_planks
Secondary: pink_terracotta
Accent:    stripped_cherry_log
Roof:      cherry_stairs
Details:   cherry_leaves, lantern
```

## Color Relationships

### Complementary (High Contrast)
```
Orange + Blue:    terracotta + prismarine
Red + Cyan:       red_nether_brick + warped_planks
Yellow + Purple:  gold_block + purpur_block
```

### Analogous (Harmonious)
```
Warm:   oak → spruce → dark_oak
Cool:   prismarine → diamond → lapis
Neutral: stone → andesite → cobblestone
```

### Monochromatic
```
Gray:   white_concrete → light_gray → gray → black
Brown:  birch_planks → oak → spruce → dark_oak
Stone:  smooth_stone → stone → cobblestone → mossy
```

## Material Properties

### Wood Types
| Wood | Tone | Best For |
|------|------|----------|
| Oak | Warm yellow | Generic, medieval |
| Spruce | Dark brown | Rustic, cabin |
| Birch | Light cream | Modern, light |
| Dark Oak | Deep brown | Medieval, dramatic |
| Jungle | Red-brown | Tropical |
| Acacia | Orange | Desert, savanna |
| Cherry | Pink | Japanese, fantasy |
| Mangrove | Red | Swamp |

### Stone Types
| Stone | Tone | Best For |
|-------|------|----------|
| Stone bricks | Gray | Castle, fortress |
| Cobblestone | Dark gray | Rustic, path |
| Andesite | Light gray | Modern, clean |
| Granite | Pink-gray | Warm builds |
| Diorite | White-gray | Light accents |
| Deepslate | Dark blue-gray | Gothic, dungeon |
| Blackstone | Black | Nether, dark |

### Concrete Colors
```
White, Light Gray, Gray, Black
Brown, Red, Orange, Yellow
Lime, Green, Cyan, Light Blue
Blue, Purple, Magenta, Pink
```

## Texture Considerations

### Smooth vs Rough
```
Smooth (formal): quartz, concrete, smooth_stone
Rough (rustic):  cobblestone, stone, mossy variants
```

### Weathering
```
New:      stone_bricks, oak_planks
Aged:     cracked_stone_bricks, mossy variants
Ancient:  infested variants, cobblestone
```

### Repetition
Large surfaces need variety:
```
# Instead of:
//set stone_bricks

# Use pattern:
//set 80%stone_bricks,15%cracked_stone_bricks,5%mossy_stone_bricks
```

## Block Search

Find blocks by name:
```python
# Search for all oak blocks
search_minecraft_item(query="oak")

# Search for stairs
search_minecraft_item(query="stairs")

# Search by color
search_minecraft_item(query="blue")
```

## Common Mistakes

### Too Many Materials
```
❌ 5+ different materials = chaotic
✅ 3-4 materials max = cohesive
```

### No Contrast
```
❌ Oak planks + oak stairs + oak fence
✅ Oak planks + cobblestone corners + dark_oak trim
```

### Clashing Colors
```
❌ Orange terracotta + cyan terracotta (jarring)
✅ Orange terracotta + brown terracotta (harmonious)
```

### Ignoring Scale
```
Small build: 2-3 materials
Medium build: 3-4 materials
Large build: 4-5 materials (with clear hierarchy)
```

## Quick Reference

| Style | Primary | Roof | Trim |
|-------|---------|------|------|
| Cottage | Oak planks | Dark oak stairs | Cobblestone |
| Castle | Stone bricks | Deepslate tiles | Andesite |
| Modern | White concrete | Flat/quartz | Iron bars |
| Japanese | Spruce | Deepslate tiles | Dark oak |
| Desert | Sandstone | Terracotta | Cut sandstone |
| Gothic | Deepslate bricks | Deepslate tiles | Blackstone |
