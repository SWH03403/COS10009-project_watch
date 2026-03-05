from dataclasses import dataclass, field
from typing import Callable
from pygame import Color
from pygame.math import Vector2

def c(name: str) -> Callable[[], Color]: return lambda: Color(name)

@dataclass
class Skybox: ...

@dataclass
class Fog:
	color: Color = field(default_factory=c("black"))
	near: float = 100.
	far: float = 300.
	intensity: float = 1.

@dataclass
class Room:
	corners: list[Vector2]
	wall: Color = field(default_factory=c("red"))
	floor: Color = field(default_factory=c("navyblue"))
	ceiling: Color = field(default_factory=c("bisque3"))
	fog: Fog = field(default_factory=Fog)

@dataclass
class Level:
	rooms: list[Room]
