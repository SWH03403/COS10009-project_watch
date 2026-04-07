from dataclasses import dataclass
from pygame import Vector2

@dataclass
class Spawn:
	sector: int
	position: Vector2
	angle: float
