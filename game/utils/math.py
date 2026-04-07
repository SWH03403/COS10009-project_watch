from dataclasses import dataclass
from typing import Self
from pygame import Vector2

@dataclass
class Line:
	a: float
	b: float
	c: float

	@staticmethod
	def from_point(p: Vector2, q: Vector2 = Vector2()) -> Self:
		a, b = q.y - p.y, p.x - q.x
		c = -(a * p.x + b * p.y)
		return Line(a, b, c)

	def get_x(self, y: float) -> float:
		return -(self.b * y + self.c) / self.a

	def get_y(self, x: float) -> float:
		return -(self.a * x + self.c) / self.b

	def cross(self, p: Vector2) -> float:
		return self.a * p.x + self.b * p.y + self.c

	def intersect(self, other: Self) -> Vector2:
		det = self.a * other.b - other.a * self.b
		x = (self.b * other.c - other.b * self.c) / det
		y = (other.a * self.c - self.a * other.c) / det
		return Vector2(x, y)
