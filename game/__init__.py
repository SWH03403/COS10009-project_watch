from dataclasses import dataclass, field
from random import randrange
from time import sleep
import pygame
from pygame import Color, Surface, Vector2
from . import assets, editor, engine, entities, render
from .assets import Image, Sound, library, loaders
from .entities import Direction, MovementState, player
from .world import Level

SENSITIVITY: float = .5
DEFAULT_LEVEL: str = "test/cafe"
EDITOR_MODE: bool = True

@dataclass
class Game:
	running: bool
	level: Level

	scan_frame: bool
	editor_mode: bool
	death_delay: float

I: Game

def init() -> None:
	engine.init() # NOTE: must be run first
	assets.init()
	render.init()

	pygame.display.set_icon(library.get_image(Image.WINDOW_ICON))
	library.play_sound(Sound.AMBIENT_WINDY, True)
	level = loaders.level(DEFAULT_LEVEL)
	player.init(level.spawns[randrange(len(level.spawns))])

	global I
	I = Game(running=True, level=level, scan_frame=False, editor_mode=False, death_delay=0)
	if EDITOR_MODE: set_editor(True)

def get_level() -> Level:
	return I.level

def is_scan_mode() -> bool:
	return I.scan_frame

def set_editor(enabled: bool) -> None:
	I.editor_mode = enabled
	if enabled and not editor.get_init(): editor.init()
	engine.set_editor_mode(enabled)
	if enabled: pygame.mixer.music.pause()
	else: pygame.mixer.music.unpause()

def set_death_delay(delay: float) -> None:
	I.death_delay = max(delay, 0)

def die() -> None:
	I.running = False

def handle_keydown(key: int) -> None:
	match key:
		case pygame.K_ESCAPE | pygame.K_q:
			die()
		case pygame.K_p:
			I.scan_frame = True
		case pygame.K_LEFTBRACKET:
			set_editor(True)

def handle_keys() -> None:
	if I.editor_mode: return
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
		if event.type == pygame.QUIT: die()
		elif I.editor_mode: editor.handle_event(event)
		elif event.type == pygame.KEYDOWN: handle_keydown(event.key)
		elif event.type == pygame.MOUSEMOTION: handle_mouse(event.rel[0])

def run() -> None:
	while I.running:
		handle_events()
		handle_keys()

		engine.clear()
		if I.editor_mode:
			editor.render.perform()
		else:
			entities.update()
			render.perform()
		engine.update()
		engine.tick()

	blackout = min(I.death_delay, .1)
	pygame.display.set_gamma(2, .2, .2)
	sleep(blackout)
	engine.clear()
	engine.update()
	sleep(I.death_delay - blackout)
	pygame.quit()
