import pygame
from pygame import Surface
from .level import load as load_level

def load_image(path: str, alpha: bool) -> Surface:
	image = pygame.image.load(f"assets/images/{path}.png")
	return image.convert_alpha() if alpha else image.convert()

def load_skybox(name: str) -> Surface:
	return load_image(f"skybox/{name}", False)

def load_music(name: str) -> None:
	pygame.mixer.music.load(f"assets/music/{name}.mp3")
