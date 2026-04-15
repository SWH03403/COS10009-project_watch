import pygame
from pygame import Vector2

import game
from game.assets import savers
from game.entities import player
from game.world import Spawn
from game.world.sector import Wall, WallType, set_wall_type
from .. import editor
from . import cache, selection
from .cache import SectorRef
from .common import EditMode, is_shift_held, screen_to_world, snap_to_grid

def get_neighbor_ref() -> SectorRef | None:
	sel = editor.get_selection()
	if not isinstance(sel, selection.Wall): return
	level = game.get_level()
	sector = level.sectors[sel.sector_id]
	left = sector.walls[sel.wall_idx].vertex
	right = sector.walls[sel.wall_idx - len(sector.walls) + 1].vertex

	for ref in cache.get_sectors(left, right):
		# FIX: verify walls are opposite facing
		if ref.id != sel.sector_id: return ref

def insert_vertex() -> None:
	cache.set_expired()
	sel = editor.get_selection()
	level = game.get_level()
	if sel is None:
		cache.set_expired_walls()
		vertex = snap_to_grid(screen_to_world(Vector2(pygame.mouse.get_pos())))
		game.get_level().vertexes.append(vertex)
		return

	if not isinstance(sel, selection.Wall): return
	ref = get_neighbor_ref() # NOTE: find connection **only** before the wall is separated

	# expand selection
	vertex_id = len(level.vertexes)
	sector = level.sectors[sel.sector_id]
	wall = sector.walls[sel.wall_idx]

	# insert new vertex in middle of wall
	left = level.vertexes[wall.vertex]
	right = level.vertexes[sector.walls[sel.wall_idx - len(sector.walls) + 1].vertex]
	level.vertexes.append(snap_to_grid((left + right) / 2))

	# create wall for selected sector
	new_wall = Wall(vertex=vertex_id, neighbor=wall.neighbor, color=wall.color)
	sector.walls.insert(sel.wall_idx + 1, new_wall)

	# patch neighbor
	if ref is None: return
	sector = level.sectors[ref.id]
	wall = sector.walls[ref.wall_idx]
	new_wall = Wall(vertex=vertex_id, neighbor=wall.neighbor, color=wall.color)
	sector.walls.insert(ref.wall_idx + 1, new_wall)

def delete() -> None:
	level = game.get_level()
	sel = editor.get_selection()
	if isinstance(sel, selection.Vertex):
		level.vertexes.pop(sel.id)
		for sector in level.sectors:
			for i in range(len(sector.walls) - 1, -1, -1):
				wall = sector.walls[i]
				if wall.vertex == sel.id: sector.walls.pop(i)
				elif wall.vertex > sel.id: wall.vertex -= 1
	elif isinstance(sel, selection.Sector):
		level.sectors.pop()
	editor.set_selection(None)
	cache.set_expired()

def set_selection_wall_type(typ: WallType, onesided: bool) -> None:
	sel = editor.get_selection()
	if not isinstance(sel, selection.Wall): return
	ref = get_neighbor_ref()

	level = game.get_level()
	wall = level.sectors[sel.sector_id].walls[sel.wall_idx]
	nb_wall = None if ref is None else level.sectors[ref.id].walls[ref.wall_idx]

	onesided |= nb_wall is None
	if typ == WallType.NEIGHBOR:
		set_wall_type(wall, WallType.SOLID)
		wall.neighbor = None if ref is None else ref.id
		if not onesided:
			set_wall_type(nb_wall, WallType.SOLID)
			nb_wall.neighbor = sel.sector_id
	else:
		set_wall_type(wall, typ)
		if not onesided: set_wall_type(nb_wall, typ)

	cache.set_expired_walls() # NOTE: this must only be called after wall types are changed

def switch_wall_side() -> None:
	ref = get_neighbor_ref()
	if ref is None: return
	editor.set_selection(selection.Wall(sector_id=ref.id, wall_idx=ref.wall_idx))

def reverse_sector_walls() -> None:
	sel = editor.get_selection()
	level = game.get_level()
	if not isinstance(sel, selection.Sector): return

	sector = level.sectors[sel.id]
	n_walls = len(sector.walls)
	for i in range(1, n_walls // 2):
		a, b = sector.walls[i], sector.walls[-i]
		a.vertex, b.vertex = b.vertex, a.vertex
	for i in range(0, n_walls // 2):
		a, b = sector.walls[i], sector.walls[-i - 1]
		a.color, b.color = b.color, a.color
		a.neighbor, b.neighbor = b.neighbor, a.neighbor
	cache.set_expired()

def save_level() -> None:
	path = savers.level(*game.get_named_level())
	print(f"saved to: {path}")

def place_spawn() -> None:
	sel = editor.get_selection()
	if not isinstance(sel, selection.Sector): return
	print("placing spawn")
	position = snap_to_grid(screen_to_world(Vector2(pygame.mouse.get_pos())))
	spawn = Spawn(sector=sel.id, position=position, angle=0)
	game.get_level().spawns.append(spawn)

def move_player() -> None:
	sel = editor.get_selection()
	if isinstance(sel, selection.Sector):
		player.set_position(screen_to_world(Vector2(pygame.mouse.get_pos())), sel.id)
	elif isinstance(sel, selection.Spawn):
		spawn = game.get_level().spawns[sel.id]
		player.set_position(spawn.position, spawn.sector)

def handle_keydown(key: int) -> None:
	shift = is_shift_held()

	match key:
		case pygame.K_q | pygame.K_ESCAPE:
			if editor.get_mode() == EditMode.NORMAL:
				save_level()
				game.die()
				return
			editor.set_mode(EditMode.NORMAL)

		case pygame.K_LEFTBRACKET:
			game.set_editor(False)
		case pygame.K_DELETE:
			delete()
		case pygame.K_a:
			insert_vertex()
		case pygame.K_d:
			if isinstance(editor.get_selection(), selection.Vertex):
				editor.set_mode(EditMode.DIVIDE)
		case pygame.K_c:
			sel = editor.get_selection()
			if isinstance(sel, (selection.Vertex, selection.Wall)):
				editor.set_mode(EditMode.ADD)
		case pygame.K_e:
			switch_wall_side()
		case pygame.K_r:
			reverse_sector_walls()
		case pygame.K_s:
			save_level()
		case pygame.K_b:
			place_spawn()
		case pygame.K_p:
			move_player()
		case pygame.K_1:
			set_selection_wall_type(WallType.SOLID, shift)
		case pygame.K_2:
			set_selection_wall_type(WallType.NEIGHBOR, shift)
		case pygame.K_3:
			set_selection_wall_type(WallType.SKY, shift)
