from dataclasses import dataclass
import pygame
from pygame import FULLSCREEN, SCALED, Surface
from pygame.time import Clock
from game.assets import Image, library

TITLE: str = "watch"
LOW_RES: tuple[int, int] = 800, 450
HIGH_RES: tuple[int, int] = 1920, 1080
FPS: int = 60
BACKGROUND: str = "black"

@dataclass
class Engine:
	screen: Surface | None
	clock: Clock
	delta: float

I: Engine

def init() -> None:
	from game import EDITOR_MODE

	global I
	I = Engine(screen=None, clock=Clock(), delta=0)
	set_editor_mode(EDITOR_MODE)
	pygame.font.init()
	pygame.mixer.init()

def get_screen() -> Surface:
	return I.screen

def get_delta() -> float:
	return I.delta

def clear() -> None:
	I.screen.fill(BACKGROUND)

def update() -> None:
	pygame.display.flip()

def tick() -> None:
	I.delta = I.clock.tick(FPS) / 1000 # seconds

def set_editor_mode(enabled: bool) -> None:
	res = HIGH_RES if enabled else LOW_RES
	if I.screen is not None and I.screen.size == res: return
	I.screen = pygame.display.set_mode(res, FULLSCREEN | SCALED)
	subtitle = " (editor)" if enabled else ""
	pygame.display.set_caption(TITLE + subtitle)
	pygame.mouse.set_relative_mode(not enabled)
