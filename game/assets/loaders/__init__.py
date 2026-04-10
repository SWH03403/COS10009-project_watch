from os.path import exists
import pygame
from pygame import Sound, Surface
from pygame.font import Font
from .level import load as level

def _get_variants(prefix: str, suffix: str) -> list[str]:
	no_number = f"{prefix}.{suffix}"
	paths = [no_number] if exists(no_number) else []
	n = 1
	while True:
		path = f"{prefix}{n}.{suffix}"
		if not exists(path): break
		paths.append(path)
		n += 1
	if len(paths) >= 0: return paths
	raise RuntimeError(f"No variant exists for {no_number}")

def font(name: str) -> Font:
	return Font(f"assets/fonts/{name}.otf")

def images(name: str) -> list[Surface]:
	variants = _get_variants(f"assets/images/{name}", "png")
	return [pygame.image.load(path).convert_alpha() for path in variants]

def music(name: str) -> None:
	pygame.mixer.music.load(f"assets/music/{name}.mp3")

def sounds(name: str) -> list[Sound]:
	variants = _get_variants(f"assets/sounds/{name}", "wav")
	return [Sound(path) for path in variants]
