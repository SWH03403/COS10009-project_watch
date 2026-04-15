from copy import deepcopy
import pygame
from pygame import Vector2
from pygame.event import Event

import game
from game.utils.math import is_polygon_clockwise
from game.world import Wall, default_sector
from .. import editor
from . import cache, selection, ui
from .common import DragMode, EditMode, ZOOM_STEP, screen_to_world, snap_to_grid
from .selection import Selection, is_world_element

def move_selection(mouse: Vector2) -> None:
	sel = editor.get_selection()
	vertexes = selection.get_vertexes(sel)
	diff = editor.move_drag(mouse, vertexes[0])
	if is_world_element(sel) and (diff.x != 0 or diff.y != 0):
		cache.set_expired()
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

def divide_sector(sel: Selection) -> None:
	cache.set_expired()

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

	# connect neighbors to new sector
	for new_wall in new_walls:
		if new_wall.neighbor is None or new_wall.neighbor == sector_id: continue
		walls = level.sectors[new_wall.neighbor].walls
		# shared neighbor of old and new
		is_shared = False
		for i, wall in enumerate(walls):
			if wall.neighbor == sector_id and walls[i - 1].neighbor == sector_id:
				wall.neighbor = new_sector_id
				is_shared = True
				break
		if is_shared: continue
		for wall in walls:
			if wall.neighbor == sector_id:
				wall.neighbor = new_sector_id
				break

	# insert sector into level
	sector.walls = []
	new_sector = deepcopy(sector)
	sector.walls = old_walls
	new_sector.walls = new_walls
	level.sectors.append(new_sector)

def add_sector() -> None:
	cache.set_expired()
	level = game.get_level()
	first = editor.get_selection().id

	next_id = len(level.vertexes)
	new_vertexes = editor.get_extensions()
	if len(new_vertexes) < 2: return
	new_ids = [first]
	for vertex in new_vertexes:
		if isinstance(vertex, int):
			new_ids.append(vertex)
			continue
		level.vertexes.append(vertex)
		new_ids.append(next_id)
		next_id += 1
	new_vertexes.clear()

	sector = default_sector()
	sector.walls = [Wall(vertex=v_id) for v_id in new_ids]
	level.sectors.append(sector)

def select(mouse: Vector2) -> None:
	sel = selection.get_nearest(mouse)
	cur = editor.get_selection()
	mode = editor.get_mode()
	add_mode = mode == EditMode.ADD
	if sel is None and not add_mode:
		drag(mouse, start=DragMode.PANNING)
		editor.set_selection(sel)
		return
	elif sel is not None and sel == cur:
		drag(mouse, start=DragMode.MOVING)

	if mode == EditMode.DIVIDE:
		if isinstance(sel, selection.Vertex): divide_sector(sel)
		editor.set_mode(EditMode.NORMAL)
	elif add_mode:
		buf = editor.get_extensions()
		if isinstance(sel, selection.Vertex):
			if sel == cur:
				add_sector()
				editor.set_mode(EditMode.NORMAL)
			else:
				buf.append(sel.id)
		elif sel is None:
			buf.append(snap_to_grid(screen_to_world(Vector2(pygame.mouse.get_pos()))))
		return

	editor.set_selection(sel)

def handle_mouse_event(event: Event) -> None:
	if ui.on_mouse_event(event): return

	keys = pygame.key.get_pressed()
	space = keys[pygame.K_SPACE]

	match event.type:
		case pygame.MOUSEBUTTONDOWN:
			match event.button:
				case pygame.BUTTON_LEFT:
					if space: drag(event.pos, start=DragMode.PANNING)
					else: select(event.pos)
				case pygame.BUTTON_RIGHT:
					if editor.get_mode() == EditMode.ADD:
						parts = editor.get_extensions()
						if len(parts) > 0: parts.pop()
						else: editor.set_mode(EditMode.NORMAL)
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
