from dataclasses import dataclass
from enum import IntEnum, auto
from .fog import Fog, default_fog

# default colors
CEILING_COLOR: str = "khaki4"
FLOOR_COLOR: str = "darkslategrey"
WALL_COLOR: str = "darkkhaki"

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
	neighbor: int | None = None
	color: str | None = WALL_COLOR

@dataclass
class Sector:
	floor: Plane
	ceiling: Plane
	walls: list[Wall]
	fog: Fog

def default_sector() -> Sector:
	return Sector(
		floor=Plane(height=0, color=FLOOR_COLOR),
		ceiling=Plane(height=30, color=CEILING_COLOR),
		walls=[],
		fog=default_fog(),
	)

def get_wall_type(wall: Wall) -> WallType:
	if wall.color is None: return WallType.SKY
	if wall.neighbor is None: return WallType.SOLID
	return WallType.NEIGHBOR

def set_wall_type(wall: Wall, typ: WallType) -> None:
	if typ == WallType.SKY:
		wall.neighbor = wall.color = None
	elif typ == WallType.SOLID:
		wall.neighbor = None
		if wall.color is None: wall.color = WALL_COLOR
