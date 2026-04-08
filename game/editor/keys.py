from enum import IntEnum, auto
import pygame

import game
from game.world import Wall
from .. import editor
from . import selection

class EditMode(IntEnum):
	NORMAL = auto()
	CREATE = auto()
	CONNECT = auto()

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

def handle_keydown(key: int) -> None:
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
		case pygame.K_c:
			editor.set_mode(EditMode.CONNECT)
		case pygame.K_n:
			editor.set_mode(EditMode.CREATE)
