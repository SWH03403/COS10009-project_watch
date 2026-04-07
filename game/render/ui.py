from dataclasses import dataclass
import math
from time import monotonic
import pygame
from pygame import Color, Surface, Vector2

from game import engine
from game.entity import player
from . import region

COLOR: str = "gray80"
COLOR_LOW: str = "red3"
LOW_THRESHOLD = .4
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
	screen = engine.get_screen()
	stamina = player.get_stamina()
	bar = I.stamina.surface
	now = monotonic()
	if stamina < 1: I.stamina.last_full = now
	transparency = min((now - I.stamina.last_full) / FADE, 1)
	if transparency >= 1: return
	fill_color = Color(COLOR_LOW if stamina <= LOW_THRESHOLD else COLOR)
	fill_color.a = int(255 * (1 - transparency))
	bar.fill(fill_color)

	bw, bh = bar.size
	bar = I.stamina.surface.subsurface((0, 0, bw * stamina, bh))
	pos = I.stamina.position.copy()
	pos.x += bw * (1 - stamina) / 2
	screen.blit(bar, pos)
