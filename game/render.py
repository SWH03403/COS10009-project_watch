from copy import copy
from dataclasses import dataclass
import math
from time import sleep
import pygame
from pygame import Color, draw
from pygame.math import clamp, invlerp, lerp, remap
from pygame.typing import ColorLike

import game
from game import engine
from game.entity import player
from game.utils.math import Line, Vec2
from game.world.level import Fog, get_walls

NEAR_PLANE: float = 1e-3
EXTEND_THRESHOLD: float = 1e6

@dataclass
class ScopedSector:
	id: int
	min_x: int
	max_x: int

@dataclass
class Renderer:
	queue: list[ScopedSector]
	mask: list[tuple[int, int]]

I: Renderer

def init() -> None:
	global I
	I = Renderer(queue=[], mask=[])

def debug_delay() -> None:
	if game.is_scan_mode():
		sleep(5e-3)
		pygame.display.update()

def world_to_screen(p: Vec2, floor: float, ceiling: float) -> tuple[Vec2, Vec2]:
	w, h = engine.get_screen().get_size()
	eye = player.get_absolute_eye_height()

	x = remap(-1, 1, 0, w, p.x / p.y)
	y1 = remap(0, 1, h / 2, 0, (ceiling - eye) / p.y)
	y2 = remap(0, 1, h / 2, h, (eye - floor) / p.y)
	return Vec2(x, y1), Vec2(x, y2)

def line(color: Color, x: float, y1: float, y2: float) -> None:
	screen = engine.get_screen()
	draw.line(screen, color, (x, y1), (x, y2))
	debug_delay()

def render_floor(
	eye_diff: float,
	color: ColorLike,
	fog: Fog,
	mask: list[tuple[int, int]],
	wall: Line,
	right_further: bool,
	x_range: tuple[int, int],
	y_range: tuple[int, int],
	y_fog_levels: tuple[float, float], # screen coordinate of near & far
) -> None:
	screen = engine.get_screen()
	left, right = x_range
	near_on_far = Line.from_point(Vec2(fog.far, eye_diff)).get_y(fog.near)
	for y in range(*y_range):
		for min_x in range(left, len(I.mask)):
			min_y, max_y = mask[min_x]
			if min_y <= y <= max_y: break
		for max_x in range(right - 1, -1, -1):
			min_y, max_y = mask[max_x]
			if min_y <= y <= max_y: break

		if not wall.is_horz():
			intersect = wall.get_x(y)
			if right_further: min_x = max(min_x, intersect)
			else: max_x = min(max_x, intersect)
		if min_x >= max_x: continue

		fact = invlerp(*y_fog_levels, y)
		blended = Color(color)
		if fact >= 1: blended = fog.color
		elif fact > 0:
			proj_y = lerp(eye_diff, near_on_far, fact)
			ray = Line.from_point(Vec2(fog.near, proj_y))
			dist = ray.get_x(eye_diff)
			fog_fact = invlerp(fog.near, fog.far, dist)
			blended = blended.lerp(fog.color, fog_fact)
		draw.line(screen, blended, (min_x, y), (max_x, y))
		debug_delay()

def render_sector(scoped: ScopedSector) -> None:
	level = game.get_level()
	sector = level.sectors[scoped.id]
	screen = engine.get_screen()
	h = screen.get_height()

	eye = player.get_absolute_eye_height()
	eye_to_floor = eye - sector.floor
	eye_to_ceil = sector.ceiling - eye
	fog = level.fog # FIX: use sector-specific fog
	fog_coords = []
	fog_coords.extend(world_to_screen(Vec2(0, fog.near), sector.floor, sector.ceiling))
	fog_coords.extend(world_to_screen(Vec2(0, fog.far), sector.floor, sector.ceiling))
	fog_ys = [int(p.y) for p in fog_coords]

	walls = get_walls(level, scoped.id, True)
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

		left_x = int(clamp(l_top.x, scoped.min_x, scoped.max_x))
		right_x = int(clamp(r_top.x, scoped.min_x, scoped.max_x))

		# extend to edge of scope if wall plane cuts through eye
		if abs(l_top.y) >= EXTEND_THRESHOLD: left_x = scoped.min_x
		if abs(r_top.y) >= EXTEND_THRESHOLD: right_x = scoped.max_x

		# get screen coordinate for window to neighbor sector
		nl_top, nl_bot, nr_top, nr_bot = None, None, None, None
		if connect is not None:
			neighbor = level.sectors[connect]
			nl_top, nl_bot = world_to_screen(left, neighbor.floor, neighbor.ceiling)
			nr_top, nr_bot = world_to_screen(right, neighbor.floor, neighbor.ceiling)
			I.queue.append(ScopedSector(connect, left_x, right_x))

		last_mask = copy(I.mask)
		flrs = [h, 0, h, 0]

		for x in range(left_x, right_x):
			min_y, max_y = I.mask[x]
			if min_y >= max_y: continue

			camera_dist = 0
			if l_top.x != r_top.x:
				fact = invlerp(l_top.x, r_top.x, x)
				proj_x = lerp(left.x, right_proj_x, fact)
				proj_vec = Vec2(proj_x, left.y)
				if abs(proj_vec.cross(left - right)) > proj_vec.epsilon:
					proj = Line.from_point(proj_vec)
					world_pos = proj.intersect(wall)
					camera_dist = world_pos.length()
			else:
				fact = 1 if x > l_top.x else 0

			fog_amt = clamp(invlerp(fog.near, fog.far, camera_dist), 0, 1) * fog.intensity
			blended = Color("darkkhaki").lerp(fog.color, fog_amt)
			top = int(clamp(lerp(l_top.y, r_top.y, fact), min_y, max_y))
			bot = int(clamp(lerp(l_bot.y, r_bot.y, fact), min_y, max_y))

			if connect is None:
				line(blended, x, top, bot) # solid wall
				I.mask[x] = (-1, -1)
			else:
				ntop = int(clamp(lerp(nl_top.y, nr_top.y, fact), min_y, max_y))
				nbot = int(clamp(lerp(nl_bot.y, nr_bot.y, fact), min_y, max_y))
				I.mask[x] = (max(top, ntop), min(bot, nbot))
				if game.is_scan_mode(): line("crimson", x, *I.mask[x])
				if ntop > top: line(blended, x, top, ntop)
				if nbot < bot: line(blended, x, nbot, bot)

			flrs[0] = min(flrs[0], min_y)
			flrs[1] = max(flrs[1], top)
			flrs[2] = min(flrs[2], bot)
			flrs[3] = max(flrs[3], max_y)

		if eye_to_ceil > 0:
			right_further = l_top.y < r_top.y
			render_floor(
				eye_to_ceil, "khaki4", fog, last_mask, Line.from_point(l_top, r_top), right_further,
				(left_x, right_x), (flrs[0], flrs[1]), (fog_ys[0], fog_ys[2])
			)
		if eye_to_floor > 0:
			right_further = l_bot.y > r_bot.y
			render_floor(
				eye_to_floor, "darkslategrey", fog, last_mask, Line.from_point(l_bot, r_bot), right_further,
				(left_x, right_x), (flrs[2], flrs[3] + 1), (fog_ys[1], fog_ys[3])
			)

def update() -> None:
	w, h = engine.get_screen().get_size()
	_, current_sector = player.get_position()
	I.queue = [ScopedSector(current_sector, 0, w)]

	# reset render mask
	I.mask = [(0, h) for _ in range(w)]

	while len(I.queue) > 0:
		scoped = I.queue.pop(0)
		if scoped.min_x >= scoped.max_x: continue
		render_sector(scoped)
