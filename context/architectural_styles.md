# Architectural Styles Guide

How to build in different architectural styles in Minecraft. Each style includes key features, material palettes, proportions, and building techniques.

---

## Medieval European

### Characteristics
- **Stone bases** with timber framing upper floors
- **Steep pitched roofs** (45-60 degrees)
- **Small windows** with wooden shutters
- **Asymmetrical layouts** (organic growth)
- **Overhanging upper floors** (jettying)

### Material Palette
| Element | Primary | Secondary | Accent |
|---------|---------|-----------|--------|
| Foundation | `cobblestone` | `stone_bricks` | `mossy_cobblestone` |
| Walls | `oak_planks` | `spruce_planks` | `stripped_oak_log` |
| Timber Frame | `dark_oak_log` | `stripped_dark_oak_log` | - |
| Roof | `dark_oak_stairs` | `spruce_stairs` | `cobblestone_slab` |
| Floor | `oak_planks` | `spruce_planks` | `cobblestone` |

### Key Features
```
TIMBER FRAMING:
- Horizontal beams at floor levels
- Vertical posts at corners and every 3-4 blocks
- Diagonal braces in large panels
- Use stripped_dark_oak_log for contrast

ROOF:
- 45-60 degree pitch (1:1 rise/run)
- Dormers for upper floors
- Overhang 1-2 blocks past walls
- Mix dark_oak_stairs with spruce_stairs

WINDOWS:
- 1-2 blocks tall
- Trapdoor shutters
- No glass or only glass_pane
- Flower boxes below (slabs + potted flowers)

CHIMNEYS:
- Cobblestone or brick
- 2x2 or 3x3 base
- Extend 2-3 blocks above roof peak
```

### Example Structure
```
Ground floor: Cobblestone walls, oak door, small windows
Second floor: Timber frame with plaster (white_concrete), overhang 1 block
Roof: Steep dark_oak_stairs, stone chimney
Details: Lanterns, flower boxes, hay bales
```

---

## Gothic

### Characteristics
- **Vertical emphasis** - Tall and narrow
- **Pointed arches** - Signature element
- **Flying buttresses** - External supports
- **Large windows** - Stained glass
- **Towers and spires** - Reaching skyward

### Material Palette
| Element | Primary | Secondary | Accent |
|---------|---------|-----------|--------|
| Walls | `stone_bricks` | `smooth_stone` | `chiseled_stone_bricks` |
| Arches | `stone_brick_stairs` | `polished_andesite_stairs` | - |
| Windows | `black_stained_glass_pane` | colored glass | `iron_bars` |
| Roof | `gray_concrete` | `stone_brick_slab` | `oxidized_copper` |
| Floor | `polished_andesite` | `stone_bricks` | `polished_diorite` |

### Key Features
```
POINTED ARCHES:
- Two intersecting arcs creating a point at top
- Build with stairs: north stairs + south stairs meeting at center
- Width should be odd (3, 5, 7 blocks)

FLYING BUTTRESSES:
- Angled stone supports from ground to upper walls
- Use stairs and slabs for diagonal effect
- Place every 5-8 blocks along walls

ROSE WINDOWS:
- Circular stained glass above main entrance
- 5-9 blocks diameter
- Radiating pattern using colored glass_pane

TOWERS & SPIRES:
- Octagonal or square bases
- Transition to pointed tops using stairs
- Height 2-3x base width
- Crockets (small projecting ornaments)

RIBBED VAULTING (Interior):
- Crossed diagonal ribs on ceiling
- Use stone_brick_wall for ribs
- Fill between with stone_brick_slab
```

### Proportions
- Wall height: 3x wall width minimum
- Window height: 60-70% of wall height
- Tower height: 2-3x building height
- Arch width: 1/3 to 1/2 of wall width

---

## Japanese Traditional

### Characteristics
- **Low-pitched roofs** with curved edges
- **Wood and paper** materials
- **Sliding doors** (shoji screens)
- **Elevated floors** on posts
- **Minimal decoration** - Zen simplicity
- **Integration with nature**

### Material Palette
| Element | Primary | Secondary | Accent |
|---------|---------|-----------|--------|
| Structure | `dark_oak_log` | `stripped_dark_oak_log` | `bamboo_block` |
| Walls | `white_concrete` | `birch_planks` | `paper` (white banners) |
| Roof | `dark_oak_stairs` | `deepslate_tile_stairs` | `crimson_stairs` |
| Floor | `birch_planks` | `bamboo_mosaic` | - |
| Accents | `cherry_log` | `cherry_leaves` | `lantern` |

### Key Features
```
ROOFS:
- Low pitch (2:3 rise/run, about 34 degrees)
- Curved edges using slabs
- Multi-tiered for temples (2-5 levels)
- Significant overhang (2-3 blocks)
- Exposed rafters underneath

SLIDING DOORS (SHOJI):
- White banner or white carpet as paper
- Dark oak frame
- 2-3 blocks wide openings

ENGAWA (VERANDA):
- Raised platform around building
- Birch planks or bamboo_mosaic
- Dark oak fence as railing

TORII GATES:
- Two vertical posts
- Two horizontal beams (lower straight, upper curved)
- Red concrete or crimson blocks
- Place at path entrances

STONE GARDENS:
- Gravel (white concrete powder)
- Large rocks (andesite, diorite boulders)
- Raked patterns (lines in gravel)
- Minimal plants
```

### Proportions
- Raised 1-2 blocks off ground
- Ceiling height: 3-4 blocks
- Veranda width: 2-3 blocks
- Roof overhang: 2-3 blocks past walls

---

## Modern/Contemporary

### Characteristics
- **Flat or low-pitched roofs**
- **Large glass walls**
- **Clean geometric forms**
- **Open floor plans**
- **Minimal ornamentation**
- **Integration of indoor/outdoor**

### Material Palette
| Element | Primary | Secondary | Accent |
|---------|---------|-----------|--------|
| Structure | `white_concrete` | `gray_concrete` | `black_concrete` |
| Glass | `glass` | `tinted_glass` | `glass_pane` |
| Metal | `iron_block` | `light_gray_concrete` | `chain` |
| Wood | `stripped_birch_log` | `birch_planks` | `bamboo_planks` |
| Floor | `polished_deepslate` | `smooth_quartz` | `white_concrete` |

### Key Features
```
WALLS:
- Large uninterrupted surfaces
- Floor-to-ceiling glass panels
- Cantilevered sections
- Contrasting colors in blocks

ROOFS:
- Flat with slight hidden drainage
- Green roof (grass blocks on top)
- Rooftop terraces
- Minimal overhang or none

WINDOWS:
- Full-height glass walls
- Minimal frames (iron bars or none)
- Corner windows (glass meeting at corner)
- Clerestory windows (high ribbon windows)

POOLS & WATER:
- Infinity pool edges
- Reflecting pools
- Indoor-outdoor water features
- Glass pool walls

LANDSCAPING:
- Geometric planters
- Bamboo or single-species plants
- Gravel or concrete paths
- Minimal, curated vegetation
```

### Proportions
- Horizontal emphasis (width > height)
- Floor height: 4-5 blocks
- Glass ratio: 40-60% of facade
- Cantilevers: 3-5 blocks

---

## Castle/Fortress

### Characteristics
- **Thick walls** for defense
- **Towers at corners** and gates
- **Crenellations** (battlements)
- **Narrow arrow slits**
- **Gatehouse with portcullis**
- **Inner and outer walls**

### Material Palette
| Element | Primary | Secondary | Accent |
|---------|---------|-----------|--------|
| Walls | `stone_bricks` | `cobblestone` | `mossy_stone_bricks` |
| Towers | `stone_bricks` | `polished_andesite` | `cracked_stone_bricks` |
| Roofs | `dark_oak_stairs` | `stone_brick_slab` | `deepslate_slab` |
| Floors | `polished_andesite` | `stone_bricks` | `oak_planks` |
| Details | `stone_brick_wall` | `iron_bars` | `chain` |

### Key Features
```
WALLS:
- 3-5 blocks thick
- Battered base (wider at bottom)
- Walkway on top (2-3 blocks wide)
- Machicolations (overhanging parapets)

BATTLEMENTS (CRENELLATIONS):
- Alternating merlons and crenels
- Merlons: 2 high, 1 wide
- Crenels: 1 high, 1 wide (gaps)
- Pattern: MEME... or MMEMME...

TOWERS:
- Round or square
- 5-7 blocks diameter/width
- Extend above wall height
- Conical or flat roof with battlements
- Place at corners and every 15-20 blocks

GATEHOUSE:
- Twin towers flanking entrance
- Portcullis (iron bars or nether_brick_fence)
- Murder holes above passage
- Drawbridge (oak_planks + chains)

ARROW SLITS:
- 1 block wide, 2-3 high on inside
- Narrow to 1x1 on outside
- Angled for vision/protection
```

### Proportions
- Wall height: 6-10 blocks
- Tower height: 1.5-2x wall height
- Tower spacing: 15-25 blocks
- Wall thickness: 3-5 blocks

---

## Fantasy/Wizard Tower

### Characteristics
- **Tall cylindrical towers**
- **Spiraling elements**
- **Magical aesthetics**
- **Purple and blue accents**
- **Floating elements**
- **Crystals and enchantment themes**

### Material Palette
| Element | Primary | Secondary | Accent |
|---------|---------|-----------|--------|
| Structure | `stone_bricks` | `deepslate_bricks` | `purpur_block` |
| Roof | `purpur_stairs` | `prismarine_stairs` | `amethyst_block` |
| Magic | `crying_obsidian` | `end_stone_bricks` | `sea_lantern` |
| Windows | `purple_stained_glass` | `blue_stained_glass` | `magenta_stained_glass` |
| Details | `end_rod` | `lightning_rod` | `amethyst_cluster` |

### Key Features
```
TOWERS:
- Circular cross-section (use calculate_shape)
- 7-11 block diameter
- Slight taper upward
- Spiral staircase inside
- Multiple levels with balconies

ROOFS:
- Conical with steep pitch
- Witch hat style (wide brim)
- Spire at top with lightning_rod
- Floating ring around spire

MAGICAL ELEMENTS:
- Glowing crystals (amethyst_cluster, end_rod)
- Floating islands around tower
- Enchantment table rooms
- Portal circles (end portal frames)
- Star patterns on floors

SPIRAL STAIRS:
- Use stairs rotating around central column
- Landings every 4-5 blocks
- Windows at each landing
```

### Proportions
- Height: 3-5x base diameter
- Roof height: 1/3 of tower height
- Brim overhang: 2-3 blocks
- Levels: every 5-6 blocks

---

## Desert/Sandstone

### Characteristics
- **Flat roofs** with parapets
- **Thick walls** for insulation
- **Courtyards** for shade and cooling
- **Minimal windows** on exterior
- **Arched doorways**
- **Domes and minarets**

### Material Palette
| Element | Primary | Secondary | Accent |
|---------|---------|-----------|--------|
| Walls | `sandstone` | `smooth_sandstone` | `cut_sandstone` |
| Details | `chiseled_sandstone` | `red_sandstone` | `terracotta` |
| Roof | `sandstone_slab` | `terracotta` | `blue_terracotta` |
| Floor | `smooth_sandstone` | `sandstone_slab` | `red_sandstone` |
| Accents | `cyan_terracotta` | `blue_stained_glass` | `gold_block` |

### Key Features
```
WALLS:
- 2-3 blocks thick
- Minimal exterior openings
- Decorative patterns (cut_sandstone bands)
- Slight batter (wider at base)

ROOFS:
- Flat with parapet
- Domes (half-sphere using stairs/slabs)
- Accessible rooftops
- Decorative crenellations

COURTYARDS:
- Central open-air space
- Fountain in center
- Shaded colonnades around edges
- Trees and plants inside

ARCHES:
- Horseshoe arches (wider than tall)
- Pointed arches for doorways
- Mashrabiya screens (patterned walls)

MINARETS:
- Tall slender towers
- Octagonal or round
- Balconies at regular intervals
- Onion dome or pointed top
```

### Proportions
- Wall height: 4-6 blocks per floor
- Parapet height: 1-2 blocks
- Courtyard: 1/4 to 1/3 of total footprint
- Dome height: 1/2 of dome diameter

---

## Building Tips by Style

### Adding Authenticity

**Medieval:**
- Randomize materials (50% cobblestone, 30% mossy, 20% stone)
- Add vines and moss
- Uneven rooflines
- Attached animal pens

**Gothic:**
- Vertical lines everywhere
- Lots of detail and ornamentation
- Consistent pointed arch motif
- Gargoyles (armor stands or custom heads)

**Japanese:**
- Asymmetry in layout
- Nature integration (trees, ponds)
- Consistent color restraint
- Proper post-and-beam visible

**Modern:**
- Perfect geometric alignment
- Material consistency
- Lighting integration
- Landscape as extension of building

**Castle:**
- Weathering and damage
- Functional defensive elements
- Mixed old and new repairs
- Scale appropriate for defense

**Fantasy:**
- Break physics rules
- Glowing elements at night
- Particle effects if possible
- Color gradient up the tower

### Scale Guidelines

| Style | Floor Height | Room Width | Building Height |
|-------|--------------|------------|-----------------|
| Medieval | 3-4 | 4-8 | 6-12 |
| Gothic | 6-10 | 10-20 | 30-60 |
| Japanese | 3-4 | 8-12 | 6-10 |
| Modern | 4-5 | 8-15 | 8-20 |
| Castle | 5-8 | 6-15 | 15-40 |
| Fantasy | 5-6 | 5-9 | 20-50 |

---

## Quick Style Selection

**User wants rustic/cozy** → Medieval or Japanese
**User wants grand/impressive** → Gothic or Castle
**User wants clean/minimal** → Modern or Japanese
**User wants magical/whimsical** → Fantasy
**User wants desert/warm climate** → Desert/Sandstone
**User wants defensive/military** → Castle
**User wants spiritual/religious** → Gothic or Japanese temple
