from dataclasses import dataclass, field
import math
from pygame import draw, Color, SRCALPHA, Surface, Vector2
from pygame.math import clamp, invlerp, lerp, remap
from app.world import Fog, Room

WALL_HEIGHT: float = 60.
PLAYER_HEIGHT: float = 20.
NEAR_PLANE: float = 1.

@dataclass
class Renderer:
	screen: Surface
	room: Room
	wall: Surface = field(init=False)
	floor: Surface = field(init=False)
	_origin: Vector2 = field(default_factory=Vector2)
	_rotate: float = 0.
	_redraw_wall: bool = False
	_redraw_floor: bool = False

	def __post_init__(self) -> None:
		size = self.screen.get_size()
		self.wall = Surface(size, flags=SRCALPHA).convert()
		self.floor = Surface(size, flags=SRCALPHA).convert()

	def set_position(self, origin: Vector2, rotate: float) -> None:
		self._origin = origin
		self._rotate = rotate

	def set_redraw_wall(self) -> None:
		self._redraw_wall = True

	@staticmethod
	def _transform(target: Vector2, origin: Vector2, rotate: float) -> Vector2:
		return (target - origin).rotate(rotate)

	def _world_to_screen(self, p: Vector2) -> tuple[Vector2, Vector2]:
		w, h = self.screen.get_size()
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

		w, h = self.screen.get_size()
		left_x, right_x = int(clamp(l_top[0], 0., w)), int(clamp(r_top[0], 0., w))
		left_dist, right_dist = left.length(), right.length()
		for x in range(left_x, right_x):
			fact = invlerp(l_top[0], r_top[0], x)
			top = max(0., lerp(l_top[1], r_top[1], fact))
			bot = min(h, lerp(l_bot[1], r_bot[1], fact))

			dist = lerp(left_dist, right_dist, fact)
			fact = clamp(invlerp(fog.near, fog.far, dist), 0., 1.) * fog.intensity
			blended = Color(*tuple(lerp(c, f, fact) for c, f in zip(color, fog.color)))

			draw.line(self.wall, blended, (x, top), (x, bot))

	def _render_room(self) -> None:
		room = self.room
		assert len(room.corners) > 2
		corners = [Renderer._transform(p, self._origin, self._rotate) for p in room.corners]
		self.wall.fill(Color(0, 0, 0, 0))
		for i in range(len(corners) - 1):
			self._wall(corners[i], corners[i + 1], room.wall, room.fog)
		self._wall(corners[-1], corners[0], room.wall, room.fog)
		self._redraw_wall = False

	def render(self) -> None:
		if self._redraw_wall:
			self._render_room()
		self.screen.blit(self.floor, (0, 0))
		self.screen.blit(self.wall, (0, 0))
