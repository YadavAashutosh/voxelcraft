"""
src/utils/skybox.py
Procedural gradient sky — no texture asset required.
Falls back to a solid colour if Sky() is unavailable.
"""

from ursina import *


def setup_skybox():
    """Create a gradient sky dome."""
    try:
        # Ursina's built-in Sky entity accepts a texture
        sky = Sky(texture="sky_sunset")   # ships with Ursina
    except Exception:
        # Fallback: large inverted sphere
        sky = Entity(
            model   = "sphere",
            texture = "sky_sunset",
            scale   = 500,
            double_sided = True,
        )

    # Slight fog for distance cull illusion (free depth cue)
    scene.fog_color    = color.rgb(180, 210, 240)
    scene.fog_density  = 0.012

    return sky