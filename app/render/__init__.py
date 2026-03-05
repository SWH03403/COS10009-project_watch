from dataclasses import dataclass, field
import math
from pygame import draw, Color, Surface, Vector2
from pygame.math import clamp, invlerp, lerp, remap
from app.utils import map_range
from app.world import Fog, Room

WALL_HEIGHT: float = 30.

@dataclass
class Renderer:
	surface: Surface

	@staticmethod
	def _transform(target: Vector2, origin: Vector2, rotate: float) -> Vector2:
		return (target - origin).rotate(rotate)

	def _world_to_screen(self, p: Vector2) -> tuple[Vector2, Vector2]:
		w, h = self.surface.get_size()
		x = map_range(p[0] / p[1], -1., 1., 0, w)
		y = map_range(WALL_HEIGHT / p[1], 0., 1., h / 2., 0.)
		return Vector2(x, y), Vector2(x, h - y)

	def _wall(self, left: Vector2, right: Vector2, color: Color, fog: Fog) -> None:
		# Only render if facing the player
		facing = math.atan2(left[0], left[1]) - math.atan2(right[0], right[1])
		if facing >= 0: return

		l_top, l_bot = self._world_to_screen(left)
		r_top, r_bot = self._world_to_screen(right)
		# draw.polygon(self.surface, color, [l_top, r_top, r_bot, l_bot]) # DEBUG: REMOVE

		w, h = self.surface.get_size()
		left_x, right_x = int(l_top[0]), int(r_top[0])
		left_dist, right_dist = left.length(), right.length()
		for x in range(left_x, right_x):
			if x < 0 or x >= w: continue
			top = max(0., map_range(x, l_top[0], r_top[0], l_top[1], r_top[1]))
			bot = min(h, map_range(x, l_top[0], r_top[0], l_bot[1], r_bot[1]))

			dist = map_range(x, l_top[0], r_top[0], left_dist, right_dist)
			fact = invlerp(fog.near, fog.far, dist)
			blended = Color(*tuple(lerp(c, f, fact) for c, f in zip(color, fog.color)))

			draw.line(self.surface, blended, (x, top), (x, bot))

	def room(self, room: Room, origin: Vector2, rotate: float) -> None:
		assert len(room.corners) > 2
		corners = [Renderer._transform(p, origin, rotate) for p in room.corners]
		for i in range(len(corners) - 1):
			self._wall(corners[i], corners[i + 1], room.wall, room.fog)
		self._wall(corners[-1], corners[0], room.wall, room.fog)
