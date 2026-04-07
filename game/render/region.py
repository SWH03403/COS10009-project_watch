from dataclasses import dataclass

from game.engine import RESOLUTION

ASPECT: float = 4 / 3

# limit rendering for most elements
@dataclass
class RenderRegion:
	w: int
	h: int
	offset_x: int
	offset_y: int

I: RenderRegion

def offset(x: int, y: int) -> tuple[int, int]:
	return (x + I.offset_x, y + I.offset_y)

def init() -> None:
	global I

	# render into a 3:4 region on a 16:9 surface for special effect
	sw, sh = RESOLUTION
	w = int(sh * ASPECT)
	x = int((sw - w) / 2)
	I = RenderRegion(w=w, h=sh, offset_x=x, offset_y=0)

def get_size() -> tuple[int, int]:
	return I.w, I.h

def get_width() -> int:
	return I.w

def get_height() -> int:
	return I.h
