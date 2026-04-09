from dataclasses import dataclass
from enum import IntEnum, auto
from .fog import Fog

# default colors
WALL_COLOR: str = "darkkhaki"
CEILING_COLOR: str = "khaki4"
FLOOR_COLOR: str = "darkslategrey"

class WallType(IntEnum):
	NEIGHBOR = auto()
	SKY = auto()
	SOLID = auto()

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

def get_wall_type(wall: Wall) -> WallType:
	if wall.color is None: return WallType.SKY
	if wall.neighbor is None: return WallType.SOLID
	return WallType.NEIGHBOR
