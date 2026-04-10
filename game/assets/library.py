from dataclasses import dataclass
from enum import Enum
import random
from pygame import Sound as SoundFile, Surface
from . import loaders

class Image(Enum):
	CREATURE_FLOAT = "creature/float"
	CREATURE_GRAB = "creature/grab"
	SKYBOX_CLOUDY = "skybox/cloudy"
	WINDOW_ICON = "icon"
	VIGNETTE = "vignette"

class Sound(Enum):
	AMBIENT_WINDY = "windy"
	DEATH_CAUGHT = "death/caught"
	DEATH_FALL = "death/fall"
	STEP_CONCRETE = "footsteps/concrete"
	STEP_METAL = "footsteps/metal"
	STEP_TILE = "footsteps/tile"
	STEP_WOOD = "footsteps/wood"
	STEP_WOOD_PANEL = "footsteps/woodpanel"

@dataclass
class Library:
	images: dict[Image, list[Surface]]
	sounds: dict[Sound, list[SoundFile]]

I: Library

def init() -> None:
	global I
	I = Library(images={}, sounds={})

def get_images(image: Image) -> list[Surface]:
	if image in I.images: return
	I.images[image] = loaders.images(image.value)
	assert len(I.images[image]) > 0
	return I.images[image]

def get_image(image: Image) -> Surface:
	return random.choice(get_images(image))

def get_sounds(sound: Sound) -> list[SoundFile]:
	if sound in I.sounds: return
	I.sounds[sound] = loaders.sounds(sound.value)
	assert len(I.sounds[sound]) > 0
	return I.sounds[sound]

def play_sound(sound: Sound, forever: bool = False) -> None:
	loops = -1 if forever else 0
	random.choice(get_sounds(sound)).play(loops)

def stop_sound(sound: Sound) -> None:
	for variant in get_sounds(sound):
		variant.stop()
