import pygame

import game
from game.world import Wall
from .. import editor
from . import selection

def insert_vertex() -> None:
	sel = editor.get_selection()
	if not isinstance(sel, selection.Wall): return
	level = game.get_level()

	vertex_id = len(level.vertexes)
	sector = level.sectors[sel.sector_id]
	wall = sector.walls[sel.wall_idx]

	# patch neighbor sector
	if wall.neighbor is not None:
		...

	left = level.vertexes[wall.vertex]
	right = level.vertexes[sector.walls[sel.wall_idx - len(sector.walls) + 1].vertex]
	level.vertexes.append((left + right) / 2)

	new_wall = Wall(vertex=vertex_id, neighbor=wall.neighbor, color=wall.color)
	sector.walls.insert(sel.wall_idx + 1, new_wall)

	editor.set_selection(selection.Vertex(id=vertex_id))

def handle_keydown(key: int) -> None:
	match key:
		case pygame.K_q | pygame.K_ESCAPE:
			game.die()
		case pygame.K_LEFTBRACKET:
			game.set_editor(False)
		case pygame.K_i:
			insert_vertex()
