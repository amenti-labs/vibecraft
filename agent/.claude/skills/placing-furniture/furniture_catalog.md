# Furniture Schematic Catalog

Complete catalog of furniture designs using the VibeCraft schematic format.
All designs use correct Minecraft block IDs and states.

## How to Use

Copy any schematic JSON and use with `build_schematic()`:

```python
build_schematic(
    schematic={...},  # Copy from catalog
    description="Dining table"
)
```

**Adjust anchor `"a"` to your placement location!**

---

## SEATING

### Simple Chair
Single stair block - most basic chair.
```json
{"a": [X, Y, Z], "p": {"C": "oak_stairs[facing=south]"}, "l": [[0, "C"]]}
```
Variations: Change `oak_stairs` to `spruce_stairs`, `birch_stairs`, `dark_oak_stairs`, etc.

### Armchair
Stair with sign armrests.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "oak_stairs[facing=south]",
    "L": "oak_wall_sign[facing=east]",
    "R": "oak_wall_sign[facing=west]"
  },
  "l": [[0, "L C R"]]
}
```

### Chair with Back (Trapdoor)
Stair seat with trapdoor backrest.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "oak_stairs[facing=south]",
    "B": "oak_trapdoor[facing=south,half=bottom,open=true]"
  },
  "l": [
    [0, ". C ."],
    [0, ". B ."]
  ]
}
```
Note: Place trapdoor on north side of stair, opened to form backrest.

### Dining Chair
Slab with sign back and sides.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "oak_slab[type=bottom]",
    "Bl": "oak_wall_sign[facing=east]",
    "Br": "oak_wall_sign[facing=west]",
    "Bb": "oak_wall_sign[facing=south]"
  },
  "l": [[0, "Bl S Br|. Bb ."]]
}
```

### Bench (2-wide)
Two stairs side by side.
```json
{"a": [X, Y, Z], "p": {"B": "oak_stairs[facing=south]"}, "l": [[0, "B B"]]}
```

### Bench (3-wide with Arms)
Three stairs with sign armrests.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "oak_stairs[facing=south]",
    "L": "oak_wall_sign[facing=east]",
    "R": "oak_wall_sign[facing=west]"
  },
  "l": [[0, "L B B B R"]]
}
```

### Stool
Single fence with pressure plate.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "P": "oak_pressure_plate"
  },
  "l": [
    [0, "F"],
    [1, "P"]
  ]
}
```

### Sofa (2-seat)
Two stairs with sign armrests.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "oak_stairs[facing=south]",
    "L": "oak_wall_sign[facing=east]",
    "R": "oak_wall_sign[facing=west]"
  },
  "l": [[0, "L S S R"]]
}
```

### Sofa (3-seat)
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "oak_stairs[facing=south]",
    "L": "oak_wall_sign[facing=east]",
    "R": "oak_wall_sign[facing=west]"
  },
  "l": [[0, "L S S S R"]]
}
```

### L-Shaped Sofa
Corner sofa with armrests.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Ss": "oak_stairs[facing=south]",
    "Se": "oak_stairs[facing=east]",
    "L": "oak_wall_sign[facing=east]",
    "R": "oak_wall_sign[facing=north]"
  },
  "l": [[0, "L Ss Ss Ss|. . . Se|. . . Se|. . . R"]]
}
```

### Throne
Grand chair with high back.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "oak_stairs[facing=south]",
    "P": "oak_planks",
    "L": "oak_stairs[facing=east]",
    "R": "oak_stairs[facing=west]"
  },
  "l": [
    [0, "L C R"],
    [1, "P . P"],
    [2, "P . P"]
  ]
}
```

### Dog/Pet Bed
Small cozy bed for pets.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "oak_slab[type=bottom]",
    "Lf": "oak_wall_sign[facing=south]",
    "Lb": "oak_wall_sign[facing=north]",
    "Ll": "oak_wall_sign[facing=east]",
    "Lr": "oak_wall_sign[facing=west]"
  },
  "l": [[0, "Ll S S Lr|Lf . . Lf|Lb . . Lb"]]
}
```

---

## TABLES

### Simple Table (Fence Legs)
Classic table with fence post legs.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "P": "oak_pressure_plate"
  },
  "l": [
    [0, "F . F"],
    [1, "P P P"]
  ]
}
```

### Coffee Table
Low table with slab top.
```json
{
  "a": [X, Y, Z],
  "p": {"S": "oak_slab[type=bottom]"},
  "l": [[0, "S S"]]
}
```

### Coffee Table (with Carpet)
Slab table with carpet decoration.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "oak_slab[type=bottom]",
    "C": "brown_carpet"
  },
  "l": [
    [0, "S S"],
    [0, "C C"]
  ]
}
```

### Corner Table
Single fence with decorative top.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "P": "oak_pressure_plate"
  },
  "l": [
    [0, "F"],
    [1, "P"]
  ]
}
```

### Dining Table (2x3)
Rectangular table for dining room.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "S": "oak_slab[type=bottom]"
  },
  "l": [
    [0, "F . F|. . .|F . F"],
    [1, "S S S|S S S|S S S"]
  ]
}
```

### Dining Table (Stairs Method)
Upside-down stairs as table legs.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Le": "oak_stairs[facing=east,half=top]",
    "Lw": "oak_stairs[facing=west,half=top]",
    "S": "oak_slab[type=top]"
  },
  "l": [[0, "Le S S Lw"]]
}
```

### Round Table (5x5)
Circular table approximation.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "S": "oak_slab[type=bottom]"
  },
  "l": [
    [0, ". F . F .|F . . . F|. . F . .|F . . . F|. F . F ."],
    [1, ". S S S .|S S S S S|S S S S S|S S S S S|. S S S ."]
  ]
}
```

### Kitchen Counter
Counter with storage underneath.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "barrel[facing=up]",
    "S": "smooth_stone_slab[type=bottom]"
  },
  "l": [
    [0, "B B B"],
    [1, "S S S"]
  ]
}
```

### Desk (Simple)
Work desk with drawers underneath.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "C": "chest[facing=south]",
    "S": "oak_slab[type=bottom]"
  },
  "l": [
    [0, "F . C"],
    [1, "S S S"]
  ]
}
```

### Desk (Piston Style)
Modern desk using pistons.
```json
{
  "a": [X, Y, Z],
  "p": {"P": "piston[facing=up,extended=true]"},
  "l": [[0, "P P P"]]
}
```
Note: Requires redstone block beneath each piston.

### Long Dining Table (with Dishware)
Table set for dinner.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "S": "oak_slab[type=bottom]",
    "Pl": "stone_pressure_plate",
    "Cp": "flower_pot"
  },
  "l": [
    [0, "F . . . . F|. . . . . .|. . . . . .|F . . . . F"],
    [1, "S S S S S S|S S S S S S|S S S S S S|S S S S S S"],
    [1, "Pl . . . . Pl|. . Cp . . .|. . . Cp . .|Pl . . . . Pl"]
  ]
}
```

---

## BEDROOM

### Bed (Standard Minecraft)
Use actual bed blocks.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Bf": "red_bed[facing=south,part=foot]",
    "Bh": "red_bed[facing=south,part=head]"
  },
  "l": [[0, "Bf|Bh"]]
}
```
Colors: `white_bed`, `orange_bed`, `magenta_bed`, `light_blue_bed`, `yellow_bed`, `lime_bed`, `pink_bed`, `gray_bed`, `light_gray_bed`, `cyan_bed`, `purple_bed`, `blue_bed`, `brown_bed`, `green_bed`, `red_bed`, `black_bed`

### Nightstand
Bedside table with lamp.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "barrel[facing=up]",
    "L": "lantern"
  },
  "l": [
    [0, "B"],
    [1, "L"]
  ]
}
```

### Nightstand (with Drawer)
Bedside table using chest.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "chest[facing=south]",
    "T": "oak_trapdoor[facing=south,half=top,open=false]"
  },
  "l": [
    [0, "C"],
    [1, "T"]
  ]
}
```

### Wardrobe / Closet
Tall storage cabinet.
```json
{
  "a": [X, Y, Z],
  "p": {
    "P": "oak_planks",
    "Dl": "oak_door[facing=south,half=lower,hinge=left]",
    "Du": "oak_door[facing=south,half=upper,hinge=left]",
    "Dr": "oak_door[facing=south,half=lower,hinge=right]",
    "Dur": "oak_door[facing=south,half=upper,hinge=right]"
  },
  "l": [
    [0, "P P"],
    [1, "Dl Dr"],
    [2, "Du Dur"],
    [3, "P P"]
  ]
}
```

### Dresser (Functional)
Double chest storage.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Cl": "chest[facing=south,type=left]",
    "Cr": "chest[facing=south,type=right]"
  },
  "l": [
    [0, "Cl Cr"],
    [1, "Cl Cr"]
  ]
}
```

### Dresser (Decorative)
Wooden block with trapdoor handles.
```json
{
  "a": [X, Y, Z],
  "p": {
    "P": "oak_planks",
    "T": "oak_trapdoor[facing=south,half=bottom,open=true]"
  },
  "l": [
    [0, "P P|T T"],
    [1, "P P|T T"]
  ]
}
```

### Vanity / Mirror
Dresser with mirror above.
```json
{
  "a": [X, Y, Z],
  "p": {
    "P": "oak_planks",
    "T": "oak_trapdoor[facing=south,half=bottom,open=true]",
    "G": "glass_pane"
  },
  "l": [
    [0, "P P|T T"],
    [1, "G G"]
  ]
}
```

### Bunk Bed
Stacked beds with ladder.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "P": "oak_planks",
    "Bf": "red_bed[facing=south,part=foot]",
    "Bh": "red_bed[facing=south,part=head]",
    "L": "ladder[facing=east]"
  },
  "l": [
    [0, "F . F|Bf . .|Bh . ."],
    [1, "F . F|. . .|. . ."],
    [2, "F . F|. . .|. . ."],
    [3, "F P F|Bf . L|Bh . L"]
  ]
}
```

---

## STORAGE

### Bookshelf Wall (3x3)
Decorative bookshelf arrangement.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "bookshelf",
    "P": "oak_planks"
  },
  "l": [
    [0, "B B B"],
    [1, "B P B"],
    [2, "B B B"]
  ]
}
```

### Cabinet (Wall)
Wall-mounted cabinet with door.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "barrel[facing=south]",
    "T": "oak_trapdoor[facing=south,half=bottom,open=false]"
  },
  "l": [[0, "B|T"]]
}
```

### Cupboard (Bookshelf Style)
Cabinet using bookshelf block.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "bookshelf",
    "T": "oak_trapdoor[facing=south,half=bottom,open=false]"
  },
  "l": [[0, "B|T"]]
}
```

### Cupboard (Stairs)
U-shaped storage using stairs.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Se": "oak_stairs[facing=east,half=bottom]",
    "Sw": "oak_stairs[facing=west,half=bottom]",
    "Te": "oak_trapdoor[facing=east,half=bottom,open=false]",
    "Tw": "oak_trapdoor[facing=west,half=bottom,open=false]"
  },
  "l": [[0, "Se Sw|Te Tw"]]
}
```

### Display Shelf
Trapdoor shelf on wall.
```json
{
  "a": [X, Y, Z],
  "p": {"T": "oak_trapdoor[facing=south,half=bottom,open=true]"},
  "l": [[0, "T T T"]]
}
```

### Barrel Storage Rack
Horizontal barrels for storage.
```json
{
  "a": [X, Y, Z],
  "p": {"B": "barrel[facing=south]"},
  "l": [
    [0, "B B B"],
    [1, "B B B"]
  ]
}
```

---

## LIGHTING

### Floor Lamp (Fence Post)
Simple standing lamp.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "L": "lantern"
  },
  "l": [
    [0, "F"],
    [1, "F"],
    [2, "L"]
  ]
}
```

### Floor Lamp (Tall)
Tall standing lamp with torchlight.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "T": "torch"
  },
  "l": [
    [0, "F"],
    [1, "F"],
    [2, "F"],
    [3, "T"]
  ]
}
```

### Table Lamp (Trapdoor Shade)
Lamp with decorative shade.
```json
{
  "a": [X, Y, Z],
  "p": {
    "L": "glowstone",
    "Tn": "oak_trapdoor[facing=north,half=bottom,open=true]",
    "Ts": "oak_trapdoor[facing=south,half=bottom,open=true]",
    "Te": "oak_trapdoor[facing=east,half=bottom,open=true]",
    "Tw": "oak_trapdoor[facing=west,half=bottom,open=true]"
  },
  "l": [[0, ". Tn .|Tw L Te|. Ts ."]]
}
```

### Ceiling Lamp (Hanging)
Lantern hanging from chain.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "chain",
    "L": "lantern[hanging=true]"
  },
  "l": [
    [0, "C"],
    [-1, "L"]
  ]
}
```
Note: Attach chain to ceiling, lantern hangs below. Y=0 is ceiling level.

### Chandelier (Small)
3-light chandelier.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "chain",
    "F": "oak_fence",
    "L": "lantern[hanging=true]"
  },
  "l": [
    [0, ". C ."],
    [-1, "L F L"],
    [-2, ". L ."]
  ]
}
```

### Chandelier (Large)
5-light grand chandelier.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "chain",
    "F": "oak_fence",
    "L": "lantern[hanging=true]"
  },
  "l": [
    [0, ". . C . ."],
    [-1, ". . C . ."],
    [-2, "L F F F L"],
    [-3, ". L . L ."]
  ]
}
```

### Wall Sconce (Torch)
Simple wall-mounted light.
```json
{"a": [X, Y, Z], "p": {"T": "wall_torch[facing=south]"}, "l": [[0, "T"]]}
```
Facing options: `north`, `south`, `east`, `west` (direction torch points)

### Wall Sconce (Lantern)
Fancy wall light with bracket.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "L": "lantern[hanging=true]"
  },
  "l": [
    [0, "F|L"]
  ]
}
```

### Hidden Light (Under Carpet)
Light source hidden beneath carpet.
```json
{
  "a": [X, Y, Z],
  "p": {
    "G": "glowstone",
    "C": "white_carpet"
  },
  "l": [
    [-1, "G"],
    [0, "C"]
  ]
}
```
Note: Place in floor. Light passes through carpet.

### Lava Lamp
Decorative lava display (creative/careful).
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "stone",
    "G": "glass",
    "L": "lava"
  },
  "l": [
    [0, "S G S|G L G|S G S"],
    [1, "S G S|G L G|S G S"],
    [2, "S S S|S S S|S S S"]
  ]
}
```

### Modern Lamp (Sea Lantern)
Clean modern light fixture.
```json
{
  "a": [X, Y, Z],
  "p": {
    "L": "sea_lantern",
    "Tn": "white_stained_glass_pane"
  },
  "l": [[0, "Tn L Tn"]]
}
```

---

## KITCHEN

### Sink (Cauldron)
Basic kitchen sink.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "cauldron",
    "L": "lever"
  },
  "l": [
    [0, "C"],
    [1, "L"]
  ]
}
```

### Sink (Hopper)
Modern sink with drain.
```json
{
  "a": [X, Y, Z],
  "p": {
    "H": "hopper[facing=down]",
    "L": "lever"
  },
  "l": [
    [0, "H"],
    [1, "L"]
  ]
}
```

### Stove (Furnace)
Basic cooking stove.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "furnace[facing=south]",
    "T": "oak_trapdoor[facing=south,half=top,open=false]"
  },
  "l": [
    [0, "F F|T T"]
  ]
}
```

### Stove (Smoker with Burners)
Cooking stove with detector rails as burners.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "smoker[facing=south]",
    "R": "detector_rail"
  },
  "l": [
    [0, "S S"],
    [1, "R R"]
  ]
}
```

### Kitchen Island
Central kitchen workspace.
```json
{
  "a": [X, Y, Z],
  "p": {
    "P": "polished_andesite",
    "B": "barrel[facing=up]",
    "S": "smooth_stone_slab[type=bottom]"
  },
  "l": [
    [0, "B P B"],
    [1, "S S S"]
  ]
}
```

### Refrigerator (Iron Door)
Functional fridge with dispenser.
```json
{
  "a": [X, Y, Z],
  "p": {
    "D": "dispenser[facing=south]",
    "I": "iron_block",
    "Dr": "iron_door[facing=south,half=lower,hinge=left]",
    "Du": "iron_door[facing=south,half=upper,hinge=left]",
    "B": "stone_button[face=wall,facing=south]"
  },
  "l": [
    [0, "D|Dr"],
    [1, "I|Du"],
    [2, ". B"]
  ]
}
```
Note: Button dispenses food from dispenser.

### Refrigerator (Simple)
Decorative fridge.
```json
{
  "a": [X, Y, Z],
  "p": {
    "I": "iron_block",
    "B": "stone_button[face=wall,facing=south]"
  },
  "l": [
    [0, "I"],
    [1, "I|B"]
  ]
}
```

### Cabinet (Upper)
Wall-mounted kitchen cabinet.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "barrel[facing=south]",
    "T": "spruce_trapdoor[facing=south,half=bottom,open=false]"
  },
  "l": [[0, "B B B|T T T"]]
}
```

### Counter with Sink
Kitchen counter section with sink.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "barrel[facing=up]",
    "S": "smooth_stone_slab[type=bottom]",
    "H": "hopper[facing=down]",
    "L": "lever"
  },
  "l": [
    [0, "B B B B B"],
    [1, "S S H S S|. . L . ."]
  ]
}
```

---

## BATHROOM

### Toilet (Hopper)
Basic toilet design.
```json
{
  "a": [X, Y, Z],
  "p": {
    "H": "hopper[facing=down]",
    "T": "oak_trapdoor[facing=south,half=top,open=false]",
    "L": "lever"
  },
  "l": [
    [0, "H"],
    [1, "T L"]
  ]
}
```

### Toilet (Cauldron)
Alternative toilet design.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "cauldron",
    "T": "iron_trapdoor[facing=south,half=top,open=false]",
    "B": "stone_button[face=wall,facing=east]"
  },
  "l": [
    [0, "C B"],
    [1, "T ."]
  ]
}
```

### Bathtub (Simple)
Basic bathtub.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Qn": "quartz_stairs[facing=north,half=bottom]",
    "Qs": "quartz_stairs[facing=south,half=bottom]",
    "Q": "quartz_block",
    "W": "water",
    "L": "lever"
  },
  "l": [
    [0, "Qn Q Qs"],
    [0, "W W W"],
    [1, ". L ."]
  ]
}
```

### Bathtub (Large)
Larger bathtub with steps.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Q": "quartz_block",
    "Qn": "quartz_stairs[facing=north,half=bottom]",
    "Qs": "quartz_stairs[facing=south,half=bottom]",
    "Qe": "quartz_stairs[facing=east,half=bottom]",
    "Qw": "quartz_stairs[facing=west,half=bottom]",
    "W": "water",
    "L": "lever"
  },
  "l": [
    [0, "Qn Qn Qn|Qw W Qe|Qw W Qe|Qs Qs Qs"],
    [1, ". . .|. . .|L . .|. . ."]
  ]
}
```

### Shower (Decorative)
Glass-enclosed shower.
```json
{
  "a": [X, Y, Z],
  "p": {
    "G": "glass_pane",
    "Q": "quartz_block",
    "L": "lever"
  },
  "l": [
    [0, "Q Q"],
    [1, "G G|. ."],
    [2, "G G|L ."]
  ]
}
```

### Sink with Mirror
Bathroom vanity.
```json
{
  "a": [X, Y, Z],
  "p": {
    "C": "cauldron",
    "L": "lever",
    "G": "glass_pane"
  },
  "l": [
    [0, "C"],
    [1, "L"],
    [2, "G"]
  ]
}
```

### Towel Rack
Wall-mounted towel holder.
```json
{
  "a": [X, Y, Z],
  "p": {"B": "white_banner[facing=south]"},
  "l": [[0, "B"]]
}
```

---

## LIVING ROOM

### TV (Painting)
Simple flat screen TV.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "black_concrete",
    "P": "oak_planks"
  },
  "l": [
    [0, "P P"],
    [1, "B B"]
  ]
}
```
Note: Place a 2x1 painting on the black concrete for screen.

### TV (Modern)
TV with speakers.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "black_concrete",
    "N": "note_block"
  },
  "l": [
    [0, "N B B N"],
    [1, "N B B N"]
  ]
}
```

### Fireplace (Simple)
Basic wall fireplace.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "stone_bricks",
    "C": "campfire[lit=true]"
  },
  "l": [
    [0, "S C S"],
    [1, "S . S"],
    [2, "S S S"]
  ]
}
```

### Fireplace (Brick)
Classic brick fireplace.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "bricks",
    "C": "campfire[lit=true]",
    "Sl": "brick_slab[type=bottom]"
  },
  "l": [
    [0, "Sl Sl Sl|B C B"],
    [1, "B . B|B . B"],
    [2, "B . B|B . B"],
    [3, "B B B|B B B"]
  ]
}
```

### Fireplace (with Chimney)
Full fireplace with chimney extending upward.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "stone_bricks",
    "N": "netherrack",
    "F": "fire"
  },
  "l": [
    [-1, ". . .|. N .|. . ."],
    [0, "B . B|B F B|B B B"],
    [1, "B . B|B . B|B . B"],
    [2, "B . B|B . B|B . B"],
    [3, "B B B|B . B|B B B"],
    [4, ". B .|B . B|. B ."],
    [5, ". B .|B . B|. B ."]
  ]
}
```
Note: Light the netherrack for eternal flame.

### Piano (Simple)
Basic piano design.
```json
{
  "a": [X, Y, Z],
  "p": {
    "N": "note_block",
    "J": "jukebox",
    "S": "nether_brick_stairs[facing=south,half=top]"
  },
  "l": [
    [0, "N J"],
    [0, "S S"]
  ]
}
```

### Piano (Grand)
Larger grand piano.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "black_wool",
    "N": "note_block",
    "S": "nether_brick_stairs[facing=south,half=bottom]",
    "St": "nether_brick_stairs[facing=south,half=top]"
  },
  "l": [
    [0, "B B B|B B B|N N N|St St St"],
    [1, "B B .|B . .|. . .|. . ."]
  ]
}
```

### Clock (Wall)
Simple wall clock.
```json
{
  "a": [X, Y, Z],
  "p": {"F": "item_frame[facing=south]"},
  "l": [[0, "F"]]
}
```
Note: Place clock item in frame.

### Bookshelf (Decorative)
Built-in bookshelf with variety.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "bookshelf",
    "P": "oak_planks",
    "L": "loom"
  },
  "l": [
    [0, "P B P"],
    [1, "B L B"],
    [2, "P B P"]
  ]
}
```

### Potted Plant (Floor)
Decorative plant with pot.
```json
{
  "a": [X, Y, Z],
  "p": {"P": "potted_oak_sapling"},
  "l": [[0, "P"]]
}
```
Variations: `potted_fern`, `potted_bamboo`, `potted_cactus`, `potted_red_tulip`, `potted_azure_bluet`, `potted_dandelion`

### Potted Plant (Trapdoor Planter)
Floor planter using trapdoors.
```json
{
  "a": [X, Y, Z],
  "p": {
    "D": "dirt",
    "F": "fern",
    "Tn": "oak_trapdoor[facing=north,half=bottom,open=true]",
    "Ts": "oak_trapdoor[facing=south,half=bottom,open=true]",
    "Te": "oak_trapdoor[facing=east,half=bottom,open=true]",
    "Tw": "oak_trapdoor[facing=west,half=bottom,open=true]"
  },
  "l": [
    [-1, ". Tn .|Tw D Te|. Ts ."],
    [0, ". F ."]
  ]
}
```

### Area Rug (3x5)
Decorative floor rug.
```json
{
  "a": [X, Y, Z],
  "p": {"C": "red_carpet"},
  "l": [[0, "C C C C C|C C C C C|C C C C C"]]
}
```

### Area Rug (with Border)
Rug with contrasting border.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "brown_carpet",
    "C": "orange_carpet"
  },
  "l": [[0, "B B B B B|B C C C B|B C C C B|B B B B B"]]
}
```

---

## GAMES ROOM

### Pool Table
Billiards table.
```json
{
  "a": [X, Y, Z],
  "p": {
    "G": "green_wool",
    "Tn": "dark_oak_trapdoor[facing=north,half=top,open=false]",
    "Ts": "dark_oak_trapdoor[facing=south,half=top,open=false]",
    "Te": "dark_oak_trapdoor[facing=east,half=top,open=false]",
    "Tw": "dark_oak_trapdoor[facing=west,half=top,open=false]"
  },
  "l": [[0, "Tw G G G G Te|Tw G G G G Te|Tw G G G G Te|Tn Tn Tn Tn Tn Ts"]]
}
```

### Ping Pong Table
Table tennis table with net.
```json
{
  "a": [X, Y, Z],
  "p": {
    "G": "green_carpet",
    "S": "oak_slab[type=bottom]",
    "F": "oak_fence",
    "C": "cobweb"
  },
  "l": [
    [0, "S S S S S|S S S S S|S S S S S"],
    [0, "G G G G G|G G G G G|G G G G G"],
    [1, ". . F . .|. . C . .|. . F . ."]
  ]
}
```

### Arcade Cabinet
Retro arcade machine.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "black_concrete",
    "Y": "yellow_concrete",
    "G": "glass_pane",
    "L": "lever"
  },
  "l": [
    [0, "B"],
    [1, "Y|L"],
    [2, "G"],
    [3, "B"]
  ]
}
```

### Chessboard Table
Checkerboard pattern table.
```json
{
  "a": [X, Y, Z],
  "p": {
    "N": "note_block",
    "T": "dark_oak_trapdoor[facing=south,half=top,open=false]"
  },
  "l": [
    [0, "N|T"]
  ]
}
```
Note: Note block texture looks like checkerboard.

---

## OFFICE / STUDY

### Computer (Basic)
Desktop computer setup.
```json
{
  "a": [X, Y, Z],
  "p": {
    "I": "iron_block",
    "P": "stone_pressure_plate"
  },
  "l": [
    [0, "I"],
    [0, "P"]
  ]
}
```
Note: Place painting on iron block as monitor.

### Computer (Laptop)
Portable computer on desk.
```json
{
  "a": [X, Y, Z],
  "p": {
    "P": "oak_planks",
    "Pr": "stone_pressure_plate",
    "F": "flower_pot",
    "B": "stone_button[face=floor,facing=north]"
  },
  "l": [
    [0, "P"],
    [1, "Pr"],
    [1, "F B"]
  ]
}
```

### Filing Cabinet
Office storage.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "barrel[facing=south]",
    "T": "iron_trapdoor[facing=south,half=bottom,open=false]"
  },
  "l": [
    [0, "B|T"],
    [1, "B|T"]
  ]
}
```

### Office Chair
Rolling desk chair.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "red_nether_brick_slab[type=bottom]",
    "Tn": "spruce_trapdoor[facing=north,half=bottom,open=true]",
    "Te": "spruce_trapdoor[facing=east,half=bottom,open=true]",
    "Tw": "spruce_trapdoor[facing=west,half=bottom,open=true]",
    "B": "red_banner[facing=south]"
  },
  "l": [
    [0, ". Tn .|Tw S Te"],
    [1, ". B ."]
  ]
}
```

### Printer
Office printer.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "smooth_stone_slab[type=bottom]",
    "Q": "quartz_slab[type=top]"
  },
  "l": [
    [0, "S"],
    [0, "Q"]
  ]
}
```

---

## OUTDOOR / PATIO

### Grill / BBQ
Outdoor cooking grill.
```json
{"a": [X, Y, Z], "p": {"A": "anvil[facing=north]"}, "l": [[0, "A"]]}
```

### Patio Table (Umbrella)
Outdoor table with umbrella.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "P": "oak_pressure_plate",
    "W": "red_wool"
  },
  "l": [
    [0, ". F ."],
    [1, "P P P"],
    [2, ". F ."],
    [3, ". F ."],
    [4, "W W W|W W W|W W W"]
  ]
}
```

### Garden Bench
Outdoor seating.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "oak_stairs[facing=south]",
    "Sl": "oak_slab[type=bottom]"
  },
  "l": [[0, "Sl S S S Sl"]]
}
```

### Fountain (Small)
Decorative water feature.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "stone_brick_slab[type=bottom]",
    "W": "water"
  },
  "l": [
    [0, ". S S S .|S W W W S|S W W W S|S W W W S|. S S S ."]
  ]
}
```

### Mailbox
Decorative mailbox.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "B": "barrel[facing=west]"
  },
  "l": [
    [0, "F"],
    [1, "B"]
  ]
}
```

---

## CURTAINS / WINDOW TREATMENTS

### Curtain (Banner)
Simple banner curtain.
```json
{
  "a": [X, Y, Z],
  "p": {"B": "white_banner[facing=south]"},
  "l": [[0, "B B"]]
}
```

### Curtain (Wool)
Wool block curtain.
```json
{
  "a": [X, Y, Z],
  "p": {"W": "white_wool"},
  "l": [
    [0, "W W"],
    [1, "W W"]
  ]
}
```

### Shutters (Trapdoor)
Window shutters.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Te": "oak_trapdoor[facing=east,half=bottom,open=true]",
    "Tw": "oak_trapdoor[facing=west,half=bottom,open=true]"
  },
  "l": [
    [0, "Te . Tw"],
    [1, "Te . Tw"]
  ]
}
```
Note: Leave middle block for window (glass pane).

---

## CEILING FEATURES

### Ceiling Fan
Decorative ceiling fan.
```json
{
  "a": [X, Y, Z],
  "p": {
    "B": "oak_planks",
    "Tn": "oak_trapdoor[facing=north,half=bottom,open=true]",
    "Ts": "oak_trapdoor[facing=south,half=bottom,open=true]",
    "Te": "oak_trapdoor[facing=east,half=bottom,open=true]",
    "Tw": "oak_trapdoor[facing=west,half=bottom,open=true]"
  },
  "l": [[0, ". Tn .|Tw B Te|. Ts ."]]
}
```

### Exposed Beam
Decorative ceiling beam.
```json
{
  "a": [X, Y, Z],
  "p": {"L": "stripped_oak_log[axis=x]"},
  "l": [[0, "L L L L L"]]
}
```
Note: Change axis for different orientations (`axis=z` for north-south).

---

## DECORATIVE ITEMS

### Water Spigot
Wall-mounted water feature.
```json
{
  "a": [X, Y, Z],
  "p": {
    "W": "cobblestone_wall",
    "L": "lever",
    "T": "tripwire_hook[facing=south]",
    "C": "cauldron"
  },
  "l": [
    [0, "C|T"],
    [1, ".|W"],
    [2, ".|L"]
  ]
}
```

### Radio
Decorative radio.
```json
{
  "a": [X, Y, Z],
  "p": {
    "N": "note_block",
    "I": "iron_block"
  },
  "l": [[0, "N I N"]]
}
```

### Fancy Jukebox
Decorated music player.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Se": "oak_stairs[facing=east,half=bottom]",
    "Sw": "oak_stairs[facing=west,half=bottom]",
    "R": "redstone_lamp",
    "J": "jukebox"
  },
  "l": [
    [0, "Se R Sw"],
    [1, ". J ."]
  ]
}
```

### Globe
Decorative world globe.
```json
{
  "a": [X, Y, Z],
  "p": {
    "F": "oak_fence",
    "H": "player_head"
  },
  "l": [
    [0, "F"],
    [1, "H"]
  ]
}
```
Note: Use a custom player head texture for globe appearance.

### Trophy
Display trophy.
```json
{
  "a": [X, Y, Z],
  "p": {
    "S": "oak_slab[type=bottom]",
    "B": "brewing_stand"
  },
  "l": [
    [0, "S"],
    [1, "B"]
  ]
}
```

### Pet Door
Small animal entrance.
```json
{
  "a": [X, Y, Z],
  "p": {
    "Pn": "heavy_weighted_pressure_plate",
    "Ps": "heavy_weighted_pressure_plate",
    "G": "oak_fence_gate[facing=south]"
  },
  "l": [[0, "Pn G Ps"]]
}
```

---

## QUICK REFERENCE: Block Names

### Wood Types
- `oak`, `spruce`, `birch`, `jungle`, `acacia`, `dark_oak`, `mangrove`, `cherry`, `bamboo`, `crimson`, `warped`

### Stair Facings
- `[facing=north/south/east/west,half=bottom/top]`

### Trapdoor States
- `[facing=north/south/east/west,half=bottom/top,open=true/false]`

### Slab Types
- `[type=bottom/top/double]`

### Door States
- `[facing=north/south/east/west,half=lower/upper,hinge=left/right]`

### Bed States
- `[facing=north/south/east/west,part=head/foot]`

### Barrel/Chest Facing
- `barrel[facing=up/down/north/south/east/west]`
- `chest[facing=north/south/east/west,type=single/left/right]`

### Campfire
- `campfire[lit=true/false,facing=north/south/east/west]`

### Wall-Mounted Blocks
- `wall_torch[facing=north/south/east/west]` (facing = direction it points)
- `ladder[facing=north/south/east/west]` (facing = direction player faces)
- `lever[face=floor/wall/ceiling,facing=north/south/east/west]`
- `stone_button[face=floor/wall/ceiling,facing=north/south/east/west]`
