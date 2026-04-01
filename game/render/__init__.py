from dataclasses import dataclass
import math
from pygame import Color, draw
from pygame.math import clamp, invlerp, lerp, remap

import game
from game import engine
from game.entity import player
from game.utils.math import Line, Vec2
from game.world import Sector
from .window import Window, current_sector, get_x_range, get_y_range
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

def _render_sector(window: Window) -> list[Window]:
	level = game.get_level()
	sector = level.sectors[window.sector]
	vertexes = [level.vertexes[idx] for idx in sector.vertexes]
	vertexes = transform_to_player(vertexes)
	screen = engine.get_screen()

	eye_to_floor = player.get_eye_height()
	eye_to_ceil = sector.ceiling - (eye_to_floor + sector.floor)

	# floor/ceiling fog pre-compute
	fog = level.fog # FIX: use sector-specific fog
	fog_coords = []
	fog_coords.extend(world_to_screen(Vec2(0, fog.near), sector.floor, sector.ceiling))
	fog_coords.extend(world_to_screen(Vec2(0, fog.far), sector.floor, sector.ceiling))
	y_fogs = [int(p.y) for p in fog_coords]

	# ceiling
	window_top = int(min(window.top_left.y, window.top_right.y))
	window_bot = int(max(window.bottom_left.y, window.bottom_right.y))
	y_mid = screen.get_height() // 2
	ray_far = Line.from_point(Vec2(fog.far, eye_to_ceil))
	far_on_near = ray_far.get_y(fog.near)
	for y in range(window_top, min(window_bot, y_mid)):
		x1, x2 = get_x_range(window, y)
		fact = invlerp(y_fogs[0], y_fogs[2], y)
		color = Color("darkgreen")
		if fact >= 1: color = fog.color
		else:
			proj_y = lerp(eye_to_ceil, far_on_near, fact)
			proj_floor = Line.from_point(Vec2(fog.near, proj_y))
			dist = proj_floor.get_x(eye_to_ceil)
			fog_fact = invlerp(fog.near, fog.far, dist)
			color = color.lerp(fog.color, fog_fact)
		draw.line(screen, color, (x1, y), (x2, y))

	# floor
	ray_far = Line.from_point(Vec2(fog.far, eye_to_floor))
	far_on_near = ray_far.get_y(fog.near)
	for y in range(max(window_top, y_mid), window_bot):
		x1, x2 = get_x_range(window, y)
		fact = invlerp(y_fogs[1], y_fogs[3], y)
		color = Color("blue")
		if fact >= 1: color = fog.color
		else:
			proj_y = lerp(eye_to_floor, far_on_near, fact)
			proj_floor = Line.from_point(Vec2(fog.near, proj_y))
			dist = proj_floor.get_x(eye_to_floor)
			fog_fact = invlerp(fog.near, fog.far, dist)
			color = color.lerp(fog.color, fog_fact)
		draw.line(screen, color, (x1, y), (x2, y))

	n_walls = len(sector.vertexes)
	walls = [(vertexes[i], vertexes[i - n_walls + 1], sector.connects[i]) for i in range(n_walls)]
	queued_neighbors = []
	for left, right, connect in walls:
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

		# get screen coordinate for window to neighbor sector
		nl_top, nl_bot, nr_top, nr_bot = None, None, None, None
		next_window = [] # a bad attempt to find render region
		if connect is not None:
			queued = level.sectors[connect]
			nl_top, nl_bot = world_to_screen(left, queued.floor, queued.ceiling)
			nr_top, nr_bot = world_to_screen(right, queued.floor, queued.ceiling)

		for x in range(left_x, right_x):
			fact = invlerp(l_top.x, r_top.x, x)
			proj_x = lerp(left.x, right_proj_x, fact)
			proj = Line.from_point(Vec2(proj_x, left.y))
			world_pos = proj.intersect(wall)

			camera_dist = world_pos.length()
			light_dist = 20. # FIX: implement lighting
			fog_amt = clamp(invlerp(fog.near, fog.far, camera_dist), 0, 1) * fog.intensity
			shade_amt = 1 - clamp(200 / light_dist, 0, 1)
			blended = Color("crimson").lerp(fog.color, fog_amt).lerp(SHADE, shade_amt)
			min_y, max_y = get_y_range(window, x)
			unclamped_top = lerp(l_top.y, r_top.y, fact)
			unclamped_bot = lerp(l_bot.y, r_bot.y, fact)
			top, bot = max(min_y, unclamped_top), min(max_y, unclamped_bot)

			if connect is None:
				draw.line(screen, blended, (x, top), (x, bot)) # solid wall
			else:
				unclamped_ntop = lerp(nl_top.y, nr_top.y, fact)
				unclamped_nbot = lerp(nl_bot.y, nr_bot.y, fact)
				ntop, nbot = max(min_y, unclamped_ntop), min(max_y, unclamped_nbot)
				if ntop > top: draw.line(screen, blended, (x, top), (x, ntop))
				if nbot < bot: draw.line(screen, blended, (x, nbot), (x, bot))

				if x == left_x or x == right_x - 1:
					next_window.append(Vec2(x, max(unclamped_top, unclamped_ntop)))
					next_window.append(Vec2(x, min(unclamped_bot, unclamped_nbot)))

		if connect is not None and len(next_window) == 4:
			tl, bl, tr, br = next_window
			tr.x += 1
			br.x += 1
			queued = Window(sector=connect, top_left=tl, top_right=tr, bottom_left=bl, bottom_right=br)
			queued_neighbors.append(queued)

	return queued_neighbors

def update() -> None:
	I.queue = [current_sector()]
	I.rendered_sectors.clear()

	while len(I.queue) > 0:
		window = I.queue.pop(0)
		if window.sector in I.rendered_sectors: continue
		I.rendered_sectors.add(window.sector)
		I.queue.extend(_render_sector(window))
