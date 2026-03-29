"""src/ui/crosshair.py — Minimal dot crosshair."""
from ursina import *

class Crosshair:
    def __init__(self):
        # Horizontal bar
        Entity(parent=camera.ui, model="quad",
               color=color.rgba(255,255,255,180),
               scale=(0.025, 0.002), position=(0,0))
        # Vertical bar
        Entity(parent=camera.ui, model="quad",
               color=color.rgba(255,255,255,180),
               scale=(0.002, 0.025), position=(0,0))
        # Centre dot
        Entity(parent=camera.ui, model="circle",
               color=color.rgba(255,255,255,200),
               scale=0.003, position=(0,0))