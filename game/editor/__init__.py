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
	origin: Vector2 # position of world coordinate (0, 0) on the screen

I: MapEditor = None

def init() -> None:
	global I
	origin = Vector2(engine.get_screen().size) / 2
	I = MapEditor(level=game.get_level(), zoom=0, origin=origin)

def get_init() -> bool:
	return I is not None

def get_zoom() -> float:
	return 2**I.zoom

def get_origin() -> Vector2:
	return I.origin * get_zoom()

def handle_keydown(key: int) -> None:
	match key:
		case pygame.K_ESCAPE:
			game.die()
		case pygame.K_q | pygame.K_LEFTBRACKET:
			game.set_editor(False)

def handle_keys() -> None:
	keys = pygame.key.get_pressed()

def handle_event(event: Event) -> None:
	...
