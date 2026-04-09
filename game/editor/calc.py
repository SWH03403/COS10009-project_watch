from pygame import Vector2

from .. import editor
from .keys import is_snap_enabled

SNAP_STEP: float = 5

def world_to_screen(p: Vector2) -> Vector2:
	p = p.copy() * editor.get_scale()
	p.y *= -1
	return editor.get_origin() + p

def screen_to_world(p: Vector2) -> Vector2:
	p = p.copy() - editor.get_origin()
	p.y *= -1
	return p / editor.get_scale()

# get closest screen coordinate that is on the snap grid of the world
# NOTE: this function takes and outputs world coordinate
def snap_to_grid(p: Vector2) -> Vector2:
	if not is_snap_enabled(): return p.copy()
	diff_x, diff_y = p.x % SNAP_STEP, p.y % SNAP_STEP
	p.x -= (diff_x - SNAP_STEP) if diff_x > SNAP_STEP / 2 else diff_x
	p.y -= (diff_y - SNAP_STEP) if diff_y > SNAP_STEP / 2 else diff_y
	return p
