from dataclasses import dataclass
from pygame import Vector2

from .sector import Sector
from .spawn import Spawn

@dataclass
class Level:
	spawns: list[Spawn]
	vertexes: list[Vector2]
	sectors: list[Sector]
