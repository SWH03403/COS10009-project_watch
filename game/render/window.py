from dataclasses import dataclass

from game import engine
from game.entity import player
from game.utils.math import Vec2

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
