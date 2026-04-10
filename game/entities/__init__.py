from . import creature, player
from .player import Direction, MovementState

def update() -> None:
	player.update()
	creature.update() # react to player's actions
