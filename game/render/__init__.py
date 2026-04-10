from . import creature, region, sky, text, ui, world

def init() -> None:
	region.init()

	creature.init()
	sky.init()
	ui.init()
	text.init()
	world.init()

def perform() -> None:
	sky.render()
	world.render()
	ui.render()
	creature.render()
	text.render()
