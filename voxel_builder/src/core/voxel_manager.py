"""
src/core/voxel_manager.py
The "brain" of the editor.

Handles all 10 operations:
  1.  Add Voxel          (left-click on face)
  2.  Remove Voxel       (right-click)
  3.  Select Voxel       (middle-click / Q)
  4.  Change Type        (scroll wheel)
  5.  Change Color Tint  (R key → colour picker cycle)
  6.  Flood Fill Paint   (F key)
  7.  Box Delete         (B key to set corner, B again to execute)
  8.  Copy Selection     (C key while voxel selected)
  9.  Paste Selection    (V key)
  10. Undo               (Ctrl+Z)
"""

from __future__ import annotations
from collections import deque
from ursina import *
from src.core.world import World
from src.core.voxel import Voxel
from src.utils.constants import (
    VOXEL_TYPES, RAYCAST_DISTANCE, UNDO_STACK_LIMIT
)

# Preset tint colours for "Change Color" cycling
TINT_PALETTE = [
    color.white,
    color.red,
    color.orange,
    color.yellow,
    color.lime,
    color.cyan,
    color.azure,
    color.violet,
    color.magenta,
    color.pink,
]


class _UndoRecord:
    """Immutable snapshot of a single reversible action."""
    __slots__ = ("action", "pos", "type_index", "tint", "batch")

    def __init__(self, action: str, pos=None, type_index=0,
                 tint=None, batch=None):
        self.action     = action      # "add" | "remove" | "paint" | "batch_remove"
        self.pos        = pos
        self.type_index = type_index
        self.tint       = tint
        self.batch      = batch       # list of _UndoRecord for compound ops


class VoxelManager:
    """Mediates all user interactions with the World."""

    def __init__(self, world: World):
        self.world          = world

        # Active state
        self.active_type    = 0
        self.active_tint    = TINT_PALETTE[0]
        self.tint_index     = 0
        self.mode           = "add"           # "add" | "remove" | "paint" | "fill" | "box"

        # Selection
        self.selected_voxel: Voxel | None = None
        self._hover_voxel:   Voxel | None = None

        # Box-delete corners
        self._box_corner_a: tuple | None = None

        # Clipboard
        self._clipboard: list[dict] = []     # list of {rel_pos, type, tint}

        # Undo stack
        self._undo_stack: deque[_UndoRecord] = deque(maxlen=UNDO_STACK_LIMIT)

        # Status message (read by HUD)
        self.status_msg = ""

    # ────────────────────────────────────────────────────────────────────────
    # Frame update — hover outline
    # ────────────────────────────────────────────────────────────────────────

    def update(self):
        hit = raycast(
            camera.world_position,
            camera.forward,
            distance=RAYCAST_DISTANCE,
            ignore=(scene,),
        )

        new_hover = hit.entity if (hit.hit and isinstance(hit.entity, Voxel)) else None

        if new_hover is not self._hover_voxel:
            if self._hover_voxel:
                self._hover_voxel.show_outline(False)
            self._hover_voxel = new_hover
            if self._hover_voxel:
                self._hover_voxel.show_outline(True)

    # ────────────────────────────────────────────────────────────────────────
    # Input routing
    # ────────────────────────────────────────────────────────────────────────

    def handle_input(self, key: str):
        # ── Mode / type selection ──────────────────────────────────────────
        if key == "scroll up":
            self.active_type = (self.active_type + 1) % len(VOXEL_TYPES)
            self.status_msg  = f"Type: {VOXEL_TYPES[self.active_type][0]}"

        elif key == "scroll down":
            self.active_type = (self.active_type - 1) % len(VOXEL_TYPES)
            self.status_msg  = f"Type: {VOXEL_TYPES[self.active_type][0]}"

        elif key == "r":
            self._cycle_tint()

        # ── Operations ────────────────────────────────────────────────────
        elif key == "left mouse down":
            self._op_add()

        elif key == "right mouse down":
            self._op_remove()

        elif key == "middle mouse down" or key == "q":
            self._op_select()

        elif key == "f":
            self._op_flood_fill()

        elif key == "b":
            self._op_box_delete()

        elif key == "c":
            self._op_copy()

        elif key == "v":
            self._op_paste()

        elif key == "control+z" or key == "z" and held_keys["control"]:
            self._op_undo()

        # ── Mode toggles ──────────────────────────────────────────────────
        elif key == "1":
            self.mode = "add";    self.status_msg = "Mode: Add"
        elif key == "2":
            self.mode = "remove"; self.status_msg = "Mode: Remove"
        elif key == "3":
            self.mode = "paint";  self.status_msg = "Mode: Paint"
        elif key == "4":
            self.mode = "fill";   self.status_msg = "Mode: Flood Fill"
        elif key == "5":
            self.mode = "box";    self.status_msg = "Mode: Box Delete"

    # ────────────────────────────────────────────────────────────────────────
    # Operation 1 — Add Voxel
    # ────────────────────────────────────────────────────────────────────────

    def _op_add(self):
        hit = self._raycast_hit()
        if not hit:
            return

        # Place on the face normal of the hit voxel
        new_pos = self._snap(hit.entity.position + hit.normal)
        if self.world.has(new_pos):
            return

        v = self.world.add(new_pos, self.active_type, self.active_tint)
        self._push_undo(_UndoRecord("add", new_pos, self.active_type, self.active_tint))
        self.status_msg = f"Added {VOXEL_TYPES[self.active_type][0]}"

    # ────────────────────────────────────────────────────────────────────────
    # Operation 2 — Remove Voxel
    # ────────────────────────────────────────────────────────────────────────

    def _op_remove(self):
        hit = self._raycast_hit()
        if not hit or not isinstance(hit.entity, Voxel):
            return

        v   = hit.entity
        pos = v.grid_pos
        self._push_undo(_UndoRecord("remove", pos, v.type_index, v.tint_color))
        self.world.remove(pos)
        if self.selected_voxel is v:
            self.selected_voxel = None
        self.status_msg = "Removed voxel"

    # ────────────────────────────────────────────────────────────────────────
    # Operation 3 — Select Voxel
    # ────────────────────────────────────────────────────────────────────────

    def _op_select(self):
        # De-select previous
        if self.selected_voxel:
            self.selected_voxel.color = self.selected_voxel.tint_color
            self.selected_voxel.selected = False

        hit = self._raycast_hit()
        if not hit or not isinstance(hit.entity, Voxel):
            self.selected_voxel = None
            self.status_msg = "Deselected"
            return

        v = hit.entity
        v.selected = True
        v.color    = color.rgba(255, 255, 100, 200)   # gold highlight
        self.selected_voxel = v
        self.status_msg = f"Selected @ {v.grid_pos}"

    # ────────────────────────────────────────────────────────────────────────
    # Operation 4/5 — Change Type (scroll) / Change Tint (R)
    # ────────────────────────────────────────────────────────────────────────

    def _cycle_tint(self):
        self.tint_index  = (self.tint_index + 1) % len(TINT_PALETTE)
        self.active_tint = TINT_PALETTE[self.tint_index]

        # Also apply to the selected voxel if any
        if self.selected_voxel:
            old_tint = self.selected_voxel.tint_color
            self._push_undo(_UndoRecord(
                "paint", self.selected_voxel.grid_pos,
                self.selected_voxel.type_index, old_tint
            ))
            self.selected_voxel.set_tint(self.active_tint)

        self.status_msg = "Tint changed"

    # ────────────────────────────────────────────────────────────────────────
    # Operation 6 — Flood Fill Paint
    # ────────────────────────────────────────────────────────────────────────

    def _op_flood_fill(self):
        hit = self._raycast_hit()
        if not hit or not isinstance(hit.entity, Voxel):
            self.status_msg = "No target for fill"
            return

        origin   = hit.entity
        old_tint = origin.tint_color
        old_type = origin.type_index

        if old_tint == self.active_tint and old_type == self.active_type:
            return

        visited: set[tuple] = set()
        queue   = [origin.grid_pos]
        changed = []

        while queue:
            pos = queue.pop()
            if pos in visited:
                continue
            v = self.world.get(pos)
            if v is None:
                continue
            # Match by tint colour (flood fill criterion)
            if self._colors_approx_equal(v.tint_color, old_tint) \
               and v.type_index == old_type:
                visited.add(pos)
                changed.append(_UndoRecord("paint", pos, v.type_index, v.tint_color))
                v.set_type(self.active_type)
                v.set_tint(self.active_tint)
                for nb in self.world.neighbors(pos):
                    if nb.grid_pos not in visited:
                        queue.append(nb.grid_pos)

        if changed:
            self._push_undo(_UndoRecord("batch_remove", batch=changed))
            self.status_msg = f"Flood-filled {len(changed)} voxels"
        else:
            self.status_msg = "Fill: nothing to change"

    # ────────────────────────────────────────────────────────────────────────
    # Operation 7 — Box Delete
    # ────────────────────────────────────────────────────────────────────────

    def _op_box_delete(self):
        hit = self._raycast_hit()
        if not hit or not isinstance(hit.entity, Voxel):
            self.status_msg = "Box delete: aim at a voxel"
            return

        pos = hit.entity.grid_pos

        if self._box_corner_a is None:
            self._box_corner_a = pos
            self.status_msg    = f"Box corner A set @ {pos} — press B again for B"
            # Visual marker
            Entity(
                model="sphere", scale=0.25,
                color=color.red, position=Vec3(*pos),
                name="box_marker_a"
            )
        else:
            ax, ay, az = self._box_corner_a
            bx, by, bz = pos
            removed    = []

            for x in range(min(ax,bx), max(ax,bx)+1):
                for y in range(min(ay,by), max(ay,by)+1):
                    for z in range(min(az,bz), max(az,bz)+1):
                        v = self.world.get((x, y, z))
                        if v:
                            removed.append(_UndoRecord(
                                "remove", v.grid_pos, v.type_index, v.tint_color
                            ))
                            self.world.remove((x, y, z))

            # Clean up marker
            for e in scene.entities:
                if getattr(e, "name", "") == "box_marker_a":
                    destroy(e)

            if removed:
                self._push_undo(_UndoRecord("batch_remove", batch=removed))

            self._box_corner_a = None
            self.status_msg    = f"Box deleted {len(removed)} voxels"

    # ────────────────────────────────────────────────────────────────────────
    # Operation 8 — Copy Selection
    # ────────────────────────────────────────────────────────────────────────

    def _op_copy(self):
        if not self.selected_voxel:
            self.status_msg = "Nothing selected to copy"
            return

        origin = self.selected_voxel.grid_pos
        # Copy a 3×3×3 region around the selected voxel
        self._clipboard.clear()
        ox, oy, oz = origin
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    v = self.world.get((ox+dx, oy+dy, oz+dz))
                    if v:
                        self._clipboard.append({
                            "rel": (dx, dy, dz),
                            "type": v.type_index,
                            "tint": v.tint_color,
                        })

        self.status_msg = f"Copied {len(self._clipboard)} voxels"

    # ────────────────────────────────────────────────────────────────────────
    # Operation 9 — Paste Selection
    # ────────────────────────────────────────────────────────────────────────

    def _op_paste(self):
        if not self._clipboard:
            self.status_msg = "Clipboard is empty"
            return

        hit = self._raycast_hit()
        if not hit:
            self.status_msg = "Aim at a surface to paste"
            return

        origin  = self._snap(hit.entity.position + hit.normal)
        added   = []
        ox, oy, oz = origin

        for entry in self._clipboard:
            dx, dy, dz = entry["rel"]
            new_pos    = (ox+dx, oy+dy, oz+dz)
            if not self.world.has(new_pos):
                self.world.add(new_pos, entry["type"], entry["tint"])
                added.append(_UndoRecord("add", new_pos, entry["type"], entry["tint"]))

        if added:
            self._push_undo(_UndoRecord("batch_remove", batch=added))

        self.status_msg = f"Pasted {len(added)} voxels"

    # ────────────────────────────────────────────────────────────────────────
    # Operation 10 — Undo
    # ────────────────────────────────────────────────────────────────────────

    def _op_undo(self):
        if not self._undo_stack:
            self.status_msg = "Nothing to undo"
            return

        record = self._undo_stack.pop()

        if record.action == "add":
            self.world.remove(record.pos)
            self.status_msg = "Undo: removed voxel"

        elif record.action == "remove":
            self.world.add(record.pos, record.type_index, record.tint)
            self.status_msg = "Undo: restored voxel"

        elif record.action == "paint":
            v = self.world.get(record.pos)
            if v:
                v.set_type(record.type_index)
                v.set_tint(record.tint)
            self.status_msg = "Undo: reverted paint"

        elif record.action == "batch_remove":
            # Reverse a batch — reverse each sub-record
            for sub in reversed(record.batch):
                if sub.action == "add":
                    self.world.remove(sub.pos)
                elif sub.action == "remove":
                    self.world.add(sub.pos, sub.type_index, sub.tint)
                elif sub.action == "paint":
                    v = self.world.get(sub.pos)
                    if v:
                        v.set_type(sub.type_index)
                        v.set_tint(sub.tint)
            self.status_msg = f"Undo: batch ({len(record.batch)} ops)"

    # ────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ────────────────────────────────────────────────────────────────────────

    def _raycast_hit(self):
        """Return a valid RaycastHit hitting a Voxel, or None."""
        hit = raycast(
            camera.world_position,
            camera.forward,
            distance=RAYCAST_DISTANCE,
            ignore=(scene,),
        )
        return hit if hit.hit else None

    def _push_undo(self, record: _UndoRecord):
        self._undo_stack.append(record)

    @staticmethod
    def _snap(pos) -> tuple:
        return (int(round(pos.x)), int(round(pos.y)), int(round(pos.z)))

    @staticmethod
    def _colors_approx_equal(a: Color, b: Color, tol: float = 0.05) -> bool:
        return (abs(a.r - b.r) < tol and abs(a.g - b.g) < tol
                and abs(a.b - b.b) < tol)