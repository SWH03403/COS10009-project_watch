from copy import deepcopy
from enum import IntEnum, auto
import pygame
from pygame import Vector2
from pygame.event import Event

import game
from game.world import Sector
from .. import editor
from . import selection
from .keys import EditMode
from .selection import Selection

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

def connect_vertexes(sel: Selection) -> None:
	level = game.get_level()
	cur, sel = editor.get_selection().id, sel.id

	# find the first sector that contains both vertexes
	sector_id, vertexes = None, None
	for i, sector in enumerate(level.sectors):
		vertexes = [wall.vertex for wall in sector.walls]
		if cur in vertexes and sel in vertexes:
			sector_id = i
			break
	if sector_id is None: return
	sector = level.sectors[sector_id]

	# check if points are consecutive
	left, right = vertexes.index(cur), vertexes.index(sel)
	if left > right: left, right = right, left
	if right - left <= 1 or right - left == len(sector.walls) - 1: return

	# get sector vertexes
	old_walls = sector.walls[:left + 1] + sector.walls[right:]
	new_walls = [deepcopy(sector.walls[left])]
	new_walls.extend(sector.walls[left + 1:right])
	new_walls.append(deepcopy(sector.walls[right]))
	new_sector_id = len(level.sectors)

	# connect sectors to each others
	old_walls[left].neighbor = new_sector_id
	new_walls[-1].neighbor = sector_id

	# insert sector into level
	sector.walls = []
	new_sector = deepcopy(sector)
	sector.walls = old_walls
	new_sector.walls = new_walls
	level.sectors.append(new_sector)

def select(mouse: Vector2) -> None:
	sel = selection.get_nearest(mouse)
	if sel is not None:
		drag(mouse, start=DragMode.MOVING)

	if editor.get_mode() == EditMode.CONNECT:
		if isinstance(sel, selection.Vertex): connect_vertexes(sel)
		editor.set_mode(EditMode.NORMAL)

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
