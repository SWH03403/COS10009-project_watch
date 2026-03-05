from dataclasses import dataclass, field
import math
import pygame
from pygame import Color, Surface, Vector2
from pygame.time import Clock
from app.entity import Direction, Player
from app.world import Room
from app.utils import map_range

TITLE: str = "The Game"
RESOLUTION: tuple[int, int] = 1920, 1080
FPS: int = 60
WALL_HEIGHT: float = 30.
SENSITIVITY: float = 2.

def default_screen() -> Surface:
	return pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN | pygame.SCALED)

@dataclass
class Meta:
	background: Surface = field(init=False)
	screen: Surface = field(default_factory=default_screen)
	clock: Clock = field(default_factory=Clock)

	def __post_init__(self) -> None:
		self.background = Surface(self.screen.get_size()).convert()
		self.background.fill((0, 0, 0))
		pygame.display.set_caption(TITLE)
		pygame.mouse.set_relative_mode(True)

	def clear(self) -> None: self.screen.blit(self.background, (0, 0))
	def update(self) -> None: pygame.display.flip()
	def tick(self) -> float: return self.clock.tick(FPS) / 1000. # seconds

@dataclass
class Engine:
	running: bool = True
	player: Player = field(default_factory=Player)
	_meta: Meta = field(default_factory=Meta)
	_delta: float = 0.

	def _handle_keydown(self, key: int) -> bool:
		match key:
			case pygame.K_ESCAPE | pygame.K_q: self.running = False

	def _handle_key(self) -> bool:
		keys = pygame.key.get_pressed()

		# player movement
		direction = Vector2()
		if keys[pygame.K_w]: direction += Direction.FORWARD
		if keys[pygame.K_s]: direction += Direction.BACKWARD
		if keys[pygame.K_a]: direction += Direction.LEFT
		if keys[pygame.K_d]: direction += Direction.RIGHT
		self.player.step(direction, self._delta)

	def _handle_mouse(self, rel: int) -> None:
		self.player.aim += rel * SENSITIVITY * self._delta

	def _handle_events(self) -> bool:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: self.running = False
			elif event.type == pygame.KEYDOWN: self._handle_keydown(event.key)
			elif event.type == pygame.MOUSEMOTION: self._handle_mouse(event.rel[0])

	def _world_to_screen(self, p: Vector2) -> tuple[Vector2, Vector2]:
		sw, sh = self._meta.screen.get_size()
		x = map_range(p[0] / p[1], -1., 1., 0, sw)
		y = map_range(WALL_HEIGHT / p[1], 0., 1., sh / 2., 0.)
		return Vector2(x, y), Vector2(x, sh - y)

	def _render_wall(self, p1: Vector2, p2: Vector2) -> None:
		player = self.player.position.coord
		aim = self.player.aim
		top_left, bottom_left = self._world_to_screen((p1 - player).rotate(aim))
		top_right, bottom_right = self._world_to_screen((p2 - player).rotate(aim))
		points = [top_left, top_right, bottom_right, bottom_left]
		pygame.draw.polygon(self._meta.screen, Color("red"), points)

	def _render_room(self, room: Room) -> None: ...

	def run(self) -> None:
		while self.running:
			self._handle_events()
			self._handle_key()

			self._meta.clear()
			self._render_wall(Vector2(-50., 50.), Vector2(10., 80.)) # DEBUG:
			self._render_wall(Vector2(20., 80.), Vector2(50., 40.)) # DEBUG:
			self._meta.update()
			self._delta = self._meta.tick()

		pygame.quit()
