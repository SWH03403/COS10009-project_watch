from dataclasses import dataclass, field
from pygame import Vector2
from .stats import Position, Vitality

WALK_SPEED: float = 2.
SPRINT_SPEED: float = 4.

class Direction:
	FORWARD = Vector2(0., 1.)
	BACKWARD = Vector2(0., -1.)
	LEFT = Vector2(-1., 0.)
	RIGHT = Vector2(1., 0.)

@dataclass
class Player:
	position: Position = field(default_factory=Position)
	aim: float = 0. # degree
	vitality: Vitality = field(default_factory=Vitality)
	sprinting: bool = False

	def step(self, direction: Vector2, delta: float) -> None:
		distance = SPRINT_SPEED if self.sprinting else WALK_SPEED
		movement = direction.clamp_magnitude(1.).rotate(self.aim) * distance
		self.position.coord += movement
