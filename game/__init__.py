from dataclasses import dataclass, field
from random import randrange
from typing import NoReturn
import pygame
from pygame import Color, Surface, Vector2
from . import assets, editor, engine, entities, render
from .assets import Cause, Image, Sound, library, loaders
from .assets.deaths import execute as die
from .entities import player
from .world import Level

SENSITIVITY: float = .5
DEFAULT_LEVEL: str = "test/cafe"
EDITOR_MODE: bool = False

@dataclass
class Game:
	level: Level

	scan_frame: bool = False
	editor_mode: bool = False

I: Game

def init(level: str | None = None) -> None:
	engine.init() # NOTE: must be run first
	assets.init()
	render.init()

	pygame.display.set_icon(library.get_image(Image.WINDOW_ICON))
	library.play_sound(Sound.AMBIENT_WINDY, True)
	level = loaders.level(level or DEFAULT_LEVEL)
	player.init(level.spawns[randrange(len(level.spawns))])

	global I
	I = Game(level=level)
	if EDITOR_MODE: set_editor(True)

def get_level() -> Level:
	return I.level

def is_scan_mode() -> bool:
	return I.scan_frame

def set_editor(enabled: bool) -> None:
	I.editor_mode = enabled
	if enabled and not editor.get_init(): editor.init()
	engine.set_editor_mode(enabled)
	if enabled: pygame.mixer.pause()
	else: pygame.mixer.unpause()

def handle_keydown(key: int) -> None:
	match key:
		case pygame.K_ESCAPE | pygame.K_q:
			die()
		case pygame.K_p:
			I.scan_frame = True
		case pygame.K_LEFTBRACKET:
			set_editor(True)

def handle_mouse(diff: float) -> None:
	player.turn_aim(diff * SENSITIVITY)

def handle_events() -> None:
	I.scan_frame = False # reset next frame
	for event in pygame.event.get():
		if event.type == pygame.QUIT: die()
		elif I.editor_mode: editor.handle_event(event)
		elif event.type == pygame.KEYDOWN: handle_keydown(event.key)
		elif event.type == pygame.MOUSEMOTION: handle_mouse(event.rel[0])

def run() -> NoReturn:
	while True:
		handle_events()
		engine.clear()
		if I.editor_mode:
			editor.render.perform()
		else:
			entities.update()
			render.perform()
		engine.update()
