"""
src/utils/lighting.py
Directional sun + ambient fill.
Ursina wraps Panda3D's lighting system, so we call Panda3D directly
for the directional light to get proper shadows.
"""

from ursina import *
from ursina.lights import DirectionalLight, AmbientLight


def setup_lighting():
    # ── Sun (directional) with soft shadows ─────────────────────────────────
    sun = DirectionalLight(
        shadows    = True,
        shadow_map_resolution = (2048, 2048),
    )
    sun.look_at(Vec3(1, -1.5, -1))       # angle from upper-right
    sun.color = color.rgb(255, 245, 200)  # warm sunlight

    # ── Ambient fill to prevent pitch-black undersides ───────────────────────
    ambient = AmbientLight()
    ambient.color = color.rgba(100, 130, 180, 80)   # cool sky bounce

    return sun, ambient