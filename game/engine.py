from dataclasses import dataclass
import pygame
from pygame import FULLSCREEN, SCALED, Surface
from pygame.time import Clock

TITLE: str = "The Game"
RESOLUTION: tuple[int, int] = 400, 300
FPS: int = 60
BACKGROUND: str = "black"

@dataclass
class Engine:
	screen: Surface
	clock: Clock
	delta: float

I: Engine

def init() -> None:
	screen = pygame.display.set_mode(RESOLUTION, FULLSCREEN | SCALED)
	pygame.display.set_caption(TITLE)
	pygame.mouse.set_relative_mode(True)

	global I
	I = Engine(screen=screen, clock=Clock(), delta=0)

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
