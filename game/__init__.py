from dataclasses import dataclass, field
import pygame
from pygame import Color, Surface
from . import engine, render
from .assets import load_level
from .entity import Direction, player
from .utils.math import Vec2
from .world import Level

SENSITIVITY: float = .5

@dataclass
class Game:
	running: bool
	level: Level

I: Game

def init() -> None:
	engine.init()
	render.init()
	player.init()

	level = load_level("stairs") # DEBUG: Test level
	player.set_position(level.spawn.position, level.spawn.sector)

	global I
	I = Game(running=True, level=level)

def get_level() -> Level:
	return I.level

def _handle_keydown(key: int) -> bool:
	match key:
		case pygame.K_ESCAPE | pygame.K_q:
			I.running = False

def _handle_key() -> bool:
	keys = pygame.key.get_pressed()

	# player movement
	direction = Vec2()
	if keys[pygame.K_w]: direction += Direction.FORWARD
	if keys[pygame.K_s]: direction += Direction.BACKWARD
	if keys[pygame.K_a]: direction += Direction.LEFT
	if keys[pygame.K_d]: direction += Direction.RIGHT
	player.set_sprint(keys[pygame.K_LSHIFT])
	player.step(direction)

	if direction.length_squared() > 0:
		...

def _handle_mouse(diff: float) -> None:
	player.turn_aim(diff * SENSITIVITY)

def _handle_events() -> bool:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: I.running = False
		elif event.type == pygame.KEYDOWN: _handle_keydown(event.key)
		elif event.type == pygame.MOUSEMOTION: _handle_mouse(event.rel[0])

def run() -> None:
	while I.running:
		_handle_events()
		_handle_key()

		engine.clear()
		render.update()
		engine.update()
		engine.tick()

	pygame.quit()
