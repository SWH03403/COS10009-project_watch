from dataclasses import dataclass, field
from pygame import draw, Color, Surface, Vector2
from app.utils import map_range
from app.world import Fog

WALL_HEIGHT: float = 30.

@dataclass
class Renderer:
	surface: Surface

	def _world_to_screen(self, p: Vector2) -> tuple[Vector2, Vector2]:
		w, h = self.surface.get_size()
		x = map_range(p[0] / p[1], -1., 1., 0, w)
		y = map_range(WALL_HEIGHT / p[1], 0., 1., h / 2., 0.)
		return Vector2(x, y), Vector2(x, h - y)


	def _wall(self, left: Vector2, right: Vector2, color: Color, fog: Fog) -> None:
		l_top, l_bot = self._world_to_screen(left)
		r_top, r_bot = self._world_to_screen(right)
		draw.polygon(self.surface, color, [l_top, r_top, r_bot, l_bot])
