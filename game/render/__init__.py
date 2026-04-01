from dataclasses import dataclass
import math
from pygame import Color, draw
from pygame.math import clamp, invlerp, lerp, remap

import game
from game import engine
from game.utils.math import Line, Vec2
from game.world import Sector
from .window import Window, current_sector, get_y_range
from .calc import transform_to_player, world_to_screen

NEAR_PLANE: float = 1
SHADE: Color = Color("black")
TRANSPARENT: Color = Color(0, 0, 0, 0)

@dataclass
class Renderer:
	queue: list[Window]
	rendered_sectors: set[int]

I: Renderer

def init() -> None:
	global I
	I = Renderer(queue=[], rendered_sectors=set())

def _render_sector(window: Window) -> None:
	level = game.get_level()
	sector = level.sectors[window.sector]
	vertexes = [level.vertexes[idx] for idx in sector.vertexes]
	vertexes = transform_to_player(vertexes)
	screen = engine.get_screen()

	n_walls = len(sector.vertexes)
	walls = [(vertexes[i], vertexes[i - n_walls + 1]) for i in range(n_walls)]
	for left, right in walls:
		# only render if facing the player
		facing = math.atan2(left.x, left.y) - math.atan2(right.x, right.y)
		if 0 <= facing <= math.pi: continue

		# only render if in front of the player
		left_behind, right_behind = left.y < NEAR_PLANE, right.y < NEAR_PLANE
		if left_behind and right_behind: continue

		# cut wall to near plane
		if left_behind or right_behind:
			cross_fact = (NEAR_PLANE - left.y) / (right.y - left.y)
			cross_x = left.x + (right.x - left.x) * cross_fact
			clamped = Vec2(cross_x, NEAR_PLANE)
			if left_behind: left = clamped
			else: right = clamped

		right_proj = Line.from_point(right)
		right_proj_x = right_proj.get_x(left.y)
		wall = Line.from_point(left, right)

		l_top, l_bot = world_to_screen(left, sector.floor, sector.ceiling)
		r_top, r_bot = world_to_screen(right, sector.floor, sector.ceiling)

		left_x = int(clamp(l_top.x, window.top_left.x, window.top_right.x))
		right_x = int(clamp(r_top.x, window.top_left.x, window.top_right.x))
		for x in range(left_x, right_x):
			fact = invlerp(l_top.x, r_top.x, x)
			proj_x = lerp(left.x, right_proj_x, fact)
			proj = Line.from_point(Vec2(proj_x, left.y))
			world_pos = proj.intersect(wall)

			camera_dist = world_pos.length()
			light_dist = 20. # FIX: implement lighting
			fog = level.fog # FIX: use sector-specific fog
			fog_amt = clamp(invlerp(fog.near, fog.far, camera_dist), 0, 1) * fog.intensity
			shade_amt = 1 - clamp(200 / light_dist, 0, 1)
			blended = Color("crimson").lerp(fog.color, fog_amt).lerp(SHADE, shade_amt)
			min_y, max_y = get_y_range(window, x)
			top = max(min_y, lerp(l_top.y, r_top.y, fact))
			bot = min(max_y, lerp(l_bot.y, r_bot.y, fact))

			# FIX: Shade floor and ceiling??
			if min_y < top: draw.line(screen, "darkgreen", (x, min_y), (x, top)) # ceiling
			if max_y > bot: draw.line(screen, "blue", (x, bot), (x, max_y)) # floor
			draw.line(screen, blended, (x, top), (x, bot))

def update() -> None:
	I.queue = [current_sector()]
	I.rendered_sectors.clear()

	while len(I.queue) > 0:
		window = I.queue.pop(0)
		if window.sector in I.rendered_sectors: continue
		I.rendered_sectors.add(window.sector)
		_render_sector(window)
