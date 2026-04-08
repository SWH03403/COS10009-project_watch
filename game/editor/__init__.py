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
from . import render, selection
from .keys import handle_keydown
from .selection import Selection

ZOOM_STEP: float = .2
MIN_ZOOM: float = -1
MAX_ZOOM: float = 3

class DragMode(IntEnum):
	PANNING = auto()
	MOVING = auto()

class EditMode(IntEnum):
	NORMAL = auto()
	CREATE = auto()

@dataclass
class MapEditor:
	level: Level
	zoom: float
	origin: Vector2 # position of world coordinate (0, 0) on the screen

	mode: EditMode = EditMode.NORMAL
	drag_mode: DragMode | None = None
	drag_origin: Vector2 | None = None
	selection: Selection | int | None = None

	# "create" mode
	origin_vertex: int = 0
	pending_create: list[Vector2] = field(default_factory=list)

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

def get_mode() -> EditMode:
	return I.mode

def set_selection(sel: Selection) -> None:
	I.selection = sel

def move_selection(mouse: Vector2) -> None:
	diff = mouse - I.drag_origin
	diff.y *= -1
	diff /= get_scale()
	vertexes = selection.get_vertexes(I.selection)
	for v in vertexes:
		v.update((v + diff))
	I.drag_origin = mouse

def drag(mouse: Vector2, /, start: DragMode | None = None, end: bool = False) -> None:
	if start is not None:
		I.drag_mode = start
		I.drag_origin = mouse
		return
	if not isinstance(I.drag_origin, Vector2): return
	match I.drag_mode:
		case DragMode.PANNING:
			I.origin += mouse - I.drag_origin
			I.drag_origin = mouse
		case DragMode.MOVING:
			move_selection(mouse)
	if not end: return
	I.drag_mode = None
	I.drag_origin = None
	I.pan_origin = None

# anchor to mouse position
def zoom(mouse: Vector2, enlarge: bool) -> None:
	old_fact = get_scale()
	step = ZOOM_STEP if enlarge else -ZOOM_STEP
	I.zoom = clamp(I.zoom + step, MIN_ZOOM, MAX_ZOOM)
	fact = get_scale() / old_fact
	pos = unscale_mouse_position(mouse)
	I.origin += (pos - I.origin) * (1 - fact)

def select(mouse: Vector2) -> None:
	new_selection = selection.get_nearest(mouse)
	if I.selection == new_selection and new_selection is not None:
		drag(mouse, start=DragMode.MOVING)
	I.selection = new_selection

def handle_event(event: Event) -> None:
	keys = pygame.key.get_pressed()
	space = keys[pygame.K_SPACE]

	match event.type:
		case pygame.MOUSEBUTTONDOWN:
			mouse = Vector2(event.pos)
			match event.button:
				case pygame.BUTTON_LEFT:
					if space: drag(mouse, start=DragMode.PANNING)
					else: select(mouse)
				case pygame.BUTTON_WHEELDOWN:
					zoom(mouse, False)
				case pygame.BUTTON_WHEELUP:
					zoom(mouse, True)
		case pygame.MOUSEBUTTONUP:
			mouse = Vector2(event.pos)
			match event.button:
				case pygame.BUTTON_LEFT:
					drag(mouse, end=True)
		case pygame.MOUSEMOTION:
			drag(Vector2(event.pos))
		case pygame.KEYDOWN:
			handle_keydown(event.key)
