from copy import copy
from dataclasses import dataclass
import math
from time import sleep
import pygame
from pygame import Color, Vector2, draw
from pygame.math import clamp, invlerp, lerp, remap
from pygame.typing import ColorLike

import game
from game import engine
from game.entity import player
from game.utils.math import Line
from game.world import Fog, get_walls
from . import region
from .region import offset

NEAR_PLANE: float = 1e-3
EXTEND_THRESHOLD: float = 1e6

@dataclass
class ScopedSector:
	id: int
	min_x: int
	max_x: int

@dataclass
class WorldRenderer:
	queue: list[ScopedSector]
	mask: list[tuple[int, int]]

I: WorldRenderer

def init() -> None:
	global I
	I = WorldRenderer(queue=[], mask=[])

def debug_delay() -> None:
	if game.is_scan_mode():
		sleep(1e-3)
		pygame.display.update()

def yz_to_screen(y: float, z: float) -> float:
	return remap(0, 1, region.get_height() / 2, 0, z / y)

def xyz_to_screen(p: Vector2, z: float) -> Vector2:
	return Vector2(remap(-1, 1, 0, region.get_width(), p.x / p.y), yz_to_screen(p.y, z))

def line(color: Color, x: float, y1: float, y2: float) -> None:
	screen = engine.get_screen()
	draw.line(screen, color, offset(x, y1), offset(x, y2))
	debug_delay()

def render_floor(
	eye_diff: float,
	color: ColorLike,
	fog: Fog,
	mask: list[tuple[int, int]],
	left: Vector2,
	right: Vector2,
	x_range: tuple[int, int],
	y_range: range,
) -> None:
	screen = engine.get_screen()
	near_on_far = Line.from_point(Vector2(fog.far, eye_diff)).get_y(fog.near)
	y_fog_near = yz_to_screen(fog.near, eye_diff)
	y_fog_far = yz_to_screen(fog.far, eye_diff)
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
			ray = Line.from_point(Vector2(fog.near, proj_y))
			dist = ray.get_x(eye_diff)
			fog_fact = invlerp(fog.near, fog.far, dist)
			blended = blended.lerp(fog.color, fog_fact)
		draw.line(screen, blended, offset(min_x, y), offset(max_x, y))
		debug_delay()

def render_sector(scoped: ScopedSector) -> None:
	level = game.get_level()
	sector = level.sectors[scoped.id]

	z_player = player.get_absolute_eye_height()
	z_floor = sector.floor.z - z_player
	z_ceil = sector.ceiling.z - z_player
	fog = sector.fog

	for left, right, info in get_walls(level, scoped.id, True):
		# only render if facing the player
		facing = math.atan2(left.x, left.y) - math.atan2(right.x, right.y)
		if 0 <= facing <= math.pi: continue

		# only render if in front of the player
		left_behind, right_behind = left.y < NEAR_PLANE, right.y < NEAR_PLANE
		if left_behind and right_behind: continue

		# cut wall to near plane
		wall = Line.from_point(left, right)
		if left_behind or right_behind:
			intersection = Vector2(wall.get_x(NEAR_PLANE), NEAR_PLANE)
			if left_behind: left = intersection
			else: right = intersection

		right_proj = Line.from_point(right)
		right_proj_x = right_proj.get_x(left.y)

		# wall corners
		left_top = xyz_to_screen(left, z_ceil)
		left_bottom = xyz_to_screen(left, z_floor)
		right_top = xyz_to_screen(right, z_ceil)
		right_bottom = xyz_to_screen(right, z_floor)

		# range of visible x
		left_x = int(clamp(left_top.x, scoped.min_x, scoped.max_x))
		right_x = int(clamp(right_top.x, scoped.min_x, scoped.max_x))

		# extend to edge of scope if wall plane cuts through eye
		if abs(left_top.y) >= EXTEND_THRESHOLD: left_x = scoped.min_x
		if abs(right_top.y) >= EXTEND_THRESHOLD: right_x = scoped.max_x

		# get screen coordinate for window to neighbor sector
		nb_left_top, nb_left_bottom, nb_right_top, nb_right_bottom = None, None, None, None
		if info.neighbor is not None:
			neighbor = level.sectors[info.neighbor]
			z_nb_floor = neighbor.floor.z - z_player
			z_nb_ceil = neighbor.ceiling.z - z_player
			nb_left_top = xyz_to_screen(left, z_nb_ceil)
			nb_left_bottom = xyz_to_screen(left, z_nb_floor)
			nb_right_top = xyz_to_screen(right, z_nb_ceil)
			nb_right_bottom = xyz_to_screen(right, z_nb_floor)
			I.queue.append(ScopedSector(info.neighbor, left_x, right_x))

		last_mask = copy(I.mask)
		flrs = [region.get_height(), 0] * 2

		xs = range(left_x, right_x)
		for x in xs:
			min_y, max_y = I.mask[x]
			if min_y >= max_y: continue

			camera_dist = 0
			if left_top.x != right_top.x:
				fact = invlerp(left_top.x, right_top.x, x)
				projection = Vector2(lerp(left.x, right_proj_x, fact), left.y)
				if abs(projection.cross(left - right)) > projection.epsilon:
					world_pos = Line.from_point(projection).intersect(wall)
					camera_dist = world_pos.length()
			else: # wall plane cut through eye, becoming infinitely thin
				fact = 1 if x > left_top.x else 0

			top = int(clamp(lerp(left_top.y, right_top.y, fact), min_y, max_y))
			bottom = int(clamp(lerp(left_bottom.y, right_bottom.y, fact), min_y, max_y))
			flrs[0] = min(flrs[0], min_y)
			flrs[1] = max(flrs[1], top)
			flrs[2] = min(flrs[2], bottom)
			flrs[3] = max(flrs[3], max_y)

			I.mask[x] = (-1, -1)
			if info.color is None: continue # transparent wall

			fog_amt = clamp(invlerp(fog.near, fog.far, camera_dist), 0, 1) * fog.intensity
			blended = Color(info.color).lerp(fog.color, fog_amt)

			if info.neighbor is None: # solid wall
				line(blended, x, top, bottom)
				continue

			nb_top = int(clamp(lerp(nb_left_top.y, nb_right_top.y, fact), min_y, max_y))
			nb_bottom = int(clamp(lerp(nb_left_bottom.y, nb_right_bottom.y, fact), min_y, max_y))
			I.mask[x] = (max(top, nb_top), min(bottom, nb_bottom))
			if game.is_scan_mode(): line("crimson", x, *I.mask[x])
			if nb_top > top: line(blended, x, top, nb_top)
			if nb_bottom < bottom: line(blended, x, nb_bottom, bottom)

		if z_ceil > 0 and sector.ceiling.color is not None:
			ys = range(flrs[0], flrs[1])
			render_floor(z_ceil, sector.ceiling.color, fog, last_mask, left_top, right_top, xs, ys)
		if z_floor < 0 and sector.floor.color is not None:
			ys = range(flrs[2], flrs[3] + 1)
			render_floor(z_floor, sector.floor.color, fog, last_mask, left_bottom, right_bottom, xs, ys)

def render() -> None:
	_, current_sector = player.get_position()
	w, h = region.get_size()
	I.queue = [ScopedSector(current_sector, 0, w)]

	# reset render mask
	I.mask = [(0, h) for _ in range(w)]

	while len(I.queue) > 0:
		scoped = I.queue.pop(0)
		if scoped.min_x >= scoped.max_x: continue
		render_sector(scoped)
