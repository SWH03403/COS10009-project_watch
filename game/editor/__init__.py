from dataclasses import dataclass, field
import pygame
from pygame import Vector2
from pygame.event import Event
from pygame.math import clamp

import game
from game import engine
from game.world import Level
from . import cache, render
from .common import EditMode, snap_to_grid
from .keys import handle_keydown
from .mouse import DragMode, handle_mouse_event
from .selection import Selection

DEFAULT_ZOOM = 2
MIN_ZOOM: float = -1
MAX_ZOOM: float = 3

@dataclass
class MapEditor:
	origin: Vector2 # position of world coordinate (0, 0) on the screen
	zoom: float = DEFAULT_ZOOM

	mode: EditMode = EditMode.NORMAL
	drag_mode: DragMode | None = None
	drag_origin: Vector2 | None = None
	selection: Selection = None

	# "add" mode
	add_parts: list[Vector2 | int] = field(default_factory=list)

I: MapEditor = None

def init() -> None:
	cache.init()
	render.init()

	global I
	I = MapEditor(origin=Vector2(engine.get_screen().size) / 2)

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

def get_drag_mode() -> DragMode:
	return I.drag_mode

def get_mode() -> EditMode:
	return I.mode

def get_extensions() -> list[Vector2 | int]:
	return I.add_parts

def set_zoom(zoom: float) -> None:
	I.zoom = clamp(zoom, MIN_ZOOM, MAX_ZOOM)

def set_origin(origin: Vector2) -> None:
	I.origin = origin

def set_selection(sel: Selection) -> None:
	I.selection = sel

def set_drag(mode: DragMode, origin: Vector2) -> None:
	I.drag_mode = mode
	I.drag_origin = origin

def reset_drag() -> None:
	I.drag_mode = None
	I.drag_origin = None

def move_drag(new_origin: Vector2, align_target: Vector2) -> Vector2:
	diff = new_origin - I.drag_origin
	diff.y *= -1
	diff /= get_scale()
	diff = snap_to_grid(align_target + diff) - align_target
	revert = diff * get_scale()
	revert.y *= -1
	I.drag_origin += revert
	return diff

def pan(target: Vector2) -> None:
	I.origin += target - I.drag_origin
	I.drag_origin = target

def set_mode(mode: EditMode) -> None:
	I.mode = mode
	if mode == EditMode.NORMAL: I.add_parts.clear()

def handle_event(event: Event) -> None:
	match event.type:
		case pygame.MOUSEBUTTONDOWN | pygame.MOUSEBUTTONUP | pygame.MOUSEMOTION:
			event.pos = Vector2(event.pos)
			if hasattr(event, "button"):
				# fix bug where event.pos return scaled coordinte
				if event.button in [pygame.BUTTON_WHEELDOWN, pygame.BUTTON_WHEELUP]:
					event.pos = Vector2(pygame.mouse.get_pos())
			handle_mouse_event(event)
		case pygame.KEYDOWN:
			handle_keydown(event.key)
