import pygame

import game
from game.world import Wall
from game.world.sector import WallType, set_wall_type
from .. import editor
from . import cache, selection
from .common import EditMode, is_shift_held

def insert_vertex() -> None:
	sel = editor.get_selection()
	if not isinstance(sel, selection.Wall): return
	level = game.get_level()

	vertex_id = len(level.vertexes)
	sector = level.sectors[sel.sector_id]
	wall = sector.walls[sel.wall_idx]

	# patch neighbor sector
	if wall.neighbor is not None:
		neighbor = level.sectors[wall.neighbor]
		nb_wall_idx = 0
		for i in range(1, len(neighbor.walls)):
			if neighbor.walls[i].neighbor == sel.sector_id:
				nb_wall_idx = i
				break
		neighbor.walls.insert(
			nb_wall_idx + 1,
			Wall(vertex=vertex_id, neighbor=sel.sector_id, color=neighbor.walls[nb_wall_idx].color)
		)

	left = level.vertexes[wall.vertex]
	right = level.vertexes[sector.walls[sel.wall_idx - len(sector.walls) + 1].vertex]
	level.vertexes.append((left + right) / 2)

	new_wall = Wall(vertex=vertex_id, neighbor=wall.neighbor, color=wall.color)
	sector.walls.insert(sel.wall_idx + 1, new_wall)

	editor.set_selection(selection.Vertex(id=vertex_id))

def set_selection_wall_type(typ: WallType, onesided: bool) -> None:
	sel = editor.get_selection()
	if not isinstance(sel, selection.Wall): return
	level = game.get_level()

	sector = level.sectors[sel.sector_id]
	wall = sector.walls[sel.wall_idx]
	left = wall.vertex
	right = sector.walls[sel.wall_idx - len(sector.walls) + 1].vertex

	nb_id = nb_wall = None
	for ref in cache.get_sectors(left, right):
		# FIX: verify walls are opposite facing
		if ref.id != sel.sector_id:
			nb_id = ref.id
			nb_wall = level.sectors[ref.id].walls[ref.wall_idx]
			break

	onesided |= nb_wall is None
	if typ == WallType.NEIGHBOR:
		set_wall_type(wall, WallType.SOLID)
		wall.neighbor = nb_id
		if not onesided:
			set_wall_type(nb_wall, WallType.SOLID)
			nb_wall.neighbor = sel.sector_id
	else:
		set_wall_type(wall, typ)
		if not onesided: set_wall_type(nb_wall, typ)

	cache.set_expired_walls() # NOTE: this must only be called after wall types are changed

def handle_keydown(key: int) -> None:
	shift = is_shift_held()

	match key:
		case pygame.K_q | pygame.K_ESCAPE:
			if editor.get_mode() == EditMode.NORMAL:
				game.die()
				return
			editor.set_mode(EditMode.NORMAL)

		case pygame.K_LEFTBRACKET:
			game.set_editor(False)
		case pygame.K_i:
			insert_vertex()
		case pygame.K_d:
			if isinstance(editor.get_selection(), selection.Vertex):
				editor.set_mode(EditMode.DIVIDE)
		case pygame.K_c:
			sel = editor.get_selection()
			if isinstance(sel, (selection.Vertex, selection.Wall)):
				editor.set_mode(EditMode.ADD)
		case pygame.K_1:
			set_selection_wall_type(WallType.SOLID, shift)
		case pygame.K_2:
			set_selection_wall_type(WallType.NEIGHBOR, shift)
		case pygame.K_3:
			set_selection_wall_type(WallType.SKY, shift)
