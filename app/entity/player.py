from dataclasses import dataclass, field
from math import pi
from pygame import Vector2
from .stats import Position, Vitality

WALK_SPEED: float = 80.
SPRINT_SPEED: float = 120.

class Direction:
	FORWARD = 90.
	BACKWARD = 270.
	LEFT = 180.
	RIGHT = 0.

@dataclass
class Player:
	position: Position = field(default_factory=Position)
	aim: float = 0. # degree
	vitality: Vitality = field(default_factory=Vitality)
	sprinting: bool = False

	def step(self, direction: float, delta: float) -> None:
		distance = SPRINT_SPEED if self.sprinting else WALK_SPEED
		movement = Vector2()
		movement.from_polar((distance * delta, self.aim + direction))
		self.position.coord += movement
