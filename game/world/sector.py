from dataclasses import dataclass
from .fog import Fog

# default colors
WALL_COLOR: str = "darkkhaki"
CEILING_COLOR: str = "darkslategrey"
FLOOR_COLOR: str = "khaki4"

@dataclass
class Plane:
	height: float
	color: str | None

	@property
	def z(self) -> float:
		return self.height

@dataclass
class Wall:
	vertex: int
	neighbor: int | None
	color: str | None

@dataclass
class Sector:
	floor: Plane
	ceiling: Plane
	walls: list[Wall]
	fog: Fog
