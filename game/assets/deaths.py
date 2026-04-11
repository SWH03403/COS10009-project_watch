from enum import Enum, auto
from random import randrange
import sys
from time import monotonic, sleep
import pygame
from pygame import Vector2

from . import library
from .library import Image, Sound

NOISE_DUR: float = 3.5

class Cause(Enum):
	SYSTEM = auto()
	FALL = auto()
	CAUGHT = auto()

def flash(color: str, delay: float) -> None:
	from game import engine
	engine.get_screen().fill(color)
	engine.update()
	sleep(delay)

def noise(alpha: float) -> None:
	from game import engine
	from game.render import region
	img = library.get_image(Image.NOISE)
	w, h = region.get_size()
	x, y = randrange(img.width - w), randrange(img.height - h)
	img_small = img.subsurface((x, y, w, h))
	img_small.set_alpha(255 * alpha)
	engine.get_screen().blit(img_small, region.get_origin())

def execute(cause: Cause = Cause.SYSTEM) -> None:
	from game import engine

	match cause:
		case Cause.CAUGHT:
			eye = library.get_image(Image.EYE)
			screen = engine.get_screen()
			origin = (Vector2(screen.size) - Vector2(eye.size)) / 2
			library.get_image(Image.NOISE) # preload
			until = monotonic() + NOISE_DUR
			pygame.mixer.stop()
			library.play_sound(Sound.DEATH_CAUGHT)
			pygame.display.set_gamma(2, .2, .2)
			now = 0
			while now < until:
				screen.blit(eye, origin, special_flags=pygame.BLEND_ALPHA_SDL2)
				noise(((1 - (until - now) / NOISE_DUR)**2) * .7 + .1)
				pygame.display.update()
				now = monotonic()
			pygame.display.set_gamma(1, 1, 1)
		case Cause.FALL:
			library.play_sound(Sound.DEATH_FALL)
			flash("red3", .1)
			flash("black", .4)

	pygame.quit()
	sys.exit()
