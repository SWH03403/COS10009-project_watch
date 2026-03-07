from dataclasses import dataclass, field
from app.utils.math import Vec2

@dataclass
class Position:
	room: int = 0
	coord: Vec2 = field(default_factory=Vec2)

@dataclass
class Vitality:
	health: float = 200.
	armor: float = 0.
	invulnerable: bool = False
