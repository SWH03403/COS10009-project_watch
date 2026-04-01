from dataclasses import dataclass
from game.utils.math import Vec2

WALK_SPEED: float = 60.
SPRINT_SPEED: float = 100.

class Direction:
	FORWARD = Vec2(0., 1.)
	BACKWARD = Vec2(0., -1.)
	LEFT = Vec2(-1., 0.)
	RIGHT = Vec2(1., 0.)

@dataclass
class Player:
	position: Vec2
	aim: float
	sprint: bool

	# Vitality
	health: float = 200.
	armor: float = 0.
	invulnerable: bool = False

I: Player

def init() -> None:
	global I
	I = Player(
		position=Vec2(),
		aim=0,
		sprint=False,
		health=200,
		armor=0,
	)

def set_position(pos: Vec2) -> None:
	I.position = pos

def set_sprint(sprint: bool) -> None:
	I.sprint = sprint

def turn_aim(by: float) -> None:
	I.aim += by

def step(direction: Vec2, delta: float) -> None:
	distance = SPRINT_SPEED if I.sprint else WALK_SPEED
	movement = direction.clamp_magnitude(1.).rotate(I.aim) * distance * delta
	I.position += movement
