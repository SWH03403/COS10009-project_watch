from dataclasses import dataclass, field
from pygame import Vector2

@dataclass
class Position:
	room: int = 0
	coord: Vector2 = field(default_factory=Vector2)

@dataclass
class Vitality:
	health: float = 200.
	armor: float = 0.
	invulnerable: bool = False
