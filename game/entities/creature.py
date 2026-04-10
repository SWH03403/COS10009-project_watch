from dataclasses import dataclass
from pygame import Vector2

import game
from game import engine
from . import player

KILL_DIST: float = 5

@dataclass
class Creature:
	invisible: bool # whether it can be seen by the player
	position: Vector2
	maintain_distance: tuple[float, float]
	aggressive: bool

I: Creature

def init() -> None:
	global I
	I = Creature(
		invisible=False,
		position=Vector2(100, 100),
		maintain_distance=(100, 200),
		aggressive=False,
	)

def get_position() -> Vector2:
	return I.position

def is_invisible() -> bool:
	return I.invisible

def is_aggressive() -> bool:
	return I.aggressive

def update() -> None:
	if is_aggressive():
		target, _ = player.get_position()
		I.position.move_towards_ip(target, 10 * engine.get_delta())
		if (I.position - target).length() < KILL_DIST: game.die()
