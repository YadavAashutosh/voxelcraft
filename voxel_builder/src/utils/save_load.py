"""
src/utils/save_load.py
JSON-based world persistence.
"""

import json
from pathlib import Path
from src.core.world import World


SAVE_DIR = Path("saves")


def save_world(world: World, slot: str = "world_01") -> Path:
    SAVE_DIR.mkdir(exist_ok=True)
    path = SAVE_DIR / f"{slot}.json"
    data = world.serialize()
    path.write_text(json.dumps(data, indent=2))
    print(f"💾 Saved {len(data)} voxels → {path}")
    return path


def load_world(world: World, slot: str = "world_01") -> bool:
    path = SAVE_DIR / f"{slot}.json"
    if not path.exists():
        print(f"⚠️  Save '{slot}' not found.")
        return False
    data = json.loads(path.read_text())
    world.load(data)
    print(f"📂 Loaded {len(data)} voxels from {path}")
    return True