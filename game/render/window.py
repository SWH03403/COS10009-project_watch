from dataclasses import dataclass
from pygame.math import clamp

from game import engine
from game.entity import player
from game.utils.math import Line, Vec2

# Drawable region for non-current sectors
@dataclass
class Window:
	sector: int

	# screen coordinates
	top_left: Vec2
	top_right: Vec2
	bottom_left: Vec2
	bottom_right: Vec2

def current_sector() -> Window:
	_, sector = player.get_position()
	w, h = engine.get_screen().get_size()
	return Window(
		sector=sector,
		top_left=Vec2(0, 0),
		top_right=Vec2(w, 0),
		bottom_left=Vec2(0, h),
		bottom_right=Vec2(w, h),
	)

def get_y_range(w: Window, x: float) -> tuple[float, float]:
	_, h = engine.get_screen().get_size()
	y1 = Line.from_point(w.top_left, w.top_right).get_y(x)
	y1 = clamp(y1, 0, h)
	y2 = Line.from_point(w.bottom_left, w.bottom_right).get_y(x)
	y2 = clamp(y2, y1, h)
	return y1, y2
