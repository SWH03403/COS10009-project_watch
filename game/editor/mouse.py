from enum import IntEnum, auto
import pygame
from pygame import Vector2
from pygame.event import Event

from .. import editor
from . import selection

ZOOM_STEP: float = .2

class DragMode(IntEnum):
	PANNING = auto()
	MOVING = auto()

def move_selection(mouse: Vector2) -> None:
	diff = editor.move_drag(mouse)
	vertexes = selection.get_vertexes(editor.get_selection())
	for v in vertexes:
		v.update((v + diff))

def drag(mouse: Vector2, /, start: DragMode | None = None, end: bool = False) -> None:
	if start is not None: return editor.set_drag(start, mouse)
	match editor.get_drag_mode():
		case DragMode.PANNING:
			editor.pan(mouse)
		case DragMode.MOVING:
			move_selection(mouse)
	if end: editor.reset_drag()

# anchor to mouse position
def zoom(mouse: Vector2, enlarge: bool) -> None:
	old_fact = editor.get_scale()
	editor.set_zoom(editor.get_zoom() + (ZOOM_STEP if enlarge else -ZOOM_STEP))
	fact = editor.get_scale() / old_fact
	origin = editor.get_origin()
	editor.set_origin(origin + (mouse - origin) * (1 - fact))

def select(mouse: Vector2) -> None:
	sel = selection.get_nearest(mouse)
	if sel is not None:
		drag(mouse, start=DragMode.MOVING)
	editor.set_selection(sel)

def handle_mouse_event(event: Event) -> None:
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
			drag(Vector2(event.pos))
