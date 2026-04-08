import pygame
from pygame import Vector2

def unscale_mouse_position(p: Vector2) -> Vector2:
	screen = Vector2(pygame.display.get_surface().size)
	window = Vector2(pygame.display.get_window_size())
	return Vector2(p.x / window.x * screen.x, p.y / window.y * screen.y)
