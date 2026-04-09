from dataclasses import dataclass, field
import math
import pygame
from pygame import Rect, Vector2
from pygame.typing import ColorLike

import game
from game import engine
from game.entity import player
from .. import editor
from . import selection
from .keys import EditMode

GRID_COLOR: str = "gray12"
GRID_COLOR_ORIGIN: str = "gray36"
LINE_SPACING: float = 50
DASH_LENGTH: float = 8
MIN_PLAYER_SIZE: float = 10
SPAWNPOINT_SIZE: float = 8
SELECTION_PADDING: float = 10
SELECTION_COLOR: str = "honeydew3"
SELECTION_HOVER_COLOR: str = "lightsteelblue4"
CONNECT_COLOR: str = "lightskyblue1"

@dataclass
class Renderer:
	# prevent iterating through everything every frame
	hover_position: tuple[int, int] = (0, 0)
	hover_points: list[Vector2] = field(default_factory=list)

I = Renderer()

def get_line_width(adhoc_scale: float = 1) -> int:
	return max(round(editor.get_scale() * adhoc_scale), 1)

def render_grid() -> None:
	screen = engine.get_screen()
	w, h = screen.size
	scale = editor.get_scale()
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
	scaled = p * editor.get_scale()
	scaled.y *= -1
	return editor.get_origin() + scaled

def line_dashes(color: ColorLike, start: Vector2, end: Vector2, width: int) -> None:
	screen = engine.get_screen()
	# optimize when zoom factor is small
	if editor.get_zoom() <= -.2:
		pygame.draw.line(screen, color, start, end, width)
		return

	dashes = (start - end).length() / (DASH_LENGTH * editor.get_scale())
	fact = .5 / dashes
	segments = math.ceil(dashes)
	for i in range(segments):
		a = start.lerp(end, fact * 2 * i)
		b_fact = min(fact * (2 * i + 1.2), 1)
		b = start.lerp(end, b_fact)
		pygame.draw.line(screen, color, a, b, width)

def render_level() -> None:
	screen = engine.get_screen()
	level = game.get_level()

	connect_wall = get_line_width()
	no_wall = get_line_width(.8)
	solid_wall = get_line_width(1.5)

	rendered_wall = set()
	for sector in level.sectors:
		for i, wall in enumerate(sector.walls):
			left, right = wall.vertex, sector.walls[i - len(sector.walls) + 1].vertex
			if left > right: left, right = right, left
			if (left, right) in rendered_wall: continue
			rendered_wall.add((left, right)) # FIX: consider different wall types

			left = xy_to_screen(level.vertexes[left])
			right = xy_to_screen(level.vertexes[right])
			if wall.color is None: line_dashes("firebrick3", left, right, no_wall)
			elif wall.neighbor is None: pygame.draw.line(screen, "white", left, right, solid_wall)
			else: line_dashes("goldenrod3", left, right, connect_wall)

	hlen = SPAWNPOINT_SIZE * editor.get_scale() / 2
	spawn_lw = connect_wall
	for spawn in level.spawns:
		x, y = xy_to_screen(spawn.position)
		pygame.draw.line(screen, "springgreen2", (x - hlen, y), (x + hlen, y), spawn_lw)
		pygame.draw.line(screen, "springgreen2", (x, y - hlen), (x, y + hlen), spawn_lw)

def render_new_walls() -> None:
	sel = editor.get_selection()
	points = []
	match editor.get_mode():
		case EditMode.CONNECT:
			if not isinstance(sel, selection.Vertex): return
			level = game.get_level()
			points.append(xy_to_screen(level.vertexes[sel.id]))
	if len(points) == 0: return

	mouse = pygame.mouse.get_pos()
	hovered = selection.get_nearest(mouse)
	if not isinstance(hovered, selection.Vertex): points.append(mouse)
	else: points.append(xy_to_screen(level.vertexes[hovered.id]))

	screen = engine.get_screen()
	lw = get_line_width()
	pygame.draw.lines(screen, CONNECT_COLOR, False, points, lw)

def render_player() -> None:
	screen = engine.get_screen()
	lw = get_line_width(.8)
	scale = editor.get_scale()
	size = player.HITBOX_SIZE * scale
	color = "goldenrod1" if size < MIN_PLAYER_SIZE else "white"
	size = max(size, MIN_PLAYER_SIZE)
	pos = xy_to_screen(player.get_position()[0])
	aim = Vector2(0, -10).rotate(-player.get_aim()) * scale
	pygame.draw.line(screen, "firebrick1", pos, pos + aim, lw)
	pygame.draw.circle(screen, color, pos, size, lw)

def render_box_around(points: list[Vector2], selected: bool) -> None:
	screen = engine.get_screen()
	w, h = screen.size
	points = [xy_to_screen(p) for p in points]
	min_x, min_y = max_x, max_y = points.pop()
	pad = SELECTION_PADDING
	color = SELECTION_COLOR if selected else SELECTION_HOVER_COLOR
	line_width = 2 if selected else 1
	for x, y in points:
		min_x, max_x = min(x, min_x), max(x, max_x)
		min_y, max_y = min(y, min_y), max(y, max_y)
	if min_x > w or max_x < 0 or min_y > h or max_y < 0: return # not visible
	rect = Rect(min_x - pad, min_y - pad, max_x - min_x + pad * 2, max_y - min_y + pad * 2)
	pygame.draw.rect(screen, color, rect, line_width, int(pad / 2))

def render_selection() -> None:
	sel = editor.get_selection()
	points = selection.get_vertexes(sel)
	if len(points) > 0: render_box_around(points, True)
	if len(points) > 1:
		center = xy_to_screen(points[0])
		pygame.draw.circle(engine.get_screen(), SELECTION_COLOR, center, SELECTION_PADDING / 2)

def render_hover() -> None:
	mouse = pygame.mouse.get_pos()
	if mouse != I.hover_position:
		I.hovered_position = mouse
		sel = selection.get_nearest(mouse)
		if editor.get_mode() == EditMode.CONNECT and not isinstance(sel, selection.Vertex): return
		if sel == editor.get_selection(): return
		I.hovered_points = selection.get_vertexes(sel)
	if len(I.hovered_points) > 0: render_box_around(I.hovered_points, False)

def perform() -> None:
	render_grid()
	render_level()
	render_new_walls()
	render_player()
	render_selection()
	render_hover()
