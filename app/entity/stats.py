from dataclasses import dataclass

@dataclass
class Position:
	room: int = 0
	x: float = 0.
	y: float = 0.

@dataclass
class Vitality:
	health: float = 200.
	armor: float = 0.
	invulnerable: bool = False
