from dataclasses import dataclass

import game
from game import engine
from game.utils.math import Line, Vec2
from game.world.level import get_walls

WALK_SPEED: float = 20
SPRINT_SPEED: float = 50
COLLISION_RADIUS: float = 3

class Direction:
	FORWARD = Vec2(0, 1)
	BACKWARD = Vec2(0, -1)
	LEFT = Vec2(-1, 0)
	RIGHT = Vec2(1, 0)

@dataclass
class Player:
	position: Vec2
	sector: int
	eye: float # z coordinate
	aim: float
	sprint: bool

	# Vitality
	health: float = 200
	armor: float = 0
	invulnerable: bool = False

I: Player

def init() -> None:
	global I
	I = Player(position=Vec2(), sector=0, eye=10, aim=0, sprint=False)

def get_position() -> tuple[Vec2, int]:
	return I.position, I.sector

def get_absolute_eye_height() -> float:
	sector = game.get_level().sectors[I.sector]
	return I.eye + sector.floor

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

	# collision check against wall
	walls = get_walls(game.get_level(), I.sector, False)
	for left, right, neighbor in walls:
		wall = Line.from_point(left, right)
		wall_vec = left - right
		dist = wall.dist_from(I.position + movement)
		if dist < COLLISION_RADIUS and neighbor is None:
			movement = movement.project(wall_vec)
		elif dist < 0 and neighbor is not None:
			I.sector = neighbor

	I.position += movement
