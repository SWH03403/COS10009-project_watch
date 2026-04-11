from . import deaths, library
from .deaths import Cause
from .library import Image, Sound

def init() -> None:
	library.init() # must loads first
	deaths.init()
