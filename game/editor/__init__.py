from dataclasses import dataclass
import pygame
from pygame import Vector2
from pygame.event import Event
from pygame.math import clamp

import game
from game import engine
from game.utils import unscale_mouse_position
from game.world import Level
from . import render
from .selection import Selection, find_nearest_item

ZOOM_STEP: float = .2
MIN_ZOOM: float = -1
MAX_ZOOM: float = 3

@dataclass
class MapEditor:
	level: Level
	zoom: float
	origin: Vector2 # position of world coordinate (0, 0) on the screen

	pan_start: Vector2 | None = None
	pan_origin: Vector2 | None = None
	selection: Selection | int | None = None

I: MapEditor = None

def init() -> None:
	global I
	origin = Vector2(engine.get_screen().size) / 2
	I = MapEditor(level=game.get_level(), zoom=0, origin=origin)

def get_init() -> bool:
	return I is not None

def get_scale() -> float:
	return 2**I.zoom

def get_zoom() -> float:
	return I.zoom

def get_origin() -> Vector2:
	return I.origin

def get_selection() -> Selection:
	return I.selection

def handle_keydown(key: int) -> None:
	match key:
		case pygame.K_ESCAPE:
			game.die()
		case pygame.K_q | pygame.K_LEFTBRACKET:
			game.set_editor(False)

def handle_keys() -> None:
	keys = pygame.key.get_pressed()

def select(pos: tuple[int, int]) -> None:
	I.selection = find_nearest_item(Vector2(pos))

def pan(pos: tuple[int, int], start: bool, end: bool) -> None:
	I.selection = None
	pos = Vector2(pos)
	if start:
		I.pan_start = pos
		I.pan_origin = I.origin.copy()
		return
	if not isinstance(I.pan_start, Vector2): return
	I.origin = (pos - I.pan_start) + I.pan_origin
	if end:
		I.pan_start = None
		I.pan_origin = None

# anchor to mouse position
def zoom(pos: tuple[int, int], enlarge: bool) -> None:
	old_fact = get_scale()
	step = ZOOM_STEP if enlarge else -ZOOM_STEP
	I.zoom = clamp(I.zoom + step, MIN_ZOOM, MAX_ZOOM)
	fact = get_scale() / old_fact
	pos = unscale_mouse_position(Vector2(pos))
	I.origin += (pos - I.origin) * (1 - fact)

def handle_event(event: Event) -> None:
	keys = pygame.key.get_pressed()
	space = keys[pygame.K_SPACE]

	match event.type:
		case pygame.MOUSEBUTTONDOWN:
			match event.button:
				case pygame.BUTTON_LEFT:
					if space: pan(event.pos, True, False)
					else: select(event.pos)
				case pygame.BUTTON_WHEELDOWN:
					zoom(event.pos, False)
				case pygame.BUTTON_WHEELUP:
					zoom(event.pos, True)
		case pygame.MOUSEBUTTONUP:
			match event.button:
				case pygame.BUTTON_LEFT:
					if space: pan(event.pos, False, True)
		case pygame.MOUSEMOTION:
			pan(event.pos, False, not space)
		case pygame.KEYDOWN:
			handle_keydown(event.key)
