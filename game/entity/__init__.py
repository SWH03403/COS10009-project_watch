from . import creature, player
from .player import Direction, MovementState

def init() -> None:
	creature.init()
	player.init()

def update() -> None:
	player.update()
	creature.update() # passive
