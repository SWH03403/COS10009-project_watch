import pygame
from game import engine
from game.assets import Image, library
from . import region

INTENSITY: float = .8

def init() -> None:
	alpha = int(255 * INTENSITY)
	library.get_image(Image.VIGNETTE).set_alpha(alpha)

def render() -> None:
	screen = engine.get_screen()
	image = library.get_image(Image.VIGNETTE)
	screen.blit(image, region.get_origin())
