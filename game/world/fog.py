from dataclasses import dataclass

@dataclass
class Fog:
	color: str
	near: float
	far: float
	intensity: float

def default_fog() -> Fog:
	return Fog(color="gray10", near=1, far=100, intensity=1)
