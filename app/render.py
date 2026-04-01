from dataclasses import dataclass, field
import math
from pygame import draw, Color, Rect, SRCALPHA, Surface
from pygame.math import clamp, invlerp, lerp, remap
from app.utils.math import Line, Vec2
from app.world import Door, Room

WALL_HEIGHT: float = 80.
DOOR_HEIGHT: float = 60.
PLAYER_HEIGHT: float = 20.
NEAR_PLANE: float = 1.
SHADE: Color = Color(0, 0, 0)
TRANSPARENT: Color = Color(0, 0, 0, 0)

@dataclass
class Renderer:
	screen: Surface
	room: Room
	doors: list[Door]
	wall: Surface = field(init=False)
	floor: Surface = field(init=False)
	_origin: Vec2 = field(default_factory=Vec2)
	_rotate: float = 0.
	_redraw: bool = False
	_drawn_floor: bool = False

	def __post_init__(self) -> None:
		size = self.screen.get_size()
		self.wall = Surface(size, flags=SRCALPHA).convert_alpha()
		self.floor = Surface(size, flags=SRCALPHA).convert()

	def set_position(self, origin: Vec2, rotate: float) -> None:
		self._origin = origin
		self._rotate = rotate

	def set_redraw(self) -> None:
		self._redraw = True

	def _transform(self, target: Vec2) -> Vec2:
		return (target - self._origin).rotate(self._rotate)

	def _world_to_screen(self, p: Vec2) -> tuple[Vec2, Vec2]:
		w, h = self.screen.get_size()
		x = remap(-1., 1., 0, w, p.x / p.y)
		y = remap(0., 1., h / 2., 0., (WALL_HEIGHT - PLAYER_HEIGHT) / p.y)
		py = remap(0., 1., h / 2., h, PLAYER_HEIGHT / p.y)
		return Vec2(x, y), Vec2(x, py)

	def _render_wall(self, left: Vec2, right: Vec2, idx: int) -> None:
		fog = self.room.fog
		left, right = self._transform(left), self._transform(right)

		# Only render if facing the player
		facing = math.atan2(left.x, left.y) - math.atan2(right.x, right.y)
		if 0 <= facing <= math.pi:
			return

		# Only render if in front of the player
		left_behind, right_behind = left.y < NEAR_PLANE, right.y < NEAR_PLANE
		if left_behind and right_behind:
			return

		# Cache door positions
		doors = []
		for d in self.doors:
			if d.room_from.wall != idx: continue
			doors.append((d.room_from.offset, d.width))

		# Cut wall to near plane
		true_left = left
		if left_behind or right_behind:
			cross_fact = (NEAR_PLANE - left.y) / (right.y - left.y)
			cross_x = left.x + (right.x - left.x) * cross_fact
			clamped = Vec2(cross_x, NEAR_PLANE)
			if left_behind:
				left = clamped
			else:
				right = clamped

		right_proj = Line.from_point(right)
		right_proj_x = right_proj.get_x(left.y)
		wall = Line.from_point(left, right)

		# Room center for lighting
		center = sum(self.room.corners, Vec2()) / len(self.room.corners)
		center = self._transform(center)

		l_top, l_bot = self._world_to_screen(left)
		r_top, r_bot = self._world_to_screen(right)

		l_door, r_door = l_bot.copy(), r_bot.copy()
		l_door.y -= (l_bot.y - l_top.y) * DOOR_HEIGHT / WALL_HEIGHT
		r_door.y -= (r_bot.y - r_top.y) * DOOR_HEIGHT / WALL_HEIGHT

		w, h = self.screen.get_size()
		left_x, right_x = int(clamp(l_top.x, 0., w)), int(clamp(r_top.x, 0., w))
		for x in range(left_x, right_x):
			fact = invlerp(l_top.x, r_top.x, x)
			proj_x = lerp(left.x, right_proj_x, fact)
			proj = Line.from_point(Vec2(proj_x, left.y))
			world_pos = proj.intersect(wall)

			is_door = False
			dist_to_left = (world_pos - true_left).length()
			for offset, width in doors:
				if offset < dist_to_left < offset + width:
					is_door = True
					break
			cur_l_bot = l_door if is_door else l_bot
			cur_r_bot = r_door if is_door else r_bot

			camera_dist = world_pos.length()
			light_dist = (world_pos - center).length()
			fog_amt = clamp(invlerp(fog.near, fog.far, camera_dist), 0., 1.) * fog.intensity
			shade_amt = 1. - clamp(200. / light_dist, 0., 1.)
			blended = self.room.wall.lerp(fog.color, fog_amt).lerp(SHADE, shade_amt)

			top = max(0., lerp(l_top.y, r_top.y, fact))
			bot = min(h, lerp(cur_l_bot.y, cur_r_bot.y, fact))
			draw.line(self.wall, blended, (x, top), (x, bot))

	def _render_floor(self) -> None:
		endpoints = []
		endpoints.extend(self._world_to_screen(Vec2(0., self.room.fog.near)))
		endpoints.extend(self._world_to_screen(Vec2(0., self.room.fog.far)))
		top_near, bot_near, top_far, bot_far = (int(p.y) for p in endpoints)
		sw, sh = self.screen.get_size()

		# Fog right in front of camera
		fog = self.room.fog
		if top_far < 0 and bot_far > sh:
			self.floor.fill(fog.color)
			return
		clamped_top_far = max(0, top_far)
		clamped_bot_far = min(sh, bot_far)
		far = Rect(0, clamped_top_far, sw, clamped_bot_far - clamped_top_far)
		draw.rect(self.floor, fog.color, far)

		# Solid regions
		if bot_near < sh:
			region = Rect(0, bot_near, sw, sh - bot_near)
			draw.rect(self.floor, self.room.floor, region)
		if top_near > 0:
			region = Rect(0, 0, sw, top_near)
			draw.rect(self.floor, self.room.ceiling, region)

		# Gradients by distance
		ray_top_far = Line.from_point(Vec2(0., PLAYER_HEIGHT), Vec2(fog.far, WALL_HEIGHT))
		far_on_near = ray_top_far.get_y(fog.near)
		for y in range(top_near, clamped_top_far):
			fact = invlerp(top_near, top_far, y)
			proj_y = lerp(WALL_HEIGHT, far_on_near, fact)
			proj_ceil = Line.from_point(Vec2(0., PLAYER_HEIGHT), Vec2(fog.near, proj_y))
			dist = proj_ceil.get_x(WALL_HEIGHT)
			fog_fact = clamp(invlerp(fog.near, fog.far, dist), 0., 1.)
			blended = self.room.ceiling.lerp(fog.color, fog_fact)
			draw.line(self.floor, blended, (0, y), (sw, y))

		ray_bot_far = Line.from_point(Vec2(0., PLAYER_HEIGHT), Vec2(fog.far, 0.))
		far_on_near = ray_bot_far.get_y(fog.near)
		for y in range(clamped_bot_far, bot_near):
			fact = invlerp(bot_near, bot_far, y)
			proj_y = lerp(0., far_on_near, fact)
			proj_floor = Line.from_point(Vec2(0., PLAYER_HEIGHT), Vec2(fog.near, proj_y))
			dist = proj_floor.get_x(0.)
			fog_fact = clamp(invlerp(fog.near, fog.far, dist), 0., 1.)
			blended = self.room.floor.lerp(fog.color, fog_fact)
			draw.line(self.floor, blended, (0, y), (sw, y))

	def _render_room(self) -> None:
		if not self._drawn_floor:
			self.wall.fill(TRANSPARENT)
			self._render_floor()
			self._drawn_floor = True

		p = self.room.corners
		assert len(p) > 2
		self.wall.fill(TRANSPARENT)
		for i in range(len(p) - 1):
			self._render_wall(p[i], p[i + 1], i)
		self._render_wall(p[-1], p[0], len(p) - 1)
		self._redraw = False

	def blit_room(self) -> None:
		if self._redraw:
			self._render_room()
		self.screen.blit(self.wall)

	def blit_floor(self) -> None:
		self.screen.blit(self.floor)
