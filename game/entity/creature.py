from dataclasses import dataclass
from pygame import Vector2

@dataclass
class Creature:
	position: Vector2
	maintain_distance: tuple[float, float]
	aggressive: bool

I: Creature

def init() -> None:
	global I
	I = Creature(
		position=Vector2(100, 100),
		maintain_distance=(100, 200),
		aggressive=False,
	)

def get_position() -> Vector2:
	return I.position

def is_aggressive() -> bool:
	return I.aggressive

def update() -> None:
	...
