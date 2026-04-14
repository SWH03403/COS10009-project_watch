from enum import Enum, auto
from random import random, randrange
import sys
from time import monotonic, sleep
import pygame
from pygame.math import Vector2, clamp

from . import library
from .library import Image, Sound

NOISE_DUR: float = 3.5
EYE_ORIGIN: Vector2 = None
EYE_CHANCE: float = .2

class Cause(Enum):
	SYSTEM = auto()
	FALL = auto()
	CAUGHT = auto()

def init() -> None:
	from game.engine import LOW_RES

	eye = library.get_image(Image.EYE) # preload
	global EYE_ORIGIN
	EYE_ORIGIN = (Vector2(LOW_RES) - Vector2(eye.size)) / 2

def flash_eye() -> None:
	from game import engine
	eye = library.get_image(Image.EYE)
	screen = engine.get_screen()
	screen.blit(eye, EYE_ORIGIN, special_flags=pygame.BLEND_ALPHA_SDL2)

def flash(color: str, delay: float) -> None:
	from game import engine
	screen = engine.get_screen()
	screen.fill(color)
	if color == "black" and random() <= EYE_CHANCE:
		flash_eye()
		engine.update()
		sleep(.01)
		screen.fill(color)
	engine.update()
	sleep(delay)

def noise(alpha: float) -> None:
	from game import engine
	from game.render import region
	img = library.get_image(Image.NOISE)
	w, h = region.get_size()
	x, y = randrange(img.width - w), randrange(img.height - h)
	img_small = img.subsurface((x, y, w, h))
	img_small.set_alpha(int(255 * clamp(alpha, 0, 1)))
	engine.get_screen().blit(img_small, region.get_origin())

def execute(cause: Cause = Cause.SYSTEM) -> None:
	match cause:
		case Cause.SYSTEM:
			flash("black", .1)
		case Cause.CAUGHT:
			until = monotonic() + NOISE_DUR
			pygame.mixer.stop()
			library.play_sound(Sound.DEATH_CAUGHT)
			pygame.display.set_gamma(2, .2, .2)
			now = 0
			while now < until:
				flash_eye()
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
