from dataclasses import dataclass
from pygame.typing import ColorLike

@dataclass
class Fog:
	color: ColorLike
	near: float
	far: float
	intensity: float

def default() -> Fog:
	return Fog(color="gray10", near=1, far=200, intensity=1)
