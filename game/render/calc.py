from pygame.math import remap
import game
from game import engine
from game.entity import player
from game.utils.math import Vec2

def world_to_screen(p: Vec2, floor: float, ceiling: float) -> tuple[Vec2, Vec2]:
	w, h = engine.get_screen().get_size()
	_, sector_idx = player.get_position()

	level = game.get_level()
	# get eye height aelative to current sector
	sector = level.sectors[sector_idx]
	eye = player.get_eye_height() + sector.floor

	x = remap(-1, 1, 0, w, p.x / p.y)
	y1 = remap(0, 1, h / 2, 0, (ceiling - eye) / p.y)
	y2 = remap(0, 1, h / 2, h, (eye - floor) / p.y)
	return Vec2(x, y1), Vec2(x, y2)

def transform_to_player(vertexes: list[Vec2]) -> list[Vec2]:
	return [player.get_relative(v) for v in vertexes]
