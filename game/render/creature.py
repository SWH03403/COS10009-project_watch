from dataclasses import dataclass
from random import randrange
from time import monotonic
import pygame
from pygame import Surface, Vector2

from game import engine
from game.entity import creature, player
from . import region, world

VARIANTS: int = 5
ENLARGE: float = 10
MIN_UNSEEN_DURATION: float = 3 # for the sprite to change

@dataclass
class CreatureRenderer:
	sprites: list[Surface]
	visible: bool
	variant: int
	last_change: int # variant change

I: CreatureRenderer

def init() -> None:
	from game.loaders import load_image
	global I
	sprites = []
	for i in range(VARIANTS):
		sprites.append(load_image(f"creature/float{i}", True))
		sprites.append(load_image(f"creature/grab{i}", True))
	I = CreatureRenderer(sprites=sprites, visible=False, variant=0, last_change=0)

def get_size() -> Vector2:
	idx = 1 if creature.is_aggressive() else 0
	return Vector2(I.sprites[idx].get_size())

def get_sprite(scaling_factor: float) -> Surface:
	idx = I.variant * 2
	if creature.is_aggressive(): idx += 1
	return pygame.transform.scale_by(I.sprites[idx], scaling_factor)

def render() -> None:
	if not creature.is_enabled(): return

	screen = engine.get_screen()
	world_pos = player.get_relative(creature.get_position())
	if world_pos.y < creature.KILL_DIST: return
	pos = world.xyz_to_screen(world_pos, -player.get_bob_factor() / 2)
	pos = Vector2(region.offset(*pos))
	scaling_factor = ENLARGE / world_pos.y
	size = get_size() * scaling_factor
	pos -= size / 2

	rx, _ = region.get_origin()
	rw, rh = region.get_size()
	xs = (-size.x, rx, rx + rw - size.x, screen.width)
	if pos.x < xs[0] or xs[3] < pos.x or xs[1] < pos.x < xs[2]:
		I.visible = False
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
	should_change = now >= I.last_change + MIN_UNSEEN_DURATION or creature.is_aggressive()
	if not I.visible and should_change: I.variant = randrange(VARIANTS)
	I.visible = True
	I.last_change = now

	sprite = get_sprite(scaling_factor)
	screen.blit(sprite.subsurface((sub_x, sub_y, sub_width, sub_height)), pos)
