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
from game.world import Fog
from game.world.level import get_walls

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

def world_y_to_screen(y: float, z: float) -> float:
	h = engine.get_screen().get_height()
	return remap(0, 1, h / 2, 0, z / y)

def world_to_screen(p: Vec2, z: float) -> Vec2:
	w = engine.get_screen().get_width()
	return Vec2(remap(-1, 1, 0, w, p.x / p.y), world_y_to_screen(p.y, z))

def line(color: Color, x: float, y1: float, y2: float) -> None:
	screen = engine.get_screen()
	draw.line(screen, color, (x, y1), (x, y2))
	debug_delay()

def render_floor(
	eye_diff: float,
	color: ColorLike,
	fog: Fog,
	mask: list[tuple[int, int]],
	left: Vec2,
	right: Vec2,
	x_range: tuple[int, int],
	y_range: range,
) -> None:
	screen = engine.get_screen()
	near_on_far = Line.from_point(Vec2(fog.far, eye_diff)).get_y(fog.near)
	y_fog_near = world_y_to_screen(fog.near, eye_diff)
	y_fog_far = world_y_to_screen(fog.far, eye_diff)
	right_further = left.y * eye_diff < right.y * eye_diff # multiply for sign only

	for y in y_range:
		for min_x in range(x_range.start, len(I.mask)):
			min_y, max_y = mask[min_x]
			if min_y <= y <= max_y: break
		for max_x in range(x_range.stop - 1, -1, -1):
			min_y, max_y = mask[max_x]
			if min_y <= y <= max_y: break

		if left.y != right.y:
			intersect = Line.from_point(left, right).get_x(y)
			if right_further: min_x = max(min_x, intersect)
			else: max_x = min(max_x, intersect)
		if min_x >= max_x: continue

		fact = invlerp(y_fog_near, y_fog_far, y)
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

	z_player = player.get_absolute_eye_height()
	z_floor = sector.floor - z_player
	z_ceil = sector.ceiling - z_player
	fog = sector.fog

	walls = get_walls(level, scoped.id, True)
	for left, right, neighbor_id in walls:
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

		# wall corners
		left_top = world_to_screen(left, z_ceil)
		left_bottom = world_to_screen(left, z_floor)
		right_top = world_to_screen(right, z_ceil)
		right_bottom = world_to_screen(right, z_floor)

		# range of visible x
		left_x = int(clamp(left_top.x, scoped.min_x, scoped.max_x))
		right_x = int(clamp(right_top.x, scoped.min_x, scoped.max_x))

		# extend to edge of scope if wall plane cuts through eye
		if abs(left_top.y) >= EXTEND_THRESHOLD: left_x = scoped.min_x
		if abs(right_top.y) >= EXTEND_THRESHOLD: right_x = scoped.max_x

		# get screen coordinate for window to neighbor sector
		nb_left_top, nb_left_bottom, nb_right_top, nb_right_bottom = None, None, None, None
		if neighbor_id is not None:
			neighbor = level.sectors[neighbor_id]
			z_nb_floor = neighbor.floor - z_player
			z_nb_ceil = neighbor.ceiling - z_player
			nb_left_top = world_to_screen(left, z_nb_ceil)
			nb_left_bottom = world_to_screen(left, z_nb_floor)
			nb_right_top = world_to_screen(right, z_nb_ceil)
			nb_right_bottom = world_to_screen(right, z_nb_floor)
			I.queue.append(ScopedSector(neighbor_id, left_x, right_x))

		last_mask = copy(I.mask)
		flrs = [h, 0, h, 0]

		xs = range(left_x, right_x)
		for x in xs:
			min_y, max_y = I.mask[x]
			if min_y >= max_y: continue

			camera_dist = 0
			if left_top.x != right_top.x:
				fact = invlerp(left_top.x, right_top.x, x)
				projection = Vec2(lerp(left.x, right_proj_x, fact), left.y)
				if abs(projection.cross(left - right)) > projection.epsilon:
					world_pos = Line.from_point(projection).intersect(wall)
					camera_dist = world_pos.length()
			else: # wall plane cut through eye, becoming infinitely thin
				fact = 1 if x > left_top.x else 0

			fog_amt = clamp(invlerp(fog.near, fog.far, camera_dist), 0, 1) * fog.intensity
			blended = Color("darkkhaki").lerp(fog.color, fog_amt)
			top = int(clamp(lerp(left_top.y, right_top.y, fact), min_y, max_y))
			bottom = int(clamp(lerp(left_bottom.y, right_bottom.y, fact), min_y, max_y))

			if neighbor_id is None:
				line(blended, x, top, bottom) # solid wall
				I.mask[x] = (-1, -1)
			else:
				nb_top = int(clamp(lerp(nb_left_top.y, nb_right_top.y, fact), min_y, max_y))
				nb_bottom = int(clamp(lerp(nb_left_bottom.y, nb_right_bottom.y, fact), min_y, max_y))
				I.mask[x] = (max(top, nb_top), min(bottom, nb_bottom))
				if game.is_scan_mode(): line("crimson", x, *I.mask[x])
				if nb_top > top: line(blended, x, top, nb_top)
				if nb_bottom < bottom: line(blended, x, nb_bottom, bottom)

			flrs[0] = min(flrs[0], min_y)
			flrs[1] = max(flrs[1], top)
			flrs[2] = min(flrs[2], bottom)
			flrs[3] = max(flrs[3], max_y)

		if z_ceil > 0:
			ys = range(flrs[0], flrs[1])
			render_floor(z_ceil, "khaki4", fog, last_mask, left_top, right_top, xs, ys)
		if z_floor < 0:
			ys = range(flrs[2], flrs[3] + 1)
			render_floor(z_floor, "darkslategrey", fog, last_mask, left_bottom, right_bottom, xs, ys)

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
