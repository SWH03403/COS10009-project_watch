from dataclasses import dataclass, field
from .stats import Position, Vitality

@dataclass
class Player:
	position: Position = field(default_factory=Position)
	aim: float = 0. # radian
	vitality: Vitality = field(default_factory=Vitality)
