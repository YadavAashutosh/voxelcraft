# VoxelCraft

A feature-rich 3D Voxel Builder built from scratch in Python — inspired by Minecraft & MagicaVoxel.

**Built by [Aashutosh](https://github.com/YadavAashutosh)**

---

## What is VoxelCraft?

VoxelCraft is a fully functional 3D voxel editor built entirely in Python using the Ursina Engine (powered by Panda3D). Place, remove, paint, fill, copy, paste, and undo blocks in a real-time 3D world with a first-person controller — all from a clean, modular codebase.

---

## Features

- 3D First-Person World — walk, jump, and build freely
- 10 Voxel Types — Grass, Dirt, Stone, Sand, Wood, Brick, Snow, Lava, Glass, Gold
- 10 Color Tints — per-voxel RGB color override
- Directional Lighting — sun + ambient fill with soft shadows
- Sunset Skybox — beautiful sky dome with atmospheric fog
- Live HUD — shows active mode, block type, FPS counter
- 64-deep Undo Stack — never lose your work
- JSON Save/Load — persist your worlds to disk

---

## All 10 Operations

| # | Operation | Control |
|---|-----------|---------|
| 1 | Add Voxel | Left Click on a face |
| 2 | Remove Voxel | Right Click on a block |
| 3 | Select Voxel | Middle Click or Q |
| 4 | Change Block Type | Scroll Wheel up/down |
| 5 | Change Color Tint | R key |
| 6 | Flood Fill Paint | F key |
| 7 | Box Delete | B twice (set corner A, then B) |
| 8 | Copy Selection | C key (copies 3x3x3 region) |
| 9 | Paste Selection | V key (aim at surface) |
| 10 | Undo | Ctrl+Z (64 levels deep) |

---

## Full Controls

| Key | Action |
|-----|--------|
| WASD | Move |
| Mouse | Look around |
| Space | Jump |
| 1 | Add mode |
| 2 | Remove mode |
| 3 | Paint mode |
| 4 | Flood Fill mode |
| 5 | Box Delete mode |
| Esc | Quit |

---

## Installation & Running

### 1. Clone the repo
```bash
git clone https://github.com/YadavAashutosh/voxelcraft.git
cd voxelcraft
```

### 2. Install dependencies
```bash
pip install ursina Pillow numpy
```

### 3. Run
```bash
python main.py
```

Requires Python 3.9+

---

## Project Structure

```
voxel_builder/
├── main.py                    # Entry point
├── assets/
│   ├── textures/              # PNG block textures
│   ├── shaders/               # Custom GLSL (future)
│   └── sounds/                # SFX (future)
└── src/
    ├── core/
    │   ├── voxel.py           # Voxel entity class
    │   ├── voxel_manager.py   # All 10 operations + undo
    │   └── world.py           # Spatial index
    ├── ui/
    │   ├── hud.py             # On-screen overlay
    │   └── crosshair.py       # Custom dot reticle
    └── utils/
        ├── constants.py       # All tunable values
        ├── lighting.py        # Sun + ambient lights
        ├── save_load.py       # JSON persistence
        └── skybox.py          # Sky dome + fog
```

---

## Customisation

All tunable values are in `src/utils/constants.py`:

```python
TARGET_FPS        = 120    # Lower if GPU is slow
RAYCAST_DISTANCE  = 12     # How far you can place blocks
PLAYER_SPEED      = 10     # Movement speed
MOUSE_SENSITIVITY = 40     # Mouse look speed
UNDO_STACK_LIMIT  = 64     # How many undos to remember
```

---

## Roadmap

- Greedy meshing (merge coplanar faces for better performance)
- Chunk-based frustum culling
- Custom texture pack loader
- Sound effects on place/remove
- World export to .obj format

---

## Author

**Aashutosh**
GitHub: [YadavAashutosh](https://github.com/YadavAashutosh)

---

## License

MIT License — use it, modify it, build on it freely.

---

Built with Python + Ursina Engine + Panda3D
