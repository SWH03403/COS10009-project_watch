from dataclasses import dataclass
from time import monotonic
import pygame
from pygame import Surface, Vector2

from game import engine
from game.assets import Image, library
from game.entities import creature, player
from . import region, world

ENLARGE: float = 10

@dataclass
class CreatureRenderer:
	current: Surface
	to_change: float = 0
	was_agressive: bool = False

I: CreatureRenderer

def init() -> None:
	default = library.get_image(Image.CREATURE_FLOAT)
	library.get_image(Image.CREATURE_GRAB)

	global I
	I = CreatureRenderer(default)

def render() -> None:
	if creature.is_invisible(): return
	is_aggressive = creature.is_aggressive()

	screen = engine.get_screen()
	world_pos = player.get_relative(creature.get_position())
	if world_pos.y < creature.KILL_DIST: return
	pos = world.xyz_to_screen(world_pos, -player.get_bob_factor() / 2)
	pos = Vector2(region.offset(*pos))
	scaling_factor = ENLARGE / world_pos.y
	typ = Image.CREATURE_GRAB if is_aggressive else Image.CREATURE_FLOAT
	sprite = library.get_image(typ)
	size = Vector2(sprite.size) * scaling_factor
	pos -= size / 2

	rx, _ = region.get_origin()
	rw, rh = region.get_size()
	xs = (-size.x, rx, rx + rw - size.x, screen.width)
	if pos.x < xs[0] or xs[3] < pos.x or xs[1] < pos.x < xs[2]:
		creature.set_watched(False)
		return

	if xs[0] <= pos.x <= xs[1]:
		sub_width = min(xs[1] - pos.x, size.x)
		sub_x = 0
	else:
		sub_width = min(pos.x - xs[2], size.x)
		right = screen.width - rx
		sub_x = max(right - pos.x, 0)
		if sub_x > 0: pos.x = right

	sub_y = max(-pos.y, 0)
	sub_height = min(size.y - sub_y, rh)
	if sub_y > 0: pos.y += sub_y

	now = monotonic()
	change = (now >= I.to_change or creature.is_aggressive()) and not creature.is_watched()
	change |= I.was_agressive != is_aggressive
	if change: I.current = sprite
	creature.set_watched(True)
	I.to_change = now + creature.MIN_WATCHED_DUR
	I.was_agressive = is_aggressive

	sprite = pygame.transform.scale_by(I.current, scaling_factor)
	screen.blit(sprite.subsurface((sub_x, sub_y, sub_width, sub_height)), pos)
