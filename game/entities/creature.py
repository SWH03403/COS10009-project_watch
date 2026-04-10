from dataclasses import dataclass
from pygame import Vector2

import game
from game import engine
from . import player

KILL_DIST: float = 5

@dataclass
class Creature:
	position: Vector2 | None = None # `None` means it can not be seen (temporarily invisible)
	maintain_distance: tuple[float, float] = (100, 200)
	aggressive: bool = False

I: Creature = Creature()

def get_position() -> Vector2:
	return I.position

def is_invisible() -> bool:
	return I.position is None

def is_aggressive() -> bool:
	return I.aggressive

def update() -> None:
	if is_aggressive():
		target, _ = player.get_position()
		I.position.move_towards_ip(target, 10 * engine.get_delta())
		if (I.position - target).length() < KILL_DIST: game.die()
