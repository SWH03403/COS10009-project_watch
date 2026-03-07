from dataclasses import dataclass, field
from .stats import Position, Vitality
from app.utils.math import Vec2

WALK_SPEED: float = 60.
SPRINT_SPEED: float = 100.

class Direction:
	FORWARD = Vec2(0., 1.)
	BACKWARD = Vec2(0., -1.)
	LEFT = Vec2(-1., 0.)
	RIGHT = Vec2(1., 0.)

@dataclass
class Player:
	position: Position = field(default_factory=Position)
	aim: float = 0. # degree
	vitality: Vitality = field(default_factory=Vitality)
	sprinting: bool = False

	def step(self, direction: Vec2, delta: float) -> None:
		distance = SPRINT_SPEED if self.sprinting else WALK_SPEED
		movement = direction.clamp_magnitude(1.).rotate(self.aim) * distance * delta
		self.position.coord += movement
