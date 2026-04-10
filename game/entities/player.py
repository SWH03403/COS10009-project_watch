from dataclasses import dataclass, field
from enum import Enum
from time import monotonic
import math
from pygame.math import Vector2, clamp

import game
from game import engine
from game.assets import Sound, library
from game.utils.math import is_facing
from game.world import Spawn, get_walls
from game.world.sector import WallType, get_wall_type

WALK_SPEED: float = 20
SPRINT_SPEED: float = 50
HITBOX_SIZE: float = 3

SURVIABLE_FALL_HEIGHT: float = 40
CLIMPABLE_HEIGHT: float = 10

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

class MovementState(Enum):
	STANDING = Bobbing(1, 1)
	WALKING = Bobbing(8, 1)
	SPRINTING = Bobbing(16, 2)

@dataclass
class Player:
	position: Vector2
	sector: int
	aim: float

	eye: float = 10 # z coordinate
	stamina: float = 1
	last_sprint: float = 0 # the last time the player sprints
	direction: Vector2 = field(init=False) # set by main loop anyway
	state: MovementState = MovementState.STANDING
	bob_phase: float = 0

I: Player

def init(spawn: Spawn) -> None:
	global I
	I = Player(position=spawn.position, sector=spawn.sector, aim=spawn.angle)

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
		return math.cos(I.bob_phase) * I.state.value.magnitude
	# smooth only highest
	return (abs(math.cos(I.bob_phase / 2)) * 2 - 1) * I.state.value.magnitude

def get_absolute_eye_height() -> float:
	sector = game.get_level().sectors[I.sector]
	return I.eye + sector.floor.z + get_bob_factor()

def get_relative(target: Vector2) -> Vector2:
	return (target - I.position).rotate(-I.aim)

def get_stamina() -> float:
	return I.stamina

def set_state(state: MovementState) -> None:
	if state == MovementState.SPRINTING:
		if I.stamina == 0: state = MovementState.WALKING
		else: I.last_sprint = monotonic()
	I.state = state

def set_direction(direction: Vector2) -> None:
	I.direction = direction.clamp_magnitude(1)

def turn_aim(by: float) -> None:
	I.aim -= by

def play_footstep() -> None:
	# TODO: play sound based on sector floor material
	library.play_sound(Sound.STEP_TILE)

def update() -> None:
	is_sprinting = I.state == MovementState.SPRINTING
	distance = SPRINT_SPEED if is_sprinting else WALK_SPEED
	movement = I.direction.rotate(I.aim) * distance * engine.get_delta()
	new_position = I.position + movement
	new_sector = None

	# update view bobbing
	is_standing = I.state == MovementState.STANDING
	heavy_breathing = 3 - 2 * math.pow(I.stamina, .4) if is_standing else 1
	I.bob_phase += I.state.value.frequency * heavy_breathing * engine.get_delta()
	# play sound after lowest bob
	if I.bob_phase > math.pi:
		I.bob_phase %= 2 * math.pi
		if I.bob_phase > math.pi and not is_standing: play_footstep()
		I.bob_phase -= 2 * math.pi

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
	n_crossable_walls = len(walls)
	# NOTE: `neighbors` must be separated to prevent iterating to extension
	neighbors = [info.neighbor for _, _, info in walls if info.neighbor is not None]
	for neighbor in neighbors:
		walls.extend(get_walls(level, neighbor, False))

	# collision check against wall
	for idx, (left, right, info) in enumerate(walls):
		wall = left - right
		to_left = left - new_position
		nearest = left
		if left != right:
			fact = clamp(to_left.dot(wall) / wall.length_squared(), 0, 1)
			nearest = left.lerp(right, fact)
		dist_vec = new_position - nearest
		dist = dist_vec.length()
		if dist > 0: dist_vec.normalize_ip()

		is_facing_player = is_facing(left, right, new_position)
		has_collision = is_facing_player
		has_neighbor = get_wall_type(info) == WallType.NEIGHBOR
		if has_neighbor:
			floor_height_diff = level.sectors[info.neighbor].floor.z - level.sectors[I.sector].floor.z
			has_collision &= floor_height_diff > CLIMPABLE_HEIGHT

		if dist < HITBOX_SIZE and has_collision:
			new_position = nearest + dist_vec * HITBOX_SIZE
		elif has_neighbor and not is_facing_player:
			if new_sector is None and idx < n_crossable_walls: new_sector = info.neighbor

	I.position = new_position
	if new_sector is not None:
		# reset bob when floor height changes
		z_new = level.sectors[new_sector].floor.z
		z_cur = level.sectors[I.sector].floor.z
		if z_new > z_cur: I.bob_phase = -math.pi # lowest point
		elif z_new < z_cur:
			if z_cur - z_new > SURVIABLE_FALL_HEIGHT:
				library.play_sound(Sound.DEATH_FALL)
				game.set_death_delay(.4) # TODO: refactor as asset
				game.die()
			I.bob_phase = 0 # highest point
		if z_new != z_cur: play_footstep()

		I.sector = new_sector
