from dataclasses import dataclass
from time import monotonic
import math
from random import randrange
from pygame import Sound
from pygame.math import Vector2, clamp

import game
from game import engine
from game.loaders import load_sounds_suffix
from game.utils.math import Line
from game.world.level import get_walls

WALK_SPEED: float = 20
SPRINT_SPEED: float = 50
HITBOX_SIZE: float = 3

STAMINA_DECAY: float = .1
STAMINA_REGEN: float = .15
STAMINA_REGEN_DELAY: float = 2
STAMINA_TIRED_DELAY: float = 3 # extra time penalty if running out of stamina
STAMINA_REGEN_PENALTY: float = .35 # applied when walking

class Direction:
	FORWARD = Vector2(0, 1)
	BACKWARD = Vector2(0, -1)
	LEFT = Vector2(-1, 0)
	RIGHT = Vector2(1, 0)

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
	position: Vector2
	sector: int
	eye: float # z coordinate
	aim: float
	stamina: float
	last_sprint: float # the last time the player sprints
	state: MovementState
	bob_phase: float
	footstep: list[Sound]

I: Player

def init() -> None:
	global I
	I = Player(
		position=Vector2(),
		sector=0,
		eye=10,
		aim=0,
		stamina=1,
		last_sprint=0,
		state=MovementState.STANDING,
		bob_phase=0,
		footstep=load_sounds_suffix("footsteps/tile")
	)

def get_position() -> tuple[Vector2, int]:
	return I.position, I.sector

# return degree angle in [0; 360) range
def get_aim() -> float:
	aim = I.aim % 360
	while aim >= 360:
		aim -= 360
	while aim < 0:
		aim += 360
	return aim

def get_bob_factor() -> float:
	if I.state == MovementState.STANDING:
		# smooth highest and lowest
		return math.cos(I.bob_phase) * I.state.magnitude
	# smooth only highest
	return (abs(math.cos(I.bob_phase / 2)) * 2 - 1) * I.state.magnitude

def get_absolute_eye_height() -> float:
	sector = game.get_level().sectors[I.sector]
	return I.eye + sector.floor + get_bob_factor()

def get_relative(target: Vector2) -> Vector2:
	return (target - I.position).rotate(-I.aim)

def get_stamina() -> float:
	return I.stamina

def set_position(position: Vector2, sector: int) -> None:
	I.position = position
	I.sector = sector

def set_state(state: MovementState) -> None:
	if state == MovementState.SPRINTING:
		if I.stamina == 0: state = MovementState.WALKING
		else: I.last_sprint = monotonic()
	I.state = state

def turn_aim(by: float) -> None:
	I.aim -= by

def play_footstep() -> Sound:
	I.footstep[randrange(len(I.footstep))].play()

def step(direction: Vector2) -> None:
	is_sprinting = I.state == MovementState.SPRINTING
	distance = SPRINT_SPEED if is_sprinting else WALK_SPEED
	movement = direction.clamp_magnitude(1.).rotate(I.aim) * distance * engine.get_delta()
	new_position = I.position + movement
	new_sector = None

	# update view bobbing
	heavy_breathing = 3 - 2 * math.pow(I.stamina, .4) if I.state == MovementState.STANDING else 1
	I.bob_phase += I.state.frequency * heavy_breathing * engine.get_delta()

	# update stamina
	last_stamina = I.stamina
	stamina_rate = 0
	if is_sprinting: stamina_rate = -STAMINA_DECAY
	elif monotonic() >= I.last_sprint + STAMINA_REGEN_DELAY:
		stamina_rate = STAMINA_REGEN
		if I.state == MovementState.WALKING: stamina_rate *= STAMINA_REGEN_PENALTY
	I.stamina = clamp(I.stamina + stamina_rate * engine.get_delta(), 0, 1)
	# apply extra delay if stamina reaches 0 this frame
	if last_stamina > 0 and I.stamina == 0: I.last_sprint += STAMINA_TIRED_DELAY

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
	if new_sector is not None:
		# reset bob when floor height changes
		z_new = level.sectors[new_sector].floor
		z_cur = level.sectors[I.sector].floor
		if z_new > z_cur: I.bob_phase = math.pi # lowest point
		elif z_new < z_cur: I.bob_phase = 0 # highest point
		if z_new != z_cur: play_footstep()

		I.sector = new_sector
