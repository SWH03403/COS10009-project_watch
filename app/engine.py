from dataclasses import dataclass, field
import math
import pygame
from pygame import Color, Surface, Vector2
from pygame.time import Clock
from app.entity import Direction, Player
from app.render import Renderer
from app.world import Room

TITLE: str = "The Game"
RESOLUTION: tuple[int, int] = 1920, 1080
FPS: int = 60
SENSITIVITY: float = 2.

# DEBUG:
TEST_ROOM = Room([Vector2(-40., 160.), Vector2(40., 180.), Vector2(40., 60.), Vector2(-40., 60.)])

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
	renderer: Renderer = field(init=False)
	player: Player = field(default_factory=Player)
	_meta: Meta = field(default_factory=Meta)
	_delta: float = 0.

	def __post_init__(self) -> None:
		self.renderer = Renderer(self._meta.screen)

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
		self.player.aim -= rel * SENSITIVITY * self._delta

	def _handle_events(self) -> bool:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: self.running = False
			elif event.type == pygame.KEYDOWN: self._handle_keydown(event.key)
			elif event.type == pygame.MOUSEMOTION: self._handle_mouse(event.rel[0])

	def _render_room(self, room: Room) -> None:
		player = self.player.position.coord
		aim = -self.player.aim
		self.renderer.room(room, player, aim)

	def run(self) -> None:
		while self.running:
			self._handle_events()
			self._handle_key()

			self._meta.clear()
			self._render_room(TEST_ROOM) # DEBUG:
			self._meta.update()
			self._delta = self._meta.tick()

		pygame.quit()
