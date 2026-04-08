from dataclasses import dataclass
from pygame import Vector2

import game
from .. import editor

THRESHOLD: float = 20 # pixels

@dataclass
class Sector:
	id: int

@dataclass
class Wall:
	sector_id: int
	wall_idx: int

@dataclass
class Vertex:
	id: int

type Selection = Sector | Wall | Vertex | None

def find_nearest_item(pos: Vector2) -> Selection:
	level = game.get_level()
	items: list[tuple[float, Selection]] = []

	world_pos = pos - editor.get_origin()
	world_pos.y *= -1
	world_pos /= editor.get_scale()

	for i, vertex in enumerate(level.vertexes):
		items.append(((vertex - world_pos).length(), Vertex(i)))
	for i, sector in enumerate(level.sectors):
		corners = [level.vertexes[wall.vertex] for wall in sector.walls]
		center = sum(corners, start=Vector2()) / len(sector.walls)
		items.append(((center - world_pos).length(), Sector(i)))
		for j, vertex in enumerate(corners):
			other = corners[j - len(corners) + 1]
			middle = (vertex + other) / 2
			items.append(((middle - world_pos).length(), Wall(i, j)))

	max_dist = THRESHOLD / editor.get_scale()
	items = [sel for sel in items if sel[0] <= max_dist]
	if len(items) == 0: return None
	return min(items, key=lambda sel: sel[0])[1]

def get_all_vertexes(sel: Selection) -> list[Vector2]:
	level = game.get_level()

	if isinstance(sel, Sector):
		sector = level.sectors[sel.id]
		return [level.vertexes[wall.vertex] for wall in sector.walls]
	elif isinstance(sel, Wall):
		sector = level.sectors[sel.sector_id]
		left = level.vertexes[sector.walls[sel.wall_idx].vertex]
		right = level.vertexes[sector.walls[sel.wall_idx - len(sector.walls) + 1].vertex]
		return [left, right]
	elif isinstance(sel, Vertex):
		return [level.vertexes[sel.id]]
	return []
