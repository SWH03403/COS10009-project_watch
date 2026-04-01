from dataclasses import dataclass

from game import engine
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
	sector: int
	eye: float # z coordinate
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
		sector=0,
		eye=10,
		aim=0,
		sprint=False,
		health=200,
		armor=0,
	)

def get_position() -> tuple[Vec2, int]:
	return I.position, I.sector

def get_eye_height() -> float:
	return I.eye

def get_relative(target: Vec2) -> Vec2:
	return (target - I.position).rotate(-I.aim)

def set_position(position: Vec2, sector: int) -> None:
	I.position = position
	I.sector = sector

def set_sprint(sprint: bool) -> None:
	I.sprint = sprint

def turn_aim(by: float) -> None:
	I.aim -= by * engine.get_delta()

def step(direction: Vec2) -> None:
	distance = SPRINT_SPEED if I.sprint else WALK_SPEED
	movement = direction.clamp_magnitude(1.).rotate(I.aim) * distance * engine.get_delta()
	I.position += movement
