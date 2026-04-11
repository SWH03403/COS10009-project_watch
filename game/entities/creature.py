from dataclasses import dataclass, field
from random import triangular
from time import monotonic
from pygame import Vector2

import game
from game import engine
from game.assets import Cause
from . import player

KILL_DIST: float = 5
MIN_WATCHED_DUR: float = 1
MAX_WATCHED_DUR: float = 2

INIT_PATIENCE: float = 300
PATIENCE_DECAY: float = 10
PATIENCE_DECAY_OBSESSED: float = 50 # being looked at for too long or player out of stamina
PATIENCE_GAIN: float = 50 # looked at for a "right" amount of time
AVOID_DISTANCE: float = 100 # min distant when patient
FOLLOW_DISTANCE: float = 200 # max distance when patient
SPEED_PATIENCE: float = 15

INIT_AGGRESSION: float = 500
AGGRESSION_DECAY: float = 40
AGGRESSION_DECAY_IGNORED: float = 10
SPEED_AGRESSIVE: float = 10
SPEED_PREDATOR: float = 30 # player ran out of stamina

# favors shorter duration
def get_invis_dur() -> float:
	return triangular(10, 60, 20)

@dataclass
class Creature:
	position: Vector2 = field(default_factory=Vector2)
	watched_since: float | None = None # when the eye staring contest starts
	# can only be seen after this time
	invis_until: float = field(default_factory=lambda: get_invis_dur() + monotonic())
	patience: float = INIT_PATIENCE
	gained_patience: bool = False

I: Creature = Creature()

def get_position() -> Vector2:
	return I.position

def is_aggressive() -> bool:
	return I.patience < 0 and not player.is_god()

def is_invisible() -> bool:
	return monotonic() < I.invis_until and not is_aggressive()

def is_watched() -> bool:
	return I.watched_since is not None

def set_watched(watched: bool) -> None:
	if watched and I.watched_since is None:
		I.watched_since = monotonic()
	elif not watched:
		I.watched_since = None

def update() -> None:
	player_pos, _ = player.get_position()
	to_player = player_pos - I.position
	dist = to_player.length()
	to_player.normalize_ip()
	delta = engine.get_delta()
	now = monotonic()

	if is_aggressive():
		I.position.move_towards_ip(player_pos, 10 * delta)
		if dist < KILL_DIST: game.die(Cause.CAUGHT)
		return

	speed = SPEED_PATIENCE * delta
	if dist < AVOID_DISTANCE: I.position -= to_player * speed
	elif dist > FOLLOW_DISTANCE: I.position += to_player * speed

	if is_invisible(): return
	decay_rate = PATIENCE_DECAY
	if I.watched_since is not None:
		watched_dur = now - I.watched_since # maintained eye contact duration
		decay_rate = 0 if watched_dur < MAX_WATCHED_DUR else PATIENCE_DECAY_OBSESSED
		if watched_dur > MIN_WATCHED_DUR and not I.gained_patience:
			I.patience += PATIENCE_GAIN
			I.gained_patience = True
	elif I.gained_patience:
		# TODO: maybe jump to a different angle to the player to randomize appearance spot
		I.invis_until = now + get_invis_dur()
		I.gained_patience = False
	I.patience -= decay_rate * delta

	if I.patience < 0: I.patience = -INIT_AGGRESSION
