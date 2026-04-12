from dataclasses import dataclass, field
from time import monotonic
import math
import pygame
from pygame.math import Vector2, clamp

import game
from game import engine
from game.assets import Cause, Sound, library
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

@dataclass
class Bobbing:
	frequency: float
	magnitude: float

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
	bob: Bobbing = field(default_factory=lambda: STANDING)
	bob_phase: float = 0
	god_mode: bool = False

I: Player

def init(spawn: Spawn) -> None:
	global I
	I = Player(position=spawn.position.copy(), sector=spawn.sector, aim=spawn.angle)

def is_god() -> bool:
	return I.god_mode

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
	if I.bob == STANDING:
		# smooth highest and lowest
		return math.cos(I.bob_phase) * I.bob.magnitude
	# smooth only highest
	return (abs(math.cos(I.bob_phase / 2)) * 2 - 1) * I.bob.magnitude

def get_absolute_eye_height() -> float:
	sector = game.get_level().sectors[I.sector]
	return I.eye + sector.floor.z + get_bob_factor()

def get_relative(target: Vector2) -> Vector2:
	return (target - I.position).rotate(-I.aim)

def get_stamina() -> float:
	return I.stamina

def toggle_god_mode() -> None:
	I.god_mode = not I.god_mode

def turn_aim(by: float) -> None:
	I.aim -= by

def play_footstep() -> None:
	# TODO: play sound based on sector floor material
	library.play_sound(Sound.STEP_TILE)

def update() -> None:
	keys = pygame.key.get_pressed()

	direction = Vector2()
	if keys[pygame.K_w]: direction.y += 1
	if keys[pygame.K_s]: direction.y -= 1
	if keys[pygame.K_a]: direction.x -= 1
	if keys[pygame.K_d]: direction.x += 1
	direction = direction.clamp_magnitude(1)

	I.bob = STANDING
	if direction.length_squared() > 0:
		I.bob = SPRINTING if keys[pygame.K_LSHIFT] else WALKING
	if I.bob == SPRINTING:
		if I.stamina == 0: I.bob = WALKING
		else: I.last_sprint = monotonic()

	is_sprinting = I.bob == SPRINTING
	distance = SPRINT_SPEED if is_sprinting else WALK_SPEED
	movement = direction.rotate(I.aim) * distance * engine.get_delta()
	new_position = I.position + movement
	new_sector = None

	# update view bobbing
	is_standing = I.bob == STANDING
	heavy_breathing = 3 - 2 * math.pow(I.stamina, .4) if is_standing else 1
	I.bob_phase += I.bob.frequency * heavy_breathing * engine.get_delta()
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
		if I.bob == WALKING: stamina_rate *= STAMINA_REGEN_PENALTY
	I.stamina = clamp(I.stamina + stamina_rate * engine.get_delta(), 0, 1)
	# apply extra delay if stamina reaches 0 this frame
	if last_stamina > 0 and I.stamina == 0: I.last_sprint += STAMINA_TIRED_DELAY
	if is_god(): I.stamina = 1

	# Get walls of current sector and immediate neighbors
	level = game.get_level()
	walls = get_walls(level, I.sector, False)
	n_crossable_walls = len(walls)
	# NOTE: `neighbors` must be separated to prevent iterating to extension
	neighbors = [info.neighbor for _, _, info in walls if info.neighbor is not None]
	for neighbor in neighbors:
		walls.extend(get_walls(level, neighbor, False))

	# collision check against wall
	nearest_neighbor: float = 1e10 # enter the sector of the closest wall
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
			has_collision &= floor_height_diff > CLIMPABLE_HEIGHT and not is_god()

		if dist < HITBOX_SIZE and has_collision:
			new_position = nearest + dist_vec * HITBOX_SIZE
		elif has_neighbor and not is_facing_player:
			if idx < n_crossable_walls and dist < nearest_neighbor:
				new_sector = info.neighbor
				nearest_neighbor = dist

	I.position = new_position
	if new_sector is not None:
		# reset bob when floor height changes
		z_new = level.sectors[new_sector].floor.z
		z_cur = level.sectors[I.sector].floor.z
		if z_new > z_cur: I.bob_phase = -math.pi # lowest point
		elif z_new < z_cur:
			if z_cur - z_new > SURVIABLE_FALL_HEIGHT and not is_god(): game.die(Cause.FALL)
			I.bob_phase = 0 # highest point
		if z_new != z_cur: play_footstep()

		I.sector = new_sector
