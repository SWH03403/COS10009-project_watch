from random import randrange
from game import engine
from game.assets import Image, library
from . import region

INTENSITY: float = .8
NOISE_ALPHA: int = 10

def init() -> None:
	alpha = int(255 * INTENSITY)
	library.get_image(Image.VIGNETTE).set_alpha(alpha)

def render_vignette() -> None:
	image = library.get_image(Image.VIGNETTE)
	engine.get_screen().blit(image, region.get_origin())

def render_noise() -> None:
	img = library.get_image(Image.NOISE)
	w, h = region.get_size()
	x, y = randrange(img.width - w), randrange(img.height - h)
	small = img.subsurface((x, y, w, h))
	small.set_alpha(NOISE_ALPHA)
	engine.get_screen().blit(small, region.get_origin())

def render() -> None:
	render_vignette()
	render_noise()
