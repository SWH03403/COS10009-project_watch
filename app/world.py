from dataclasses import dataclass, field
from typing import Callable, Self, TextIO
from pygame import Color
from pygame.math import Vector2

def c(name: str) -> Callable[[], Color]:
	return lambda: Color(name)

@dataclass
class Skybox:
	...

@dataclass
class Fog:
	color: Color = field(default_factory=c("black"))
	near: float = 100.
	far: float = 300.
	intensity: float = 1.

@dataclass
class Room:
	corners: list[Vector2]
	wall: Color = field(default_factory=c("red"))
	floor: Color = field(default_factory=c("navyblue"))
	ceiling: Color = field(default_factory=c("bisque3"))
	fog: Fog = field(default_factory=Fog)

@dataclass
class Door:
	closable: bool = False
	locked: bool = False

@dataclass
class Edge:
	room: int
	door: int

@dataclass
class Level:
	spawn: Vector2 = field(default_factory=Vector2)
	rooms: list[Room] = field(default_factory=list)
	doors: list[Door] = field(default_factory=list)
	_edges: dict[int, list[Edge]] = field(default_factory=dict)

@dataclass
class LevelLoader:
	name: str
	level: Level = field(default_factory=Level)
	_file: TextIO = field(init=False)

	def __del__(self) -> None:
		self._file.close()

	def _parse_spawn(self, args: list[str]) -> None:
		self.level.spawn = Vector2(float(args[0]), float(args[1]))

	def _parse_quad_room(self, args: list[str]) -> None:
		br, tl = float(args[0]), float(args[1])
		tr = Vector2()
		if len(args) < 3: # rectangular room
			tr = Vector2(br, tl)
		else:
			args = args[2].split(",")
			tr[0], tr[1] = float(args[0]), float(args[1])
		corners = [Vector2(0., 0.), Vector2(0., tl), tr, Vector2(br, 0.)]
		room = Room(corners)
		self.level.rooms.append(room)

	def __post_init__(self) -> None:
		self._file = open(f"assets/levels/{self.name}.txt", "r", encoding="utf-8")
		for line in self._file.readlines():
			args = line.strip().split(" ")
			match args.pop(0):
				case "s":
					self._parse_spawn(args)
				case "r4":
					self._parse_quad_room(args)

	def into_level(self) -> Level:
		return self.level
