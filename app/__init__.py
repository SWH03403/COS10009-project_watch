from dataclasses import dataclass, field
import pygame
from pygame import Color, Surface
from pygame.time import Clock
from app.entity import Direction, Player
from app.render import Renderer
from app.utils.math import Vec2
from app.world import Level, LevelLoader, Room

TITLE: str = "The Game"
RESOLUTION: tuple[int, int] = 800, 450
FPS: int = 60
SENSITIVITY: float = 16.

def default_screen() -> Surface:
	return pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN | pygame.SCALED)

@dataclass
class Backend:
	background: Surface = field(init=False)
	screen: Surface = field(default_factory=default_screen)
	clock: Clock = field(default_factory=Clock)

	def __post_init__(self) -> None:
		self.background = Surface(self.screen.get_size()).convert()
		self.background.fill((0, 0, 0))
		pygame.display.set_caption(TITLE)
		pygame.mouse.set_relative_mode(True)

	def clear(self) -> None:
		self.screen.blit(self.background, (0, 0))

	def update(self) -> None:
		pygame.display.flip()

	def tick(self) -> float:
		return self.clock.tick(FPS) / 1000. # seconds

@dataclass
class App:
	running: bool = True
	player: Player = field(default_factory=Player)
	level: Level = field(init=False)
	_renderers: dict[int, Renderer] = field(default_factory=dict)
	_backend: Backend = field(default_factory=Backend)
	_delta: float = 0.

	def _update_camera_position(self) -> None:
		player = self.player.position.coord
		aim = -self.player.aim
		for renderer in self._renderers.values():
			renderer.set_position(player, aim)
			renderer.set_redraw()

	def _load_room(self, idx: int) -> None:
		if idx in self._renderers: return
		room = self.level.rooms[idx]
		doors = self.level.get_doors(idx)
		self._renderers[idx] = Renderer(self._backend.screen, room, doors)

	def __post_init__(self) -> None:
		self.level = LevelLoader("test").into_level() # DEBUG:
		self.player.position.coord = self.level.spawn
		self._load_room(0)
		self._update_camera_position()

	def _handle_keydown(self, key: int) -> bool:
		match key:
			case pygame.K_ESCAPE | pygame.K_q:
				self.running = False

	def _handle_key(self) -> bool:
		keys = pygame.key.get_pressed()

		# player movement
		direction = Vec2()
		if keys[pygame.K_w]: direction += Direction.FORWARD
		if keys[pygame.K_s]: direction += Direction.BACKWARD
		if keys[pygame.K_a]: direction += Direction.LEFT
		if keys[pygame.K_d]: direction += Direction.RIGHT
		self.player.sprinting = keys[pygame.K_LSHIFT]
		self.player.step(direction, self._delta)

		if direction.length_squared() > 0:
			self._update_camera_position()

	def _handle_mouse(self, rel: int) -> None:
		self.player.aim -= rel * SENSITIVITY * self._delta
		if rel != 0:
			self._update_camera_position()

	def _handle_events(self) -> bool:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: self.running = False
			elif event.type == pygame.KEYDOWN: self._handle_keydown(event.key)
			elif event.type == pygame.MOUSEMOTION: self._handle_mouse(event.rel[0])

	def run(self) -> None:
		while self.running:
			self._handle_events()
			self._handle_key()

			self._backend.clear()
			self._renderers[0].render() # DEBUG:
			self._backend.update()
			self._delta = self._backend.tick()

		pygame.quit()
