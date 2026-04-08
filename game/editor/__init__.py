from dataclasses import dataclass
import pygame
from pygame import Vector2
from pygame.event import Event

import game
from game import engine
from game.world import Level
from . import render

@dataclass
class MapEditor:
	level: Level
	zoom: float
	position: Vector2

I: MapEditor = None

def init() -> None:
	global I
	position = -Vector2(engine.get_screen().size) / 2
	I = MapEditor(level=game.get_level(), zoom=1, position=position)

def get_init() -> bool:
	return I is not None

def handle_keydown(key: int) -> None:
	match key:
		case pygame.K_ESCAPE | pygame.K_q | pygame.K_LEFTBRACKET:
			game.set_editor(False)

def handle_keys() -> None:
	keys = pygame.key.get_pressed()

def handle_event(event: Event) -> None:
	...
