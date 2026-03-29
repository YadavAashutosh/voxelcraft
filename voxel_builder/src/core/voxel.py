"""
src/core/voxel.py
The atomic building block of the world.
Inherits from Ursina's Button for built-in raycast / mouse detection.
"""

from ursina import *
from src.utils.constants import VOXEL_TYPES


class Voxel(Button):
    """
    A single 1×1×1 voxel cube.

    Attributes
    ----------
    grid_pos   : tuple[int,int,int]  — integer world-space position
    type_index : int                 — index into VOXEL_TYPES
    tint_color : Color               — per-voxel RGB tint override
    selected   : bool                — is this voxel highlighted?
    """

    # Shared mesh — all voxels use the same cube geometry
    _CUBE_MODEL  = "cube"
    _CUBE_ORIGIN = Vec3(0, 0, 0)

    def __init__(self, grid_pos: tuple, type_index: int = 0, tint: Color = None):
        name, base_color, tex_name = VOXEL_TYPES[type_index]

        super().__init__(
            parent        = scene,
            position      = Vec3(*grid_pos),
            model         = self._CUBE_MODEL,
            origin_y      = self._CUBE_ORIGIN.y,
            texture       = self._resolve_texture(tex_name),
            color         = tint if tint else base_color,
            highlight_color = color.rgba(255, 255, 255, 40),
        )

        self.grid_pos    = tuple(int(v) for v in grid_pos)
        self.type_index  = type_index
        self.tint_color  = tint if tint else base_color
        self.selected    = False
        self._outline    = None          # lazy-created hover outline

    # ── Helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_texture(tex_name: str):
        """Return a texture asset path or fall back to white_cube."""
        path = f"assets/textures/{tex_name}.png"
        try:
            return load_texture(path)
        except Exception:
            return "white_cube"

    # ── Public API ──────────────────────────────────────────────────────────

    def set_type(self, type_index: int):
        """Change voxel type (texture + base color)."""
        self.type_index = type_index
        name, base_color, tex_name = VOXEL_TYPES[type_index]
        self.texture    = self._resolve_texture(tex_name)
        self.tint_color = base_color
        self.color      = base_color

    def set_tint(self, new_color: Color):
        """Override the voxel's color tint."""
        self.tint_color = new_color
        self.color      = new_color

    def show_outline(self, visible: bool = True):
        """Toggle a subtle black outline for hover feedback."""
        if visible and self._outline is None:
            self._outline = Entity(
                parent   = self,
                model    = "cube",
                color    = color.rgba(0, 0, 0, 80),
                scale    = 1.04,
                enabled  = True,
            )
        elif self._outline:
            self._outline.enabled = visible

    def serialize(self) -> dict:
        """Minimal dict for save/load."""
        return {
            "pos":   self.grid_pos,
            "type":  self.type_index,
            "color": (self.tint_color.r, self.tint_color.g,
                      self.tint_color.b, self.tint_color.a),
        }

    @classmethod
    def deserialize(cls, data: dict) -> "Voxel":
        r, g, b, a = data["color"]
        return cls(
            grid_pos   = data["pos"],
            type_index = data["type"],
            tint       = color.rgba(r, g, b, a),
        )