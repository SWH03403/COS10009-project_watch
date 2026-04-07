from dataclasses import dataclass
from .fog import Fog, default_fog

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

def default_sector() -> Sector:
	return Sector(
		floor=Plane(0, "khaki4"),
		ceiling=Plane(0, "darkslategrey"),
		walls=[],
		fog=default_fog(),
	)
