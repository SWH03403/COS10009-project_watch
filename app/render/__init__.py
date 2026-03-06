from dataclasses import dataclass, field
import math
from pygame import draw, Color, Surface, Vector2
from pygame.math import clamp, invlerp, lerp, remap
from app.world import Fog, Room

WALL_HEIGHT: float = 60.
PLAYER_HEIGHT: float = 20.
NEAR_PLANE: float = 1.

@dataclass
class Renderer:
	surface: Surface

	@staticmethod
	def _transform(target: Vector2, origin: Vector2, rotate: float) -> Vector2:
		return (target - origin).rotate(rotate)

	def _world_to_screen(self, p: Vector2) -> tuple[Vector2, Vector2]:
		w, h = self.surface.get_size()
		x = remap(-1., 1., 0, w, p[0] / p[1])
		y = remap(0., 1., h / 2., 0., (WALL_HEIGHT - PLAYER_HEIGHT) / p[1])
		py = remap(0., 1., h / 2., h, PLAYER_HEIGHT / p[1])
		return Vector2(x, y), Vector2(x, py)

	def _wall(self, left: Vector2, right: Vector2, color: Color, fog: Fog) -> None:
		# Only render if facing the player
		facing = math.atan2(left[0], left[1]) - math.atan2(right[0], right[1])
		if 0 <= facing <= math.pi:
			return

		# Only render if in front of the player
		left_behind, right_behind = left[1] < NEAR_PLANE, right[1] < NEAR_PLANE
		if left_behind and right_behind:
			return

		# Cut wall to near plane
		if left_behind or right_behind:
			cross_fact = (NEAR_PLANE - left[1]) / (right[1] - left[1])
			cross_x = left[0] + (right[0] - left[0]) * cross_fact
			clamped = Vector2(cross_x, NEAR_PLANE)
			if left_behind:
				left = clamped
			else:
				right = clamped

		l_top, l_bot = self._world_to_screen(left)
		r_top, r_bot = self._world_to_screen(right)

		w, h = self.surface.get_size()
		left_x, right_x = int(clamp(l_top[0], 0., w)), int(clamp(r_top[0], 0., w))
		left_dist, right_dist = left.length(), right.length()
		for x in range(left_x, right_x):
			fact = invlerp(l_top[0], r_top[0], x)
			top = max(0., lerp(l_top[1], r_top[1], fact))
			bot = min(h, lerp(l_bot[1], r_bot[1], fact))

			dist = lerp(left_dist, right_dist, fact)
			fact = invlerp(fog.near, fog.far, dist)
			blended = Color(*tuple(lerp(c, f, fact) for c, f in zip(color, fog.color)))

			draw.line(self.surface, blended, (x, top), (x, bot))

	def room(self, room: Room, origin: Vector2, rotate: float) -> None:
		assert len(room.corners) > 2
		corners = [Renderer._transform(p, origin, rotate) for p in room.corners]
		for i in range(len(corners) - 1):
			self._wall(corners[i], corners[i + 1], room.wall, room.fog)
		self._wall(corners[-1], corners[0], room.wall, room.fog)
