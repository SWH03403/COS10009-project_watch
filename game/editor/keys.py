import pygame

import game
from .. import editor

def handle_keydown(key: int) -> None:
	match key:
		case pygame.K_q | pygame.K_ESCAPE:
			game.die()
		case pygame.K_LEFTBRACKET:
			game.set_editor(False)
