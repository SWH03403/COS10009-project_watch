from enum import IntEnum, auto
import pygame
from pygame import Vector2

from .. import editor

ZOOM_STEP: float = .2

SELECTION_PADDING: int = 20

class DragMode(IntEnum):
	MOVING = auto()
	PANNING = auto()

class EditMode(IntEnum):
	ADD = auto()
	DIVIDE = auto()
	NORMAL = auto()

def world_to_screen(p: Vector2) -> Vector2:
	p = p.copy() * editor.get_scale()
	p.y *= -1
	return editor.get_origin() + p

def screen_to_world(p: Vector2) -> Vector2:
	p = p.copy() - editor.get_origin()
	p.y *= -1
	return p / editor.get_scale()

def is_shift_held() -> bool:
	keys = pygame.key.get_pressed()
	return keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

def get_snap_step() -> float:
	if is_shift_held(): return 1
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LALT] or keys[pygame.K_RALT]: return 0
	if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]: return 20
	return 5

# get closest screen coordinate that is on the snap grid of the world
def snap_to_grid(p: Vector2, is_screen: bool = False) -> Vector2:
	step = get_snap_step()
	if step == 0: return p.copy()
	if is_screen: p = screen_to_world(p)
	diff_x, diff_y = p.x % step, p.y % step
	p.x -= (diff_x - step) if diff_x > step / 2 else diff_x
	p.y -= (diff_y - step) if diff_y > step / 2 else diff_y
	return world_to_screen(p) if is_screen else p
