from pygame import Vector2

from .fog import Fog, default_fog
from .level import Level
from .sector import Sector, Plane, Wall
from .spawn import Spawn

def get_walls(level: Level, sector_id: int, relative: bool) -> list[tuple[Vector2, Vector2, Wall]]:
	from game.entity import player
	sector = level.sectors[sector_id]
	n_walls = len(sector.walls)
	v = [level.vertexes[wall.vertex] for wall in sector.walls]
	v = [player.get_relative(p) for p in v] if relative else v
	return [(v[i], v[i - n_walls + 1], sector.walls[i]) for i in range(n_walls)]
