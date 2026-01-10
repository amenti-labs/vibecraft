# Minecraft Scale & Proportion Reference
# Player-scaled architectural dimensions for realistic builds
# Format: TOON (Token-Oriented Object Notation)

player_dimensions:
  height: 1.8          # blocks (eyes at 1.62)
  width: 0.6           # blocks (hitbox)
  crouching: 1.5       # blocks tall when sneaking
  jump_reach: 4.5      # blocks (can place blocks up to this height)
  arm_reach: 4.5       # blocks horizontal reach

minimum_clearances:
  walking: 2           # blocks tall (absolute minimum, feels cramped)
  comfortable: 3       # blocks tall (standard ceiling height)
  grand: 4-6           # blocks tall (impressive spaces)
  crouch_space: 2      # blocks (for attics, crawlspaces)

  doorway_width: 1     # blocks (tight but passable)
  hallway_width: 2     # blocks (comfortable for 1 player)
  hallway_wide: 3      # blocks (two players can pass)

  stair_headroom: 3    # blocks above stair

room_sizes:
  # Format: {width: X, depth: Y, ceiling: Z}
  # All dimensions in blocks

  bedroom_single:
    minimum: {width: 4, depth: 5, ceiling: 3}      # 20 m² - tight, functional
    comfortable: {width: 5, depth: 6, ceiling: 3}  # 30 m² - standard
    spacious: {width: 6, depth: 8, ceiling: 3}     # 48 m² - luxury
    master: {width: 8, depth: 10, ceiling: 4}      # 80 m² - grand
    notes: "Bed = 2 blocks long, needs walking space around"

  bedroom_double:
    minimum: {width: 5, depth: 6, ceiling: 3}
    comfortable: {width: 6, depth: 8, ceiling: 3}
    spacious: {width: 8, depth: 10, ceiling: 4}

  kitchen:
    minimum: {width: 4, depth: 5, ceiling: 3}      # galley kitchen
    comfortable: {width: 5, depth: 7, ceiling: 3}  # U-shape possible
    spacious: {width: 6, depth: 9, ceiling: 3}     # L-shape with island
    notes: "Needs 3-block counter runs, 2-block aisle"

  dining_room:
    minimum: {width: 5, depth: 6, ceiling: 3}      # table for 4
    comfortable: {width: 6, depth: 8, ceiling: 3}  # table for 6-8
    spacious: {width: 8, depth: 10, ceiling: 4}    # table for 10+
    notes: "Table = 3-5 blocks, chairs need 1 block clearance"

  living_room:
    minimum: {width: 6, depth: 6, ceiling: 3}
    comfortable: {width: 8, depth: 10, ceiling: 3}
    spacious: {width: 10, depth: 12, ceiling: 4}
    notes: "Seating area needs 5x5 minimum"

  bathroom:
    minimum: {width: 3, depth: 3, ceiling: 3}      # powder room
    comfortable: {width: 4, depth: 5, ceiling: 3}  # full bath
    spacious: {width: 5, depth: 7, ceiling: 3}     # luxury bath
    notes: "Tub = 3 blocks, shower = 2x2 minimum"

  great_hall:
    minimum: {width: 10, depth: 15, ceiling: 6}
    comfortable: {width: 15, depth: 20, ceiling: 8}
    spacious: {width: 20, depth: 30, ceiling: 10}
    notes: "Impressive space, columns every 6-8 blocks"

  throne_room:
    minimum: {width: 12, depth: 18, ceiling: 8}
    comfortable: {width: 15, depth: 25, ceiling: 10}
    spacious: {width: 20, depth: 35, ceiling: 12}
    notes: "Throne platform = 3x3, raised 1-2 blocks"

  library:
    minimum: {width: 5, depth: 6, ceiling: 3}
    comfortable: {width: 6, depth: 8, ceiling: 4}   # two-story shelves
    spacious: {width: 8, depth: 12, ceiling: 6}     # grand library
    notes: "Shelves = 1 block thick, aisles = 2 blocks"

  storage_room:
    minimum: {width: 3, depth: 4, ceiling: 3}
    comfortable: {width: 4, depth: 6, ceiling: 3}
    spacious: {width: 6, depth: 8, ceiling: 4}
    notes: "Chest rows need 1 block access aisle"

  workshop:
    minimum: {width: 5, depth: 6, ceiling: 3}
    comfortable: {width: 6, depth: 8, ceiling: 3}
    spacious: {width: 8, depth: 10, ceiling: 4}
    notes: "Workbenches + storage + walking space"

  entrance_hall:
    minimum: {width: 4, depth: 6, ceiling: 4}
    comfortable: {width: 6, depth: 8, ceiling: 5}
    spacious: {width: 8, depth: 12, ceiling: 6}
    notes: "First impression, higher ceiling preferred"

  corridor:
    narrow: {width: 2, ceiling: 3}                  # single file
    standard: {width: 3, ceiling: 3}                # comfortable
    wide: {width: 4, ceiling: 3}                    # two-way traffic
    grand: {width: 5, ceiling: 4}                   # processional

  stairwell:
    minimum: {width: 3, depth: 4, ceiling: 3}       # per floor
    comfortable: {width: 4, depth: 5, ceiling: 3}
    grand: {width: 6, depth: 8, ceiling: 4}
    notes: "Straight stairs need 4-5 blocks length per floor"

  balcony:
    minimum: {depth: 2, ceiling: 3}                 # shallow
    comfortable: {depth: 3, ceiling: 3}             # usable
    spacious: {depth: 4, ceiling: 3}                # furniture possible

  tower_room:
    small: {diameter: 5, ceiling: 3}                # 5x5 interior
    medium: {diameter: 7, ceiling: 4}               # 7x7 interior
    large: {diameter: 9, ceiling: 5}                # 9x9 interior

openings:
  doors:
    standard: {width: 1, height: 2}                 # oak_door, iron_door
    double: {width: 2, height: 2}                   # grand entrance
    tall: {width: 1, height: 3}                     # monumental
    double_tall: {width: 2, height: 3}              # castle gates
    iron_double: {width: 3, height: 3}              # fortress gate
    notes: "Always leave 1 block above door for clearance"

  windows:
    slit: {width: 1, height: 2}                     # arrow slit, medieval
    small: {width: 1, height: 2}                    # bathroom, storage
    standard: {width: 2, height: 2}                 # most rooms
    wide: {width: 3, height: 2}                     # living areas
    tall: {width: 2, height: 3}                     # grand rooms
    picture: {width: 4, height: 3}                  # feature window
    floor_to_ceiling: {width: 3, height: 6}         # modern, dramatic
    notes: "Place at height 2-3 blocks (eye level = 1.62)"

  archways:
    small: {width: 3, height: 3}                    # interior passage
    standard: {width: 5, height: 5}                 # entrance
    grand: {width: 7, height: 7}                    # monumental
    notes: "Width should be odd number for centered keystone"

furniture_dimensions:
  # Standard Minecraft furniture sizes

  bed:
    length: 2          # blocks (head to foot)
    width: 1           # blocks
    clearance: 1       # blocks around bed for access

  table_dining:
    small: {length: 3, width: 2, height: 1}        # seats 4
    medium: {length: 5, width: 3, height: 1}       # seats 6-8
    large: {length: 7, width: 3, height: 1}        # seats 10
    notes: "Made with fence + pressure_plate"

  table_work:
    size: {length: 2, width: 1, height: 1}
    notes: "Fence + pressure_plate or slab on block"

  chair:
    footprint: {width: 1, depth: 1}
    notes: "Stairs block facing into room"

  sofa:
    small: {length: 2, depth: 1}
    large: {length: 3, depth: 1}
    notes: "Multiple stairs in row"

  chest:
    single: {width: 1, depth: 1, height: 1}
    double: {width: 2, depth: 1, height: 1}
    clearance: 1       # block above to open

  bookshelf:
    width: 1
    height: 3          # typical wall height
    depth: 1

  counter_kitchen:
    height: 1          # slab on block = 1.5 visually
    depth: 1
    workspace: 3       # minimum counter length

  fireplace:
    small: {width: 3, depth: 2, height: 3}
    standard: {width: 5, depth: 2, height: 4}
    grand: {width: 7, depth: 3, height: 6}

  throne:
    footprint: {width: 2, depth: 2}
    platform: {width: 4, depth: 4, height: 2}      # raised dais

  lectern:
    footprint: {width: 1, depth: 1}

  enchanting_area:
    table: {width: 1, depth: 1}
    bookshelf_ring: 5  # blocks diameter minimum

  brewing_area:
    stand: {width: 1, depth: 1}
    clearance: 3       # blocks around for movement

spacing_guidelines:
  window_rhythm:
    tight: 2           # blocks between windows (busy)
    standard: 3        # blocks between windows (balanced)
    wide: 4            # blocks between windows (stately)
    notes: "For facades, consistent rhythm = professional"

  column_spacing:
    minimum: 4         # blocks between columns
    standard: 6        # blocks between columns
    grand: 8           # blocks between columns
    maximum: 10        # blocks (needs support)
    notes: "Too wide = structural implausibility"

  torch_placement:
    spawn_safe: 12     # blocks apart (light level 8+)
    comfortable: 8     # blocks apart (well-lit)
    bright: 6          # blocks apart (no shadows)
    very_bright: 4     # blocks apart (workshop)
    notes: "Light level must be 8+ to prevent mob spawning"

  furniture_clearance:
    walking_aisle: 2   # blocks (comfortable passage)
    tight_passage: 1   # blocks (squeeze through)
    table_to_wall: 2   # blocks (chair pull-out space)
    bed_to_wall: 1     # blocks (making bed access)

  stair_dimensions:
    rise: 1            # block per step (always)
    run: 1             # block per step (straight stairs)
    width_min: 2       # blocks (single file)
    width_standard: 3  # blocks (comfortable)
    width_grand: 5     # blocks (impressive)
    landing: 3         # blocks minimum (turn platform)

wall_thicknesses:
  exterior:
    light: 1           # blocks (cottage, shed)
    standard: 1        # blocks (most buildings)
    fortress: 2        # blocks (castle, thick walls)
    massive: 3         # blocks (city walls, keep)

  interior:
    standard: 1        # blocks (room dividers)
    thin: 0            # use fence/glass for visual division

  foundation:
    standard: 1        # blocks (same as exterior wall)
    raised: 2          # blocks (visible basement)

  defensive:
    curtain_wall: 3    # blocks (castle outer wall)
    keep_wall: 4       # blocks (main fortress)

ceiling_heights:
  cramped: 2           # blocks (storage, attic crawlspace)
  minimum: 3           # blocks (standard rooms, feels tight)
  comfortable: 4       # blocks (preferred for main rooms)
  tall: 5              # blocks (dining halls, living rooms)
  grand: 6-8           # blocks (great halls, throne rooms)
  monumental: 9-12     # blocks (cathedrals, palaces)
  notes: "Higher ceilings = grander feel, but use blocks wisely"

structural_elements:
  columns:
    slim: 1            # blocks (pilaster, decorative)
    standard: 2        # blocks (structural 2x2)
    massive: 3         # blocks (grand 3x3)
    spacing: 6-8       # blocks between columns

  beams:
    small: 1           # blocks (decorative)
    standard: 2        # blocks (visible support)
    large: 3           # blocks (massive timber)

  stairs_exterior:
    step_width: 3      # blocks minimum (feels grand)
    step_run: 1        # blocks deep per step
    landing: 4         # blocks (before door)

  railings:
    height: 1          # blocks (fence, cobblestone_wall)
    spacing: 2         # blocks (can space fence posts)

  parapets:
    height: 1-2        # blocks (castle/roof edge)
    thickness: 1       # blocks

roof_proportions:
  overhang:
    none: 0            # blocks (flush with walls)
    minimal: 1         # blocks (most buildings)
    standard: 2        # blocks (good shadow line)
    deep: 3            # blocks (dramatic)

  pitch_rise_per_run:
    flat: 0            # rise per 12 run (modern)
    shallow: 3         # rise per 12 run (prairie style)
    standard: 6        # rise per 12 run (most roofs)
    steep: 12          # rise per 12 run (alpine, A-frame)
    very_steep: 18     # rise per 12 run (gothic, Tudor)

  gable_height:
    small_building: 4  # blocks (10 wide building)
    medium: 6          # blocks (15 wide building)
    large: 8           # blocks (20 wide building)

outdoor_spaces:
  patio:
    minimum: {width: 4, depth: 4}
    comfortable: {width: 6, depth: 6}
    spacious: {width: 8, depth: 10}

  garden_bed:
    small: {width: 2, length: 3}
    medium: {width: 3, length: 5}
    large: {width: 4, length: 8}

  pathway:
    footpath: 1        # blocks wide
    walkway: 2         # blocks wide (comfortable)
    main_path: 3       # blocks wide (standard)
    road: 5            # blocks wide (cart/horse)

  pond:
    small: {diameter: 5, depth: 2}
    medium: {diameter: 8, depth: 2}
    large: {diameter: 12, depth: 3}

  fountain:
    small: {diameter: 3}
    medium: {diameter: 5}
    large: {diameter: 7}
    notes: "Center pedestal = 1 block, basin walls = 1 block"

  tree_spacing:
    tight: 3           # blocks (forest)
    standard: 6        # blocks (grove)
    open: 10           # blocks (park)
    specimen: 15       # blocks (isolated feature)

wall_face_proportions:
  window_to_wall_ratio:
    fortress: 0.10     # 10% windows (defensive)
    medieval: 0.15     # 15% windows (typical old)
    traditional: 0.20  # 20% windows (balanced)
    modern: 0.30       # 30% windows (lots of light)
    glass_curtain: 0.60 # 60%+ (contemporary)

  door_to_facade_ratio:
    minimum: 0.05      # 5% (small door, big wall)
    standard: 0.10     # 10% (proportional)
    grand: 0.20        # 20% (impressive entry)

practical_calculations:
  blocks_per_floor:
    low_ceiling: 4     # floor slab + 3 ceiling
    standard: 5        # floor slab + 4 ceiling
    tall: 6            # floor slab + 5 ceiling

  stair_blocks_per_floor:
    straight: 5        # blocks length (4 rise + landing)
    spiral: 9          # blocks (3x3 footprint, compact)

  room_area:
    tiny: 12           # m² (3x4)
    small: 20          # m² (4x5)
    medium: 30         # m² (5x6)
    large: 48          # m² (6x8)
    very_large: 80     # m² (8x10)

best_practices:
  - "Player is 1.8 blocks tall - minimum 2 ceiling feels cramped, 3 is comfortable"
  - "Doors at 2 tall work but feel tight - 3 tall looks grand"
  - "Windows at height 2-3 blocks align with player eye level (1.62)"
  - "Rooms under 4x5 feel claustrophobic"
  - "Hallways under 2 wide require sidling"
  - "Ceilings over 6 blocks waste vertical space unless intentional (grand hall)"
  - "Furniture needs 1-2 block clearance for player access"
  - "Light sources every 8 blocks = well-lit, every 12 = spawn-safe minimum"
  - "Interior walls at 1 block thick - thicker wastes space"
  - "Exterior walls at 1-2 blocks depending on style"
  - "Window rhythm at 3-block spacing looks balanced on facades"
  - "Roof overhang at 1-2 blocks creates shadow line and depth"
  - "Columns every 6-8 blocks in large halls prevents floating ceilings"

common_mistakes:
  - "Ceiling too low (2 blocks) - use 3 minimum for comfort"
  - "Room too small (3x3) - minimum 4x5 for functional rooms"
  - "Windows too small on large walls - aim for 15-20% coverage"
  - "No walking space around furniture - need 1-2 block clearance"
  - "Hallways 1 block wide - uncomfortable, use 2-3 blocks"
  - "Stairs without headroom - need 3 blocks above stairs"
  - "Too much wasted ceiling height - 6+ blocks only for grand spaces"
  - "Inconsistent ceiling heights - pick 3 or 4 and stick to it per floor"
  - "Forgot lighting - dark corners = mob spawns"
  - "Door too small for grand entrance - use 2-3 wide for castles"
