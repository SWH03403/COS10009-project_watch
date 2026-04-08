from dataclasses import dataclass, field
from enum import IntEnum, auto
import pygame
from pygame import Vector2
from pygame.event import Event
from pygame.math import clamp

import game
from game import engine
from game.utils import unscale_mouse_position
from game.world import Level
from . import render
from .selection import Selection, find_nearest_item, get_all_vertexes

ZOOM_STEP: float = .2
MIN_ZOOM: float = -1
MAX_ZOOM: float = 3

class DragMode(IntEnum):
	PANNING = auto()
	MOVING = auto()

@dataclass
class MapEditor:
	level: Level
	zoom: float
	origin: Vector2 # position of world coordinate (0, 0) on the screen

	drag_mode: DragMode | None = None
	drag_origin: Vector2 | None = None
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
		case pygame.K_q | pygame.K_ESCAPE:
			game.die()
		case pygame.K_LEFTBRACKET:
			game.set_editor(False)

def handle_keys() -> None:
	keys = pygame.key.get_pressed()

def move_selection(mouse: Vector2) -> None:
	diff = mouse - I.drag_origin
	diff.y *= -1
	diff /= get_scale()
	vertexes = get_all_vertexes(I.selection)
	for v in vertexes:
		v.update((v + diff))
	I.drag_origin = mouse

def drag(pos: tuple[int, int], /, start: DragMode | None = None, end: bool = False) -> None:
	pos = Vector2(pos)
	if start is not None:
		I.drag_mode = start
		I.drag_origin = pos
		I.pan_origin = I.origin.copy()
		return
	if not isinstance(I.drag_origin, Vector2): return
	match I.drag_mode:
		case DragMode.PANNING:
			I.origin = (pos - I.drag_origin) + I.pan_origin
		case DragMode.MOVING:
			move_selection(pos)
	if not end: return
	I.drag_mode = None
	I.drag_origin = None
	I.pan_origin = None

# anchor to mouse position
def zoom(pos: tuple[int, int], enlarge: bool) -> None:
	old_fact = get_scale()
	step = ZOOM_STEP if enlarge else -ZOOM_STEP
	I.zoom = clamp(I.zoom + step, MIN_ZOOM, MAX_ZOOM)
	fact = get_scale() / old_fact
	pos = unscale_mouse_position(Vector2(pos))
	I.origin += (pos - I.origin) * (1 - fact)

def select(pos: tuple[int, int]) -> None:
	new_selection = find_nearest_item(Vector2(pos))
	if I.selection == new_selection and new_selection is not None:
		drag(pos, start=DragMode.MOVING)
	I.selection = new_selection

def handle_event(event: Event) -> None:
	keys = pygame.key.get_pressed()
	space = keys[pygame.K_SPACE]

	match event.type:
		case pygame.MOUSEBUTTONDOWN:
			match event.button:
				case pygame.BUTTON_LEFT:
					if space: drag(event.pos, start=DragMode.PANNING)
					else: select(event.pos)
				case pygame.BUTTON_WHEELDOWN:
					zoom(event.pos, False)
				case pygame.BUTTON_WHEELUP:
					zoom(event.pos, True)
		case pygame.MOUSEBUTTONUP:
			match event.button:
				case pygame.BUTTON_LEFT:
					drag(event.pos, end=True)
		case pygame.MOUSEMOTION:
			drag(event.pos)
		case pygame.KEYDOWN:
			handle_keydown(event.key)
