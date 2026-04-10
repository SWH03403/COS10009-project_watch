from . import creature, region, sky, text, ui, vignette, world

def init() -> None:
	region.init()

	creature.init()
	sky.init()
	text.init()
	ui.init()
	vignette.init()
	world.init()

def perform() -> None:
	sky.render()
	world.render()
	ui.render()
	creature.render()
	vignette.render()
	text.render()
