from dataclasses import dataclass, field
from typing import Callable
from pygame import Color
from pygame.math import Vector2

def c(name: str) -> Callable[[], Color]: return lambda: Color(name)

@dataclass
class Skybox: ...

@dataclass
class Fog:
	color: Color = field(default_factory=c("gray"))
	near: float = 10.
	far: float = 100.
	intensity: float = 1.

@dataclass
class Room:
	corners: list[Vector2]
	floor: Color = field(default_factory=c("navyblue"))
	ceiling: Color = field(default_factory=c("bisque3"))
	fog: Fog | None = None

@dataclass
class Level:
	rooms: list[Room]
