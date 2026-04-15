from dataclasses import dataclass
from enum import Enum, auto
from pygame import Vector2

import game
from game import entities
from .. import editor
from .common import EditMode, screen_to_world

THRESHOLD: float = 50 # pixels

class EntityType(Enum):
	CREATURE = auto()
	PLAYER = auto()

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

@dataclass
class Spawn:
	id: int

@dataclass
class Entity:
	typ: EntityType

type Selection = Sector | Wall | Vertex | Spawn | Entity | None

SELECTION_FILTERS: dict[EditMode, tuple[type, ...]] = {
	EditMode.NORMAL: (),
	EditMode.ADD: (Vertex,),
	EditMode.DIVIDE: (Vertex,),
}

def get_nearest(position: Vector2, filters: tuple[type, ...] | None = None) -> Selection:
	level = game.get_level()
	items: list[tuple[float, Selection]] = []
	world_pos = screen_to_world(position)

	if filters is None: filters = SELECTION_FILTERS[editor.get_mode()]
	no_filter = len(filters) == 0

	if no_filter or Vertex in filters:
		for i, vertex in enumerate(level.vertexes):
			items.append(((vertex - world_pos).length(), Vertex(i)))
	for i, sector in enumerate(level.sectors):
		if no_filter or Sector in filters:
			corners = [level.vertexes[wall.vertex] for wall in sector.walls]
			center = sum(corners, start=Vector2()) / len(sector.walls)
			items.append(((center - world_pos).length(), Sector(i)))
		if not (no_filter or Wall in filters): continue
		for j, left in enumerate(corners):
			right = corners[j - len(corners) + 1]
			target = left.lerp(right, 1 / 3) # differentiate shared sector wall
			items.append(((target - world_pos).length(), Wall(i, j)))

	if no_filter or Entity in filters:
		dist = (entities.creature.get_position() - world_pos).length()
		items.append((dist, Entity(typ=EntityType.CREATURE)))
		dist = (entities.player.get_position()[0] - world_pos).length()
		items.append((dist, Entity(typ=EntityType.PLAYER)))
	if no_filter or Spawn in filters:
		for i, spawn in enumerate(level.spawns):
			items.append(((spawn.position - world_pos).length(), Spawn(i)))

	max_dist = THRESHOLD / editor.get_scale()
	items = [sel for sel in items if sel[0] <= max_dist]
	if len(items) == 0: return None
	return min(items, key=lambda sel: sel[0])[1]

def is_world_element(sel: Selection) -> bool:
	return isinstance(sel, (Vertex, Wall, Sector))

def get_vertexes(sel: Selection) -> list[Vector2]:
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
	elif isinstance(sel, Spawn):
		return [level.spawns[sel.id].position]
	elif isinstance(sel, Entity):
		if sel.typ == EntityType.CREATURE: return [entities.creature.get_position()]
		elif sel.typ == EntityType.PLAYER: return [entities.player.get_position()[0]]
	return []
