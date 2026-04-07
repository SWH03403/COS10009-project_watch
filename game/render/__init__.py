from . import region, sky, ui, world

def init() -> None:
	region.init()
	sky.init()
	ui.init()
	world.init()

def update() -> None:
	sky.render()
	world.render()
	ui.render()
