"""limit rendering for most elements"""
from pygame import Rect
from game.engine import RESOLUTION

ASPECT: float = 4 / 3

I: Rect

def offset(x: int, y: int) -> tuple[int, int]:
	return (x + I.x, y + I.y)

def init() -> None:
	global I

	# render into a 3:4 region on a 16:9 surface for special effect
	sw, sh = RESOLUTION
	w = int(sh * ASPECT)
	x = int((sw - w) / 2)
	I = Rect(x, 0, w, sh)

def get_size() -> tuple[int, int]:
	return I.w, I.h

def get_width() -> int:
	return I.w

def get_height() -> int:
	return I.h
