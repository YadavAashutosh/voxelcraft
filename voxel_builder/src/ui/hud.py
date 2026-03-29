from ursina import *
from src.utils.constants import VOXEL_TYPES, UI_BG, UI_ACCENT, UI_TEXT, UI_WARN


class HUD:
    def __init__(self, manager):
        self.manager = manager
        self._fps_samples = []
        self._frame = 0

        # Panel background
        self._panel = Entity(
            parent   = camera.ui,
            model    = "quad",
            color    = UI_BG,
            scale    = (0.36, 0.20),
            position = (-0.56, -0.40),
        )

        # Block preview swatch
        self._swatch = Entity(
            parent   = camera.ui,
            model    = "quad",
            scale    = 0.055,
            position = (-0.68, -0.36),
            color    = color.white,
        )

        # Labels
        self._type_lbl = Text(
            text     = "",
            position = (-0.62, -0.33),
            scale    = 1.1,
            color    = UI_ACCENT,
            parent   = camera.ui,
            origin   = (-0.5, 0),
        )

        self._mode_lbl = Text(
            text     = "",
            position = (-0.62, -0.38),
            scale    = 0.95,
            color    = UI_TEXT,
            parent   = camera.ui,
            origin   = (-0.5, 0),
        )

        self._status_lbl = Text(
            text     = "",
            position = (-0.62, -0.43),
            scale    = 0.85,
            color    = UI_WARN,
            parent   = camera.ui,
            origin   = (-0.5, 0),
        )

        # FPS counter
        self._fps_lbl = Text(
            text     = "FPS: --",
            position = (0.64, 0.46),
            origin   = (0.5, 0),
            scale    = 1.0,
            color    = UI_ACCENT,
            parent   = camera.ui,
        )

        # Keybind hints
        hints = "[1-5] Modes  [Scroll] Type  [R] Tint\n[F] Fill  [B] Box  [C] Copy  [V] Paste\n[Q/MMB] Select  [Ctrl+Z] Undo"
        self._hint_lbl = Text(
            text     = hints,
            position = (-0.85, 0.46),
            scale    = 0.7,
            color    = color.rgba(255, 255, 255, 140),
            parent   = camera.ui,
            origin   = (-0.5, 0),
        )

    def update(self):
        m = self.manager

        name, base_color, _ = VOXEL_TYPES[m.active_type]
        self._type_lbl.text  = f"  {name}"
        self._swatch.color   = m.active_tint
        self._mode_lbl.text  = f"  {m.mode.upper()} MODE"

        if m.status_msg:
            self._status_lbl.text = f"  {m.status_msg}"
            self._frame = 0
        else:
            self._frame += 1
            if self._frame > 120:
                self._status_lbl.text = ""

        m.status_msg = ""

        self._fps_samples.append(1 / max(time.dt, 0.0001))
        if len(self._fps_samples) > 30:
            self._fps_samples.pop(0)
        avg_fps = sum(self._fps_samples) / len(self._fps_samples)
        self._fps_lbl.text  = f"FPS: {int(avg_fps)}"
        self._fps_lbl.color = (
            color.lime   if avg_fps >= 60 else
            color.yellow if avg_fps >= 30 else
            color.red
        )