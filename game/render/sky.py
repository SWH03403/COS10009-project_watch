from dataclasses import dataclass
import math
import pygame
from pygame import Surface

from game import engine
from game.entities import player
from game.loaders import load_skybox
from . import region
from .region import ASPECT, offset

HORIZONTAL_FOV: float = 90 # because of y-division

@dataclass
class SkyRenderer:
	image: Surface

I: SkyRenderer

def init() -> None:
	global I

	# find vertical fov to correctly stretch skybox image
	height = region.get_height()
	vertical_fov = 2 * math.atan(math.tan(math.radians(HORIZONTAL_FOV) / 2) / ASPECT)
	width = height / math.degrees(vertical_fov) * 360

	image = pygame.transform.scale(load_skybox("cloudy"), (width, height))
	I = SkyRenderer(image=image)

def render() -> None:
	screen = engine.get_screen()
	width = I.image.get_width()
	rw, rh = region.get_size()
	scroll = (1 - player.get_aim() / 360) * width
	if scroll + rw < width:
		sky = I.image.subsurface((scroll, 0, rw, rh))
		screen.blit(sky, offset(0, 0))
		return

	left = width - scroll
	right = rw - left
	s1 = I.image.subsurface((scroll, 0, left, rh))
	s2 = I.image.subsurface((0, 0, right, rh))
	screen.blit(s1, offset(0, 0))
	screen.blit(s2, offset(left, 0))
