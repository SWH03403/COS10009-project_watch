from dataclasses import dataclass

from game.utils.math import Vec2

@dataclass
class Spawn:
	position: Vec2
	sector: int
