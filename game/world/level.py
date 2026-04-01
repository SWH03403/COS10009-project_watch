from dataclasses import dataclass

from game.utils.math import Vec2
from .fog import Fog
from .sector import Sector
from .spawn import Spawn

@dataclass
class Level:
	spawn: Spawn
	vertexes: list[Vec2]
	sectors: list[Sector]
	fog: Fog
