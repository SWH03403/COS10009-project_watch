from enum import IntEnum, auto
import pygame
from pygame import Rect, Vector2
from pygame.event import Event

import game
from game import engine
from game.editor.common import SELECTION_PADDING, world_to_screen
from game.world import Sector
from game.world.sector import CEILING_COLOR, FLOOR_COLOR
from .. import ui

TEXT_WIDTH: int = 50

def get_value_step() -> float: # TODO: use this as common function
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LALT] or keys[pygame.K_RALT]: return .01
	if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]: return 20
	if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]: return 5
	return .5

class Interaction(IntEnum):
	TOGGLE_VISIBILITY = auto()
	INCREASE_HEIGHT = auto()
	DECREASE_HEIGHT = auto()

def get_data(sector_id: int) -> tuple[Sector, Vector2]:
	level = game.get_level()
	sector = level.sectors[sector_id]
	vertexes = [world_to_screen(level.vertexes[wall.vertex]) for wall in sector.walls]
	origin = Vector2(max(vertexes, key=lambda v: v.x), min(vertexes, key=lambda v: v.y))
	origin.x += SELECTION_PADDING * 2
	return sector, origin

def get_interaction(mouse: Vector2, button: int) -> Interaction | None:
	if not 0 < mouse.y < ui.CHECK: return None
	if 0 < mouse.x < ui.CHECK and button == pygame.BUTTON_LEFT:
		return Interaction.TOGGLE_VISIBILITY
	if 0 < mouse.x < ui.CHECK_S + TEXT_WIDTH:
		if button == pygame.BUTTON_WHEELUP: return Interaction.INCREASE_HEIGHT
		if button == pygame.BUTTON_WHEELDOWN: return Interaction.DECREASE_HEIGHT
	return None

def on_mouse_event(sector_id: int, event: Event) -> bool:
	sector, origin = get_data(sector_id)
	if event.type != pygame.MOUSEBUTTONDOWN: return False
	origin = event.pos - origin
	for i, plane in enumerate([sector.ceiling, sector.floor]):
		relative = Vector2(origin.x, origin.y - ui.CHECK_S * i)
		interaction = get_interaction(relative, event.button)
		if interaction is None: continue

		is_ceil = i == 0
		if interaction == Interaction.TOGGLE_VISIBILITY:
			solid = CEILING_COLOR if is_ceil else FLOOR_COLOR
			plane.color = solid if plane.color is None else None
		elif interaction == Interaction.INCREASE_HEIGHT:
			plane.height += get_value_step()
		elif interaction == Interaction.DECREASE_HEIGHT:
			plane.height -= get_value_step()
		return True
	return False

def render(sector_id: int) -> None:
	screen = engine.get_screen()
	render_text = ui.get_text_renderer()
	sector, origin = get_data(sector_id)
	for plane in [sector.ceiling, sector.floor]:
		color = "gray40" if plane.color is None else "white"
		checkbox = Rect(0, 0, ui.CHECK, ui.CHECK)
		checkbox.topleft = origin
		pygame.draw.rect(screen, color, checkbox)

		height_text = render_text(f"{plane.z:.1f}")
		x = ui.CHECK_S + (TEXT_WIDTH - height_text.width) / 2
		y = (ui.CHECK - render_text.font.get_linesize()) / 2
		text_origin = origin + Vector2(x, y)
		screen.blit(height_text, text_origin)

		origin.y += ui.CHECK_S
