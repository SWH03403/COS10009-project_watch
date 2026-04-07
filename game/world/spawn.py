from dataclasses import dataclass
from pygame import Vector2

@dataclass
class Spawn:
	position: Vector2
	sector: int
