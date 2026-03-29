from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from src.core.voxel_manager import VoxelManager
from src.core.world import World
from src.ui.hud import HUD
from src.ui.crosshair import Crosshair
from src.utils.lighting import setup_lighting
from src.utils.skybox import setup_skybox
from src.utils.constants import TARGET_FPS, PLAYER_SPEED, PLAYER_JUMP, MOUSE_SENSITIVITY

app = Ursina(
    title="VoxelCraft",
    borderless=False,
    fullscreen=False,
    size=(1280, 720),
    vsync=True,
    development_mode=False,
)

window.fps_counter.enabled = False
window.exit_button.visible = False
window.color = color.black
application.target_frame_rate = TARGET_FPS

setup_skybox()
setup_lighting()

world   = World()
manager = VoxelManager(world)

player = FirstPersonController(
    position=(0, 3, 0),
    speed=PLAYER_SPEED,
    jump_height=PLAYER_JUMP,
    mouse_sensitivity=Vec2(MOUSE_SENSITIVITY, MOUSE_SENSITIVITY),
)
player.cursor.visible = False

hud       = HUD(manager)
crosshair = Crosshair()

world.generate_flat_floor(size=20, y=0)

def update():
    manager.update()
    hud.update()

def input(key):
    manager.handle_input(key)

app.run()