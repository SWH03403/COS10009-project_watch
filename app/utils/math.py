from dataclasses import dataclass
from typing import Self
import pygame

# FIX: Divisions by 0

class Vec2(pygame.Vector2):
	@property
	def x(self) -> float:
		return self[0]

	@x.setter
	def x(self, x: float) -> None:
		self[0] = x

	@property
	def y(self) -> float:
		return self[1]

	@y.setter
	def y(self, y: float) -> None:
		self[1] = y

@dataclass
class Line:
	a: float
	b: float
	c: float

	@staticmethod
	def from_point(p: Vec2, q: Vec2 = Vec2()) -> Self:
		a, b = q.y - p.y, p.x - q.x
		c = -(a * p.x + b * p.y)
		return Line(a, b, c)

	def get_x(self, y: float) -> float:
		return -(self.b * y + self.c) / self.a

	def get_y(self, x: float) -> float:
		return -(self.a * x + self.c) / self.b

	def intersect(self, other: Self) -> Vec2:
		det = self.a * other.b - other.a * self.b
		x = (self.b * other.c - other.b * self.c) / det
		y = (other.a * self.c - self.a * other.c) / det
		return Vec2(x, y)
