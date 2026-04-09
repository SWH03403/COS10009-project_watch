from enum import IntEnum, auto
import pygame
from pygame import Vector2

from .. import editor

SNAP_STEP: float = 5
ZOOM_STEP: float = .2

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

def is_alt_held() -> bool:
	keys = pygame.key.get_pressed()
	return keys[pygame.K_LALT] or keys[pygame.K_RALT]

def is_shift_held() -> bool:
	keys = pygame.key.get_pressed()
	return keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

# get closest screen coordinate that is on the snap grid of the world
def snap_to_grid(p: Vector2, is_screen: bool = False) -> Vector2:
	if is_alt_held(): return p.copy()
	if is_screen: p = screen_to_world(p)
	diff_x, diff_y = p.x % SNAP_STEP, p.y % SNAP_STEP
	p.x -= (diff_x - SNAP_STEP) if diff_x > SNAP_STEP / 2 else diff_x
	p.y -= (diff_y - SNAP_STEP) if diff_y > SNAP_STEP / 2 else diff_y
	return world_to_screen(p) if is_screen else p
