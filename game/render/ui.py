from dataclasses import dataclass
import math
from time import monotonic
import pygame
from pygame import Color, Surface, Vector2

from game import engine
from game.entities import player
from . import region

COLOR: str = "gray80"
COLOR_LOW: str = "red3"
LOW_THRESHOLD: float = .5
FLASH_SPEED: float = 2
FADE: float = 2 # time to disappear after bar stays full

@dataclass
class StaminaBar:
	surface: Surface
	position: Vector2
	last_full: float # the last time the bar was not full

@dataclass
class UIRenderer:
	stamina: StaminaBar

I: UIRenderer

def init() -> None:
	global I

	rw, rh = region.get_size()
	surface = Surface((rw * .75, rh / 90), pygame.BLEND_ALPHA_SDL2).convert_alpha()
	position = Vector2((rw - surface.width) / 2, (rh * 1.8 - surface.height) / 2)
	position += region.get_origin()
	stamina = StaminaBar(surface=surface, position=position, last_full=0)

	I = UIRenderer(stamina=stamina)

def render() -> None:
	if player.is_god(): return
	screen = engine.get_screen()
	stamina = player.get_stamina()
	bar = I.stamina.surface
	now = monotonic()
	if stamina < 1: I.stamina.last_full = now
	transparency = min((now - I.stamina.last_full) / FADE, 1)
	if transparency >= 1: return
	is_low = stamina <= LOW_THRESHOLD
	faster = 4 if stamina == 0 else 1
	flash = abs(math.sin(now * FLASH_SPEED * faster)) if is_low else 1
	fill_color = Color(COLOR_LOW if is_low else COLOR)
	fill_color.a = int(255 * (1 - transparency) * flash)
	bar.fill(fill_color)

	bw, bh = bar.size
	proportion = 1 if stamina == 0 else stamina
	bar = I.stamina.surface.subsurface((0, 0, bw * proportion, bh))
	pos = I.stamina.position.copy()
	pos.x += bw * (1 - proportion) / 2
	screen.blit(bar, pos)
