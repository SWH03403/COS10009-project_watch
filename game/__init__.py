from dataclasses import dataclass, field
from random import randrange
import pygame
from pygame import Color, Surface, Vector2
from . import editor, engine, entity, render
from .entity import Direction, MovementState, player
from .loaders import load_level, load_music
from .world import Level

SENSITIVITY: float = .5

@dataclass
class Game:
	running: bool
	level: Level

	scan_frame: bool
	editor_mode: bool

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
	I = Game(running=True, level=level, scan_frame=False, editor_mode=False)

def get_level() -> Level:
	return I.level

def is_scan_mode() -> bool:
	return I.scan_frame

def set_editor(enabled: bool) -> None:
	I.editor_mode = enabled
	if enabled and not editor.get_init(): editor.init()
	pygame.mouse.set_relative_mode(not enabled)

def handle_keydown(key: int) -> None:
	if I.editor_mode: return editor.handle_keydown(key)
	match key:
		case pygame.K_ESCAPE | pygame.K_q:
			I.running = False
		case pygame.K_p:
			I.scan_frame = True
		case pygame.K_LEFTBRACKET:
			set_editor(True)

def handle_keys() -> None:
	if I.editor_mode: return editor.handle_keys()
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

def handle_mouse(diff: float) -> None:
	player.turn_aim(diff * SENSITIVITY)

def handle_events() -> None:
	I.scan_frame = False # reset next frame
	for event in pygame.event.get():
		if event.type == pygame.QUIT: I.running = False
		elif event.type == pygame.KEYDOWN: handle_keydown(event.key)
		elif event.type == pygame.MOUSEMOTION: handle_mouse(event.rel[0])
		elif I.editor_mode: editor.handle_event(event)

def run() -> None:
	while I.running:
		handle_events()
		handle_keys()

		engine.clear()
		if I.editor_mode:
			editor.render.perform()
		else:
			entity.update()
			render.perform()
		engine.update()
		engine.tick()

	pygame.quit()
