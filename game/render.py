from dataclasses import dataclass
import math
from pygame import Color, draw
from pygame.math import clamp, invlerp, lerp, remap

import game
from game import engine
from game.entity import player
from game.utils.math import Line, Vec2
from game.world.level import get_walls

NEAR_PLANE: float = .001

@dataclass
class Renderer:
	queue: list[int]
	rendered: set[int]
	mask: list[tuple[int, int]]

I: Renderer

def init() -> None:
	global I
	I = Renderer(queue=[], rendered=set(), mask=[])

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

def push_queue(sector_id: int) -> None:
	I.queue.append(sector_id)

def line(color: Color, x: float, y1: float, y2: float) -> None:
	screen = engine.get_screen()
	draw.line(screen, color, (x, y1), (x, y2))

def render_sector(sector_id: int) -> None:
	level = game.get_level()
	sector = level.sectors[sector_id]
	screen = engine.get_screen()
	w = screen.get_width()

	fog = level.fog # FIX: use sector-specific fog
	# fog_coords = []
	# fog_coords.extend(world_to_screen(Vec2(0, fog.near), sector.floor, sector.ceiling))
	# fog_coords.extend(world_to_screen(Vec2(0, fog.far), sector.floor, sector.ceiling))

	walls = get_walls(level, sector_id, True)
	for left, right, connect in walls:
		# only render if facing the player
		facing = math.atan2(left.x, left.y) - math.atan2(right.x, right.y)
		if 0 <= facing <= math.pi: continue

		# only render if in front of the player
		left_behind, right_behind = left.y < NEAR_PLANE, right.y < NEAR_PLANE
		if left_behind and right_behind: continue

		# cut wall to near plane
		wall = Line.from_point(left, right)
		if left_behind or right_behind:
			intersection = Vec2(wall.get_x(NEAR_PLANE), NEAR_PLANE)
			if left_behind: left = intersection
			else: right = intersection

		right_proj = Line.from_point(right)
		right_proj_x = right_proj.get_x(left.y)

		l_top, l_bot = world_to_screen(left, sector.floor, sector.ceiling)
		r_top, r_bot = world_to_screen(right, sector.floor, sector.ceiling)

		# get screen coordinate for window to neighbor sector
		nl_top, nl_bot, nr_top, nr_bot = None, None, None, None
		if connect is not None:
			neighbor = level.sectors[connect]
			nl_top, nl_bot = world_to_screen(left, neighbor.floor, neighbor.ceiling)
			nr_top, nr_bot = world_to_screen(right, neighbor.floor, neighbor.ceiling)
			I.queue.append(connect)

		left_x = int(clamp(l_top.x, 0, w))
		right_x = int(clamp(r_top.x, 0, w))
		for x in range(left_x, right_x):
			fact = invlerp(l_top.x, r_top.x, x)
			proj_x = lerp(left.x, right_proj_x, fact)
			proj = Line.from_point(Vec2(proj_x, left.y))
			world_pos = proj.intersect(wall)

			min_y, max_y = I.mask[x]
			if min_y >= max_y: continue

			camera_dist = world_pos.length()
			fog_amt = clamp(invlerp(fog.near, fog.far, camera_dist), 0, 1) * fog.intensity
			blended = Color("crimson").lerp(fog.color, fog_amt)
			top = max(min_y, lerp(l_top.y, r_top.y, fact))
			bot = min(max_y, lerp(l_bot.y, r_bot.y, fact))

			if connect is None:
				line(blended, x, top, bot) # solid wall
				I.mask[x] = (0, 0)
			else:
				ntop = max(min_y, lerp(nl_top.y, nr_top.y, fact))
				nbot = min(max_y, lerp(nl_bot.y, nr_bot.y, fact))
				I.mask[x] = (max(top, ntop), min(bot, nbot))
				if ntop > top: line(blended, x, top, ntop)
				if nbot < bot: line(blended, x, nbot, bot)

def update() -> None:
	_, current_sector = player.get_position()
	I.queue = [current_sector]
	I.rendered.clear()

	# reset render mask
	w, h = engine.get_screen().get_size()
	I.mask = [(0, h) for _ in range(w)]

	while len(I.queue) > 0:
		sector_id = I.queue.pop(0)
		if sector_id in I.rendered: continue
		I.rendered.add(sector_id)
		render_sector(sector_id)
