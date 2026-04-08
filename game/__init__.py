from dataclasses import dataclass, field
from random import randrange
import pygame
from pygame import Color, Surface, Vector2
from . import engine, entity, render
from .entity import Direction, MovementState, player
from .loaders import load_level, load_music
from .world import Level

SENSITIVITY: float = .5

@dataclass
class Game:
	running: bool
	level: Level

	scan_frame: bool = False

I: Game

def init() -> None:
	engine.init()
	render.init()
	entity.init()

	# music
	load_music("void")
	pygame.mixer.music.play(-1)
	pygame.mixer.music.set_volume(.5)

	level = load_level("cafe") # DEBUG: Test level
	spawn = level.spawns[randrange(len(level.spawns))]
	player.set_position(spawn.position, spawn.sector)
	player.set_aim(spawn.angle)

	global I
	I = Game(running=True, level=level)

def get_level() -> Level:
	return I.level

def is_scan_mode() -> bool:
	return I.scan_frame

def _handle_keydown(key: int) -> bool:
	match key:
		case pygame.K_ESCAPE | pygame.K_q:
			I.running = False
		case pygame.K_p:
			I.scan_frame = True

def _handle_key() -> bool:
	keys = pygame.key.get_pressed()

	# player movement
	direction = Vector2()
	if keys[pygame.K_w]: direction += Direction.FORWARD
	if keys[pygame.K_s]: direction += Direction.BACKWARD
	if keys[pygame.K_a]: direction += Direction.LEFT
	if keys[pygame.K_d]: direction += Direction.RIGHT
	state = MovementState.STANDING
	if direction.length_squared() > 0:
		state = MovementState.SPRINTING if keys[pygame.K_LSHIFT] else MovementState.WALKING
	player.set_state(state)
	player.set_direction(direction)

def _handle_mouse(diff: float) -> None:
	player.turn_aim(diff * SENSITIVITY)

def _handle_events() -> bool:
	I.scan_frame = False # reset next frame
	for event in pygame.event.get():
		if event.type == pygame.QUIT: I.running = False
		elif event.type == pygame.KEYDOWN: _handle_keydown(event.key)
		elif event.type == pygame.MOUSEMOTION: _handle_mouse(event.rel[0])

def run() -> None:
	while I.running:
		_handle_events()
		_handle_key()

		entity.update()

		engine.clear()
		render.update()
		engine.update()
		engine.tick()

	pygame.quit()
