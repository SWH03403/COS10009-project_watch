from dataclasses import dataclass
from .fog import Fog

@dataclass
class Sector:
	# height
	floor: float
	ceiling: float
	vertexes: list[int]
	connects: list[int | None]
	fog: Fog
