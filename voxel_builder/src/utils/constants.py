from ursina import color

# ── Engine
TARGET_FPS        = 120
MOUSE_SENSITIVITY = 40

# ── World
WORLD_SIZE    = 64
WORLD_HEIGHT  = 32
SPAWN_HEIGHT  = 4
CHUNK_SIZE    = 8

# ── Player
PLAYER_SPEED  = 10
PLAYER_JUMP   = 2

# ── Interaction
RAYCAST_DISTANCE = 12
UNDO_STACK_LIMIT = 64

# ── Voxel types
VOXEL_TYPES = [
    ("Grass",  color.rgb(106, 168,  78), "grass"),
    ("Dirt",   color.rgb(139,  90,  43), "dirt"),
    ("Stone",  color.rgb(128, 128, 128), "stone"),
    ("Sand",   color.rgb(237, 201, 120), "sand"),
    ("Wood",   color.rgb(101,  67,  33), "wood"),
    ("Brick",  color.rgb(178,  84,  56), "brick"),
    ("Snow",   color.rgb(240, 248, 255), "snow"),
    ("Lava",   color.rgb(220,  80,  10), "lava"),
    ("Glass",  color.rgba(180,220,255,100), "glass"),
    ("Gold",   color.rgb(255, 200,  50), "gold"),
]

# ── UI colours
UI_BG     = color.rgba(0, 0, 0, 160)
UI_ACCENT = color.rgb(80, 200, 120)
UI_TEXT   = color.white
UI_WARN   = color.rgb(255, 160, 50)