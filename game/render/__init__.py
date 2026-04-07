from . import region, sky, world

def init() -> None:
	region.init()
	sky.init()
	world.init()

def update() -> None:
	sky.render()
	world.render()
