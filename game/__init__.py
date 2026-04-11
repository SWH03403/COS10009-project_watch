from dataclasses import dataclass, field
from random import randrange
from typing import NoReturn
import pygame
from pygame import Color, Surface, Vector2
from . import assets, editor, engine, entities, render
from .assets import Cause, Image, Sound, library, loaders
from .assets.deaths import execute as die
from .entities import creature, player
from .world import Level

SENSITIVITY: float = .5
DEFAULT_LEVEL: str = "test/cafe"
EDITOR_MODE: bool = True

@dataclass
class Game:
	level: Level

	slow_render: bool = False
	editor_mode: bool = EDITOR_MODE

I: Game

def init(level: str | None = None) -> None:
	engine.init() # NOTE: must be run first
	assets.init()
	render.init()

	pygame.display.set_icon(library.get_image(Image.WINDOW_ICON))
	library.play_sound(Sound.AMBIENT_WINDY, True)
	level = loaders.level(level or DEFAULT_LEVEL)
	player.init(level.spawns[randrange(len(level.spawns))])
	creature.init()

	global I
	I = Game(level=level)
	if I.editor_mode: set_editor(True)

def get_level() -> Level:
	return I.level

def is_slow_render() -> bool:
	return I.slow_render

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
			I.slow_render = True
		case pygame.K_LEFTBRACKET:
			set_editor(True)
		case pygame.K_BACKSLASH:
			player.toggle_god_mode()

def handle_mouse(diff: float) -> None:
	player.turn_aim(diff * SENSITIVITY)

def handle_events() -> None:
	I.slow_render = False # reset next frame
	for event in pygame.event.get():
		if event.type == pygame.QUIT: die()
		elif I.editor_mode: editor.handle_event(event)
		elif event.type == pygame.KEYDOWN: handle_keydown(event.key)
		elif event.type == pygame.MOUSEMOTION: handle_mouse(event.rel[0])

def run() -> NoReturn:
	while True:
		handle_events()
		if not I.editor_mode: entities.update()
		engine.clear()
		if I.editor_mode: editor.render.perform()
		else: render.perform()
		engine.update()
