from dataclasses import dataclass
from pygame import Vector2

from .sector import Sector
from .spawn import Spawn

@dataclass
class Level:
	spawns: list[Spawn]
	vertexes: list[Vector2]
	sectors: list[Sector]

def default_level() -> Level:
	return Level(spawns=[Spawn(sector=0, position=Vector2(0, 0), angle=0)], vertexes=[], sectors=[])
