from dataclasses import dataclass
from pygame import Vector2

from game.entity import player
from .sector import Sector
from .spawn import Spawn

@dataclass
class Level:
	spawns: list[Spawn]
	vertexes: list[Vector2]
	sectors: list[Sector]

def get_walls(level: Level, sector: int, relative: bool) -> list[tuple[Vector2, Vector2]]:
	s = level.sectors[sector]
	n = len(s.vertexes)
	v = [level.vertexes[idx] for idx in s.vertexes]
	v = [player.get_relative(p) for p in v] if relative else v
	return [(v[i], v[i - n + 1], s.connects[i]) for i in range(n)]
