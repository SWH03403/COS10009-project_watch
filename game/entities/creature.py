from dataclasses import dataclass, field
from pygame import Vector2

import game
from game import engine
from . import player

KILL_DIST: float = 5

@dataclass
class Creature:
	invisible: bool = False # the player can not see it
	position: Vector2 = field(default_factory=Vector2)
	maintain_distance: tuple[float, float] = (100, 200)
	aggressive: bool = False

I: Creature = Creature()

def get_position() -> Vector2:
	return I.position

def is_aggressive() -> bool:
	return I.aggressive and not player.is_god()

def is_invisible() -> bool:
	return I.invisible and not is_aggressive()

def update() -> None:
	if is_aggressive():
		target, _ = player.get_position()
		I.position.move_towards_ip(target, 10 * engine.get_delta())
		if (I.position - target).length() < KILL_DIST: game.die()
