import math
import pygame
from pygame import Vector2

import game
from game import engine
from .. import editor

GRID_COLOR: str = "gray12"
GRID_COLOR_ORIGIN: str = "gray36"
LINE_SPACING: float = 50

def get_line_width(adhoc_scale: float = 1) -> int:
	return max(round(editor.get_zoom() * adhoc_scale), 1)

def render_grid() -> None:
	screen = engine.get_screen()
	w, h = screen.size
	scale = editor.get_zoom()
	spacing = LINE_SPACING * scale
	lw = get_line_width()
	origin = editor.get_origin()

	nx, ny = math.ceil(w / spacing), math.ceil(h / spacing)
	x0, y0 = int(origin.x % spacing), int(origin.y % spacing)
	for i in range(nx):
		x = x0 + spacing * i
		if x == origin.x: continue
		pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, h), lw)
	for i in range(ny):
		y = y0 + spacing * i
		if y == origin.y: continue
		pygame.draw.line(screen, GRID_COLOR, (0, y), (w, y), lw)

	# render origin line last so it's on top
	if 0 <= origin.x <= w:
		pygame.draw.line(screen, GRID_COLOR_ORIGIN, (origin.x, 0), (origin.x, h), lw)
	if 0 <= origin.y <= h:
		pygame.draw.line(screen, GRID_COLOR_ORIGIN, (0, origin.y), (w, origin.y), lw)

	# render dots
	for i in range(-1, nx):
		for j in range(-1, ny):
			for pi, pj in [(0, 0), (0, 3), (3, 0), (3, 3)]:
				x = x0 + spacing * (i + (pi + 1) / 5)
				y = y0 + spacing * (j + (pj + 1) / 5)
				pygame.draw.circle(screen, GRID_COLOR, (x, y), lw)

def xy_to_screen(p: Vector2) -> Vector2:
	scaled = p * editor.get_zoom()
	scaled.y *= -1
	return editor.get_origin() + scaled

def render_level() -> None:
	screen = engine.get_screen()
	level = game.get_level()
	lw = get_line_width(1.5)
	rendered_wall = set()
	for sector in level.sectors:
		for i, wall in enumerate(sector.walls):
			left, right = wall.vertex, sector.walls[i - len(sector.walls) + 1].vertex
			if left > right: left, right = right, left
			if (left, right) in rendered_wall: continue
			rendered_wall.add((left, right)) # FIX: consider different wall types

			left = xy_to_screen(level.vertexes[left])
			right = xy_to_screen(level.vertexes[right])
			pygame.draw.line(screen, "white", left, right, lw)

def perform() -> None:
	render_grid()
	render_level()
