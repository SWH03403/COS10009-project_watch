from dataclasses import dataclass

@dataclass
class Sector:
	# height
	floor: float
	ceiling: float
	vertexes: list[int]
	connects: list[int | None]
