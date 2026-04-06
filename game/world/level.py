from dataclasses import dataclass

from game.entity import player
from game.utils.math import Vec2
from .sector import Sector
from .spawn import Spawn

@dataclass
class Level:
	spawn: Spawn
	vertexes: list[Vec2]
	sectors: list[Sector]

def get_walls(level: Level, sector: int, relative: bool) -> list[tuple[Vec2, Vec2]]:
	s = level.sectors[sector]
	n = len(s.vertexes)
	v = [level.vertexes[idx] for idx in s.vertexes]
	v = [player.get_relative(p) for p in v] if relative else v
	return [(v[i], v[i - n + 1], s.connects[i]) for i in range(n)]
