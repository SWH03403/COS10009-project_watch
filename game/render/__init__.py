from . import creature, overlay, region, sky, text, ui, world

def init() -> None:
	region.init()

	creature.init()
	overlay.init()
	sky.init()
	text.init()
	ui.init()
	world.init()

def perform() -> None:
	sky.render()
	world.render()
	creature.render()
	overlay.render()
	ui.render()
	text.render()
