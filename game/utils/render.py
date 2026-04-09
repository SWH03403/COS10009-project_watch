import pygame
from pygame import Color, Rect, Surface, Vector2, draw
from pygame.typing import ColorLike

TRANSPARENT: Color = Color(0, 0, 0, 0)

def polygon(
	surface: Surface,
	color: ColorLike,
	points: list[Vector2],
	alpha: int = 255,
	width: int = 0,
) -> None:
	min_x = max_x = points[0].x
	min_y = max_y = points[0].y
	for i in range(1, len(points)):
		x, y = points[i]
		min_x, max_x = min(min_x, x), max(max_x, x)
		min_y, max_y = min(min_y, y), max(max_y, y)

	origin = Vector2(min_x - width // 2, min_y - width // 2)
	points = [p - origin for p in points]

	size = max_x - min_x + width, max_y - min_y + width
	inner = Surface(size, pygame.BLEND_ALPHA_SDL2).convert_alpha()
	inner.fill(TRANSPARENT)
	inner.set_alpha(alpha)
	draw.polygon(inner, color, points, width)

	surface.blit(inner, origin)
