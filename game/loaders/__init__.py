import os
import pygame
from pygame import Sound, Surface
from .level import load as load_level

def load_image(path: str, alpha: bool) -> Surface:
	image = pygame.image.load(f"assets/images/{path}.png")
	return image.convert_alpha() if alpha else image.convert()

def load_skybox(name: str) -> Surface:
	return load_image(f"skybox/{name}", False)

def load_music(name: str) -> None:
	pygame.mixer.music.load(f"assets/music/{name}.mp3")

def load_sound(path: str) -> Sound:
	return Sound(f"assets/sounds/{path}.wav")

def load_sounds_suffix(name: str) -> list[Sound]:
	sounds = []
	n = 1
	while True:
		path = f"assets/sounds/{name}{n}.wav"
		if not os.path.exists(path): return sounds
		sounds.append(Sound(path))
		n += 1
