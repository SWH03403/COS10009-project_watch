import math
import pygame

from game import engine
from .. import editor

GRID_COLOR: str = "gray12"
GRID_COLOR_ORIGIN: str = "gray60"
LINE_SPACING: float = 50
LINE_WIDTH: float = 1

def render_grid() -> None:
	screen = engine.get_screen()
	w, h = screen.size
	scale = editor.get_zoom()
	spacing = LINE_SPACING * scale
	lw = max(int(LINE_WIDTH * scale), 1)
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

def perform() -> None:
	render_grid()
