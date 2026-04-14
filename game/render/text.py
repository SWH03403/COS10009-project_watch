from dataclasses import dataclass
import math
from time import monotonic
import pygame
from pygame import Surface, Vector2

from game import engine
from game.entities import player
from game.utils import TextRenderer
from . import region
from .region import offset

POSITION: Vector2 = Vector2(.2, .1)
SHOW_AFTER: float = 3
BLUR_DUR: float = 3
FADE_DUR: float = 10

DISTANCE: float = 400
SAMPLES: int = 80

@dataclass
class GameText: # "watch"
	title: Surface
	god: Surface
	begin: float

I: GameText

def init() -> None:
	global I
	title = TextRenderer(32, "white", True)("watch")
	god = TextRenderer(48, "white", True)("i am god")
	I = GameText(title=title, god=god, begin=monotonic() + SHOW_AFTER)

def render_title() -> None:
	elapsed = monotonic() - I.begin
	if elapsed <= 0 or elapsed > BLUR_DUR + FADE_DUR: return
	screen = engine.get_screen()
	blur = elapsed / BLUR_DUR # standard deviation
	fade = 1
	if elapsed > BLUR_DUR: fade -= min((elapsed - BLUR_DUR) / FADE_DUR, 1)

	w, h = region.get_size()
	x = w * POSITION.x - I.title.width / 2
	y0 = h * POSITION.y - DISTANCE / 2
	base = 1 / math.sqrt(2 * math.pi) / blur
	for i in range(SAMPLES):
		y = int(y0 + DISTANCE / SAMPLES * i)
		power = -((i - SAMPLES / 2) / blur)**2 / 2
		fact = base * math.exp(power) * fade
		I.title.set_alpha(min(int(255 * fact), 255))
		screen.blit(I.title, offset(x, y), special_flags=pygame.BLEND_ALPHA_SDL2)

def render_god() -> None:
	if not player.is_god(): return
	y = region.get_size()[1] - I.god.height
	screen = engine.get_screen()
	screen.blit(I.god, offset(0, y))

def render() -> None:
	render_title()
	render_god()
