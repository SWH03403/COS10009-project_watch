from dataclasses import dataclass
from typing import Self
from pygame import Vector2

# FIX: Divisions by 0

@dataclass
class Line:
	a: float
	b: float
	c: float

	@staticmethod
	def from_point(p: Vector2, q: Vector2 = Vector2()) -> Self:
		a, b = q[1] - p[1], p[0] - q[0]
		c = -(a * p[0] + b * p[1])
		return Line(a, b, c)

	def get_x(self, y: float) -> float:
		return -(self.b * y + self.c) / self.a

	def get_y(self, x: float) -> float:
		return -(self.a * x + self.c) / self.b

	def intersect(self, other: Self) -> Vector2:
		det = self.a * other.b - other.a * self.b
		x = (self.b * other.c - other.b * self.c) / det
		y = (other.a * self.c - self.a * other.c) / det
		return Vector2(x, y)

	def validate(self, p: Vector2) -> float: # DEBUG:
		return self.a * p[0] + self.b * p[1] + self.c
