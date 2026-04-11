from enum import Enum, auto
import sys
from time import sleep
import pygame

from . import library
from .library import Sound

class Cause(Enum):
	SYSTEM = auto()
	FALL = auto()
	CAUGHT = auto()

def kill_application(ignore_god: bool = False) -> None:
	from game.entities import player
	if player.is_god() and not ignore_god: return
	pygame.quit()
	sys.exit()

def flash(color: str, delay: float) -> None:
	from game import engine
	engine.get_screen().fill(color)
	engine.update()
	sleep(delay)

def execute(cause: Cause = Cause.SYSTEM) -> None:

	match cause:
		case Cause.SYSTEM:
			kill_application(True)
		case Cause.FALL:
			library.play_sound(Sound.DEATH_FALL)
			flash("red3", .1)
			flash("black", .4)
			kill_application()
