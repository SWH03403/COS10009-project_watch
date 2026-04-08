from . import creature, player
from .player import Direction, MovementState

def init() -> None:
	creature.init()
	player.init()
