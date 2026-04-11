from dataclasses import dataclass
from time import monotonic
import pygame
from pygame import Surface, Vector2

from game import engine
from game.assets import Image, library
from game.entities import creature, player
from . import region, world

ENLARGE: float = 10
MIN_UNSEEN_DURATION: float = 3 # for the sprite to change

@dataclass
class CreatureRenderer:
	passive_size: Vector2
	aggressive_size: Vector2
	current: Surface # image currently being shown
	to_change: float = 0

I: CreatureRenderer

def init() -> None:
	current = library.get_image(Image.CREATURE_FLOAT)
	passive_size = Vector2(current.size)
	aggressive_size = Vector2(library.get_image(Image.CREATURE_GRAB).size)

	global I
	I = CreatureRenderer(passive_size, aggressive_size, current)

def render() -> None:
	if creature.is_invisible(): return

	screen = engine.get_screen()
	world_pos = player.get_relative(creature.get_position())
	if world_pos.y < creature.KILL_DIST: return
	pos = world.xyz_to_screen(world_pos, -player.get_bob_factor() / 2)
	pos = Vector2(region.offset(*pos))
	scaling_factor = ENLARGE / world_pos.y
	size = (I.aggressive_size if creature.is_aggressive() else I.passive_size) * scaling_factor
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
	should_change = now >= I.to_change or creature.is_aggressive()
	if not creature.is_watched() and should_change:
		typ = Image.CREATURE_GRAB if creature.is_aggressive() else Image.CREATURE_FLOAT
		I.current = library.get_image(typ)
	creature.set_watched(True)
	I.to_change = now + MIN_UNSEEN_DURATION

	sprite = pygame.transform.scale_by(I.current, scaling_factor)
	screen.blit(sprite.subsurface((sub_x, sub_y, sub_width, sub_height)), pos)
