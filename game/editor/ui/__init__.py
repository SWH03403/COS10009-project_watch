from dataclasses import dataclass
from pygame.event import Event

from game import editor
from game.utils import TextRenderer
from .. import selection
from . import sector

SPACE: int = 10
CHECK: int = 30 # size of square checbox
CHECK_S: int = CHECK + SPACE

@dataclass
class UI:
	f_general: TextRenderer

I: UI

def init() -> None:
	global I
	I = UI(f_general=TextRenderer(20, "gray90"))

def get_text_renderer() -> TextRenderer:
	return I.f_general

def on_mouse_event(event: Event) -> bool:
	sel = editor.get_selection()
	if isinstance(sel, selection.Sector):
		return sector.on_mouse_event(sel.id, event)

def render() -> None:
	sel = editor.get_selection()
	if isinstance(sel, selection.Sector):
		sector.render(sel.id)
