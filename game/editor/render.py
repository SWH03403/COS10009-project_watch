from dataclasses import dataclass, field
import math
import pygame
from pygame import Rect, Vector2
from pygame.typing import ColorLike

import game
from game import engine
from game.entity import player
from game.world.sector import WallType
from .. import editor
from . import cache, selection
from .calc import snap_to_grid, world_to_screen
from .keys import EditMode
from .selection import Selection

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
	hover_target: Selection = None
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

	vertexes = [world_to_screen(v) for v in level.vertexes]
	for (left, right), refs in cache.get_walls().items():
		left, right = vertexes[left], vertexes[right]
		types = [r.typ for r in refs][:2] # get at most 2
		for i, typ in enumerate(types):
			start = left.lerp(right, i / len(types))
			end = left.lerp(right, (i + 1) / len(types))
			if typ == WallType.SKY: line_dashes("firebrick3", start, end, no_wall)
			elif typ == WallType.SOLID: pygame.draw.line(screen, "white", start, end, solid_wall)
			else: line_dashes("goldenrod3", start, end, connect_wall)

	hlen = SPAWNPOINT_SIZE * editor.get_scale() / 2
	spawn_lw = connect_wall
	for spawn in level.spawns:
		x, y = world_to_screen(spawn.position)
		pygame.draw.line(screen, "springgreen2", (x - hlen, y), (x + hlen, y), spawn_lw)
		pygame.draw.line(screen, "springgreen2", (x, y - hlen), (x, y + hlen), spawn_lw)

def render_new_walls() -> None:
	sel = editor.get_selection()
	level = game.get_level()
	points = []
	snappable = False
	match editor.get_mode():
		case EditMode.DIVIDE:
			if not isinstance(sel, selection.Vertex): return
			points.append(world_to_screen(level.vertexes[sel.id]))
		case EditMode.ADD:
			if isinstance(sel, selection.Vertex):
				points.append(world_to_screen(level.vertexes[sel.id]))
				for p in editor.get_extensions():
					p = level.vertexes[p] if isinstance(p, int) else p
					points.append(world_to_screen(p))
				snappable = True
			if isinstance(sel, selection.Wall):
				...
	if len(points) == 0: return

	mouse = Vector2(pygame.mouse.get_pos())
	if snappable: mouse = snap_to_grid(mouse, True)
	hovered = selection.get_nearest(mouse)
	if not isinstance(hovered, selection.Vertex): points.append(mouse)
	else: points.append(world_to_screen(level.vertexes[hovered.id]))

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
	pos = world_to_screen(player.get_position()[0])
	aim = Vector2(0, -10).rotate(-player.get_aim()) * scale
	pygame.draw.line(screen, "firebrick1", pos, pos + aim, lw)
	pygame.draw.circle(screen, color, pos, size, lw)

def render_box_around(points: list[Vector2], selected: bool) -> None:
	screen = engine.get_screen()
	w, h = screen.size
	points = [world_to_screen(p) for p in points]
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
		center = world_to_screen(points[0])
		pygame.draw.circle(engine.get_screen(), SELECTION_COLOR, center, SELECTION_PADDING / 2)

def render_hover() -> None:
	mouse = pygame.mouse.get_pos()
	if mouse != I.hover_position:
		I.hover_position = mouse
		I.hover_target = selection.get_nearest(Vector2(mouse))
		I.hover_points = selection.get_vertexes(I.hover_target)
	if editor.get_mode() == EditMode.DIVIDE and not isinstance(I.hover_target, selection.Vertex):
		return
	if I.hover_target is not None and I.hover_target == editor.get_selection(): return
	if len(I.hover_points) > 0: render_box_around(I.hover_points, False)

def perform() -> None:
	render_grid()
	render_level()
	render_new_walls()
	render_player()
	render_selection()
	render_hover()
