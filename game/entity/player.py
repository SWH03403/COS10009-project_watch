from dataclasses import dataclass
import math
from pygame.math import clamp

import game
from game import engine
from game.utils.math import Line, Vec2
from game.world.level import get_walls

WALK_SPEED: float = 20
SPRINT_SPEED: float = 50
HITBOX_SIZE: float = 3

class Direction:
	FORWARD = Vec2(0, 1)
	BACKWARD = Vec2(0, -1)
	LEFT = Vec2(-1, 0)
	RIGHT = Vec2(1, 0)

@dataclass
class Bobbing:
	frequency: float
	magnitude: float

class MovementState:
	STANDING = Bobbing(1, 1)
	WALKING = Bobbing(8, 1)
	SPRINTING = Bobbing(16, 2)

@dataclass
class Player:
	position: Vec2
	sector: int
	eye: float # z coordinate
	aim: float
	state: MovementState
	bob_phase: float

	# Vitality
	health: float = 200
	armor: float = 0
	invulnerable: bool = False

I: Player

def init() -> None:
	global I
	I = Player(
		position=Vec2(),
		sector=0,
		eye=10,
		aim=0,
		state=MovementState.STANDING,
		bob_phase=0,
	)

def get_position() -> tuple[Vec2, int]:
	return I.position, I.sector

# return degree angle in [0; 360) range
def get_aim() -> float:
	aim = I.aim % 360
	while aim >= 360:
		aim -= 360
	while aim < 0:
		aim += 360
	return aim

def get_absolute_eye_height() -> float:
	sector = game.get_level().sectors[I.sector]
	zbob = math.cos(I.bob_phase) * I.state.magnitude
	return I.eye + sector.floor + zbob

def get_relative(target: Vec2) -> Vec2:
	return (target - I.position).rotate(-I.aim)

def set_position(position: Vec2, sector: int) -> None:
	I.position = position
	I.sector = sector

def set_state(state: MovementState) -> None:
	I.state = state

def turn_aim(by: float) -> None:
	I.aim -= by

def step(direction: Vec2) -> None:
	distance = SPRINT_SPEED if I.state == MovementState.SPRINTING else WALK_SPEED
	movement = direction.clamp_magnitude(1.).rotate(I.aim) * distance * engine.get_delta()
	new_position = I.position + movement
	new_sector = None

	# update view bobbing
	I.bob_phase += I.state.frequency * engine.get_delta()

	# Get walls of current sector and immediate neighbors
	level = game.get_level()
	walls = get_walls(level, I.sector, False)
	psector_walls = len(walls)
	neighbors = [c for _, _, c in walls if c is not None]
	for neighbor in neighbors:
		walls.extend(get_walls(level, neighbor, False))

	# collision check against wall
	for idx, (left, right, neighbor) in enumerate(walls):
		wall = left - right
		to_left = left - new_position
		nearest = left
		if left != right:
			fact = clamp(to_left.dot(wall) / wall.length_squared(), 0, 1)
			nearest = left.lerp(right, fact)
		dist_vec = new_position - nearest
		dist = dist_vec.length()
		if dist > 0: dist_vec.normalize_ip()
		if dist < HITBOX_SIZE and neighbor is None:
			new_position = nearest + dist_vec * HITBOX_SIZE
		elif neighbor is not None and Line.from_point(left, right).cross(new_position) < 0:
			if new_sector is None and idx < psector_walls: new_sector = neighbor

	I.position = new_position
	if new_sector is not None: I.sector = new_sector
