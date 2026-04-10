from . import creature, player

def update() -> None:
	player.update()
	creature.update() # react to player's actions
