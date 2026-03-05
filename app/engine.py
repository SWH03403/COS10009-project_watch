from dataclasses import dataclass, field
import math
import pygame
from pygame import Surface
from pygame.time import Clock
from app.entity import Direction, Player
from app.world import Room

TITLE: str = "The Game"
RESOLUTION: tuple[int, int] = 1920, 1080
FPS = 60

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
		pygame.mouse.set_visible(False)

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
			case pygame.K_w: self.player.step(Direction.FORWARD, self._delta)
			case pygame.K_a: self.player.step(Direction.LEFT, self._delta)
			case pygame.K_s: self.player.step(Direction.BACKWARD, self._delta)
			case pygame.K_d: self.player.step(Direction.RIGHT, self._delta)

	def _handle_events(self) -> bool:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: self.running = False
			elif event.type == pygame.KEYDOWN: self._handle_keydown(event.key)

	def _render_room(self, room: Room) -> None: ...

	def run(self) -> None:
		while self.running:
			self._handle_events()
			print(f"{self.player.position}") # DEBUG:
			self._meta.clear()
			self._delta = self._meta.tick()

		pygame.quit()
