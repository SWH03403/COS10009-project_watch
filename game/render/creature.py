from dataclasses import dataclass
from pygame import Surface, Vector2
from pygame.transform import scale_by

from game import engine
from game.entity import creature, player
from . import region, world

VARIANTS: int = 5
SCALE_FACTOR: float = 10

@dataclass
class CreatureRenderer:
	sprites: list[Surface]

I: CreatureRenderer

def init() -> None:
	from game.loaders import load_image
	global I
	sprites = []
	for i in range(VARIANTS):
		sprites.append(load_image(f"creature/float{i}", True))
		sprites.append(load_image(f"creature/grab{i}", True))
	I = CreatureRenderer(sprites=sprites)

def get_size() -> int:
	return I.sprites[0].width

def render() -> None:
	screen = engine.get_screen()
	world_pos = player.get_relative(creature.get_position())
	if world_pos.y < world.NEAR_PLANE: return
	pos = world.xyz_to_screen(world_pos, -player.get_bob_factor() / 2)
	pos = Vector2(region.offset(*pos))
	resized = scale_by(I.sprites[2], SCALE_FACTOR / world_pos.y)
	pos -= Vector2(resized.get_size()) / 2
	rx, _ = region.get_origin()
	rw, _ = region.get_size()
	xs = (-resized.width, rx, rx + rw - resized.width, screen.width)
	if pos.x < xs[0] or xs[3] < pos.x: return
	if xs[1] < pos.x < xs[2]: return
	if xs[0] <= pos.x <= xs[1]:
		sub_width = min(xs[1] - pos.x, resized.width)
		sub_x = 0
	else:
		sub_width = min(pos.x - xs[2], resized.width)
		right = screen.width - rx
		sub_x = max(right - pos.x, 0)
		if sub_x > 0: pos.x = right
	screen.blit(resized.subsurface((sub_x, 0, sub_width, resized.height)), pos)
