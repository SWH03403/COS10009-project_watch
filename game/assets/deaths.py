from enum import Enum, auto
import sys
import pygame

class Cause(Enum):
	SYSTEM = auto()
	FALL = auto()
	CAUGHT = auto()

def kill_application(ignore_god: bool = False) -> None:
	from game.entities import player
	if player.is_god() and not ignore_god: return
	pygame.quit()
	sys.exit()

def execute(cause: Cause = Cause.SYSTEM) -> None:
	match cause:
		case Cause.SYSTEM:
			kill_application(True)
