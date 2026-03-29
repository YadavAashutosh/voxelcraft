"""
src/core/world.py
Spatial index — maps integer (x,y,z) positions to Voxel instances.
Provides O(1) lookups and chunk-aware iteration for optimisation.
"""

from ursina import *
from src.core.voxel import Voxel
from src.utils.constants import CHUNK_SIZE, WORLD_SIZE, WORLD_HEIGHT


class World:
    """
    Lightweight spatial registry.
    All voxel CRUD goes through this class so the manager stays clean.
    """

    def __init__(self):
        # Primary store: grid_pos (tuple) → Voxel
        self._voxels: dict[tuple, Voxel] = {}

    # ── CRUD ────────────────────────────────────────────────────────────────

    def add(self, pos: tuple, type_index: int = 0, tint: Color = None) -> Voxel:
        """Create and register a voxel. Returns the new Voxel."""
        pos = self._norm(pos)
        if pos in self._voxels:
            return self._voxels[pos]          # don't stack
        v = Voxel(pos, type_index, tint)
        self._voxels[pos] = v
        return v

    def remove(self, pos: tuple) -> Voxel | None:
        """Destroy and deregister a voxel. Returns removed Voxel or None."""
        pos = self._norm(pos)
        v = self._voxels.pop(pos, None)
        if v:
            destroy(v)
        return v

    def get(self, pos: tuple) -> Voxel | None:
        return self._voxels.get(self._norm(pos))

    def has(self, pos: tuple) -> bool:
        return self._norm(pos) in self._voxels

    def all_voxels(self):
        return list(self._voxels.values())

    def positions(self):
        return set(self._voxels.keys())

    # ── World generation helpers ────────────────────────────────────────────

    def generate_flat_floor(self, size: int = 16, y: int = 0, type_index: int = 0):
        """Stamp a flat N×N floor of voxels."""
        half = size // 2
        for x in range(-half, half):
            for z in range(-half, half):
                self.add((x, y, z), type_index)

    # ── Chunk queries ───────────────────────────────────────────────────────

    def get_chunk(self, cx: int, cy: int, cz: int) -> list[Voxel]:
        """Return all voxels in a CHUNK_SIZE³ cell."""
        results = []
        ox = cx * CHUNK_SIZE
        oy = cy * CHUNK_SIZE
        oz = cz * CHUNK_SIZE
        for dx in range(CHUNK_SIZE):
            for dy in range(CHUNK_SIZE):
                for dz in range(CHUNK_SIZE):
                    v = self._voxels.get((ox + dx, oy + dy, oz + dz))
                    if v:
                        results.append(v)
        return results

    def neighbors(self, pos: tuple) -> list[Voxel]:
        """Return up to 6 face-adjacent voxels."""
        x, y, z = self._norm(pos)
        dirs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
        return [self._voxels[nb] for nx,ny,nz in dirs
                if (nb := (x+nx, y+ny, z+nz)) in self._voxels]

    # ── Serialisation ───────────────────────────────────────────────────────

    def serialize(self) -> list:
        return [v.serialize() for v in self._voxels.values()]

    def load(self, data: list):
        self.clear()
        for entry in data:
            v = Voxel.deserialize(entry)
            self._voxels[v.grid_pos] = v

    def clear(self):
        for v in self._voxels.values():
            destroy(v)
        self._voxels.clear()

    # ── Internal ────────────────────────────────────────────────────────────

    @staticmethod
    def _norm(pos) -> tuple:
        return (int(round(pos[0])), int(round(pos[1])), int(round(pos[2])))

    def __len__(self):
        return len(self._voxels)