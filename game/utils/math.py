from dataclasses import dataclass
from typing import Self
from pygame import Vector2

# NOTE: everything is flipped vertically, so this is actually checking for anticlockwise instead
def is_polygon_clockwise(points: list[Vector2]) -> bool:
	n = len(points)
	if n < 3: return False
	for i in range(n):
		a, b, c = points[i - 2], points[i - 1], points[i]
		if (a - b).cross(a - c) > 0: return False
	return True

def is_facing(left: Vector2, right: Vector2, target: Vector2) -> bool:
	return (target - left).cross(target - right) < 0

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
