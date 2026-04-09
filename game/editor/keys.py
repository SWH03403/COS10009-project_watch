from enum import IntEnum, auto
import pygame

import game
from game.world import Wall
from game.world.sector import WallType, WALL_COLOR
from .. import editor
from . import selection

class EditMode(IntEnum):
	NORMAL = auto()
	EXTEND = auto()
	CONNECT = auto()

def is_snap_enabled() -> bool:
	keys = pygame.key.get_pressed()
	return not (keys[pygame.K_LALT] or keys[pygame.K_RALT])

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

def set_wall_type(wall: Wall, typ: WallType) -> None:
	if typ == WallType.SKY:
		wall.neighbor = wall.color = None
	elif typ == WallType.SOLID:
		wall.neighbor = None
		if wall.color is None: wall.color = WALL_COLOR

def set_selection_wall_type(typ: WallType, onesided: bool) -> None:
	sel = editor.get_selection()
	if not isinstance(sel, selection.Wall): return
	level = game.get_level()

	wall = level.sectors[sel.sector_id].walls[sel.wall_idx]
	nb_wall = None
	if not onesided and wall.neighbor is not None:
		for nb_wall in level.sectors[wall.neighbor].walls:
			if nb_wall.neighbor == sel.sector_id: break
	if typ == WallType.NEIGHBOR:
		if nb_wall is None: return
	else:
		set_wall_type(wall, typ)
		if nb_wall is not None: set_wall_type(nb_wall, typ)

def handle_keydown(key: int) -> None:
	keys = pygame.key.get_pressed()
	shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

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
			if isinstance(editor.get_selection(), selection.Vertex):
				editor.set_mode(EditMode.CONNECT)
		case pygame.K_e:
			sel = editor.get_selection()
			if isinstance(sel, selection.Vertex) or isinstance(sel, selection.Wall):
				editor.set_mode(EditMode.EXTEND)
		case pygame.K_1:
			set_selection_wall_type(WallType.SOLID, shift)
		case pygame.K_2:
			set_selection_wall_type(WallType.NEIGHBOR, shift)
		case pygame.K_3:
			set_selection_wall_type(WallType.SKY, shift)
