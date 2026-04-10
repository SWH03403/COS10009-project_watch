import pygame
from pygame import Rect, Vector2
from pygame.event import Event

import game
from game import editor, engine
from game.editor.common import SELECTION_PADDING, world_to_screen
from game.world import Sector
from .. import ui

TEXT_WIDTH: int = 50

def get_data(sector_id: int) -> tuple[Sector, Vector2]:
	level = game.get_level()
	sector = level.sectors[sector_id]
	vertexes = [world_to_screen(level.vertexes[wall.vertex]) for wall in sector.walls]
	origin = Vector2(max(vertexes, key=lambda v: v.x), min(vertexes, key=lambda v: v.y))
	origin.x += SELECTION_PADDING * 2
	return sector, origin

def on_mouse_event(sector_id: int, event: Event) -> bool:
	sector, origin = get_data(sector_id)
	return False

def render(sector_id: int) -> None:
	screen = engine.get_screen()
	render_text = ui.get_text_renderer()
	sector, origin = get_data(sector_id)
	for plane in [sector.ceiling, sector.floor]:
		color = "gray40" if plane.color is None else "white"
		checkbox = Rect(0, 0, ui.CHECKBOX_SIZE, ui.CHECKBOX_SIZE)
		checkbox.topleft = origin
		pygame.draw.rect(screen, color, checkbox)

		height_text = render_text(f"{plane.z:.1f}")
		x = ui.CHECKBOX_SIZE + ui.SPACING + (TEXT_WIDTH - height_text.width) / 2
		y = (ui.CHECKBOX_SIZE - render_text.font.get_linesize()) / 2
		text_origin = origin + Vector2(x, y)
		screen.blit(height_text, text_origin)

		origin.y += ui.CHECKBOX_SIZE + ui.SPACING
