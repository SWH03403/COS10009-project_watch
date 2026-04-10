import os
import pygame
from pygame import Sound, Surface
from pygame.font import Font
from .level import load as level

def font(name: str) -> Font:
	return Font(f"assets/fonts/{name}.otf")

def image(name: str, alpha: bool) -> Surface:
	img = pygame.image.load(f"assets/images/{name}.png")
	return img.convert_alpha() if alpha else image.convert()

def skybox(name: str) -> Surface:
	return image(f"skybox/{name}", False)

def music(name: str) -> None:
	pygame.mixer.music.load(f"assets/music/{name}.mp3")

def sounds(name: str) -> list[Sound]:
	path = f"assets/sounds/{name}.wav"
	if os.path.exists(path): return [Sound(path)]
	variants = []
	n = 1
	while True:
		path = f"assets/sounds/{name}{n}.wav"
		if not os.path.exists(path): return variants
		variants.append(Sound(path))
		n += 1
