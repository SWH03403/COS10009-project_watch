from dataclasses import dataclass, field
from typing import Callable, TextIO
from pygame import Color
from app.utils.math import Vec2

def c(name: str) -> Callable[[], Color]:
	return lambda: Color(name)

@dataclass
class Skybox:
	...

@dataclass
class Fog:
	color: Color = field(default_factory=c("gray20"))
	near: float = 1.
	far: float = 400.
	intensity: float = .8

@dataclass
class Room:
	corners: list[Vec2]
	wall: Color = field(default_factory=c("bisque"))
	floor: Color = field(default_factory=c("burlywood4"))
	ceiling: Color = field(default_factory=c("bisque3"))
	fog: Fog = field(default_factory=Fog)

@dataclass
class RoomConnection:
	idx: int
	wall: int
	offset: float

@dataclass
class Door:
	width: float
	room_from: RoomConnection
	room_to: RoomConnection
	is_opened: bool = True
	is_locked: bool = False
	is_visible: bool = True

@dataclass
class Edge:
	room: int
	door: int

@dataclass
class Level:
	spawn: Vec2 = field(default_factory=Vec2)
	rooms: list[Room] = field(default_factory=list)
	doors: list[Door] = field(default_factory=list)
	_edges: dict[int, list[Edge]] = field(default_factory=dict)

	def _add_edge(self, r1: int, r2: int, door: int) -> None:
		if r1 not in self._edges: self._edges[r1] = []
		self._edges[r1].append(Edge(r2, door))

	def add_door(self, door: Door) -> None:
		idx = len(self.doors)
		self.doors.append(door)
		self._add_edge(door.room_from.idx, door.room_to.idx, idx)
		self._add_edge(door.room_to.idx, door.room_from.idx, idx)

	def get_doors(self, room_idx: int) -> list[Door]:
		doors = []
		for edge in self._edges[room_idx]:
			doors.append(self.doors[edge.door])
		return doors

@dataclass
class LevelLoader:
	name: str
	level: Level = field(default_factory=Level)
	_file: TextIO = field(init=False)

	def __del__(self) -> None:
		self._file.close()

	def _parse_spawn(self, args: list[str]) -> None:
		self.level.spawn = Vec2(float(args[0]), float(args[1]))

	def _parse_quad_room(self, args: list[str]) -> None:
		br, tl = float(args[0]), float(args[1])
		tr = Vec2()
		if len(args) < 3: # rectangular room
			tr = Vec2(br, tl)
		else:
			args = args[2].split(",")
			tr.x, tr.y = float(args[0]), float(args[1])
		corners = [Vec2(0., 0.), Vec2(0., tl), tr, Vec2(br, 0.)]
		room = Room(corners)
		self.level.rooms.append(room)

	def _parse_connection(self, word: str, first: bool) -> RoomConnection:
		args = word.split(",")
		room = len(self.level.rooms) - 1 if args[0] == "" else int(args[0])
		if first and args[0] == "": room -= 1
		if room < 0: room += len(self.level.rooms)
		wall, offset = int(args[1]), float(args[2])
		return RoomConnection(room, wall, offset)

	def _parse_door(self, args: list[str]) -> None:
		width = float(args[0])
		room_from = self._parse_connection(args[1], True)
		room_to = self._parse_connection(args[2], False)
		door = Door(width, room_from, room_to)
		self.level.add_door(door)

	def __post_init__(self) -> None:
		self._file = open(f"assets/levels/{self.name}.txt", "r", encoding="utf-8")
		for line in self._file.readlines():
			line = line.split("#")[0].strip()
			if len(line) == 0: continue
			args = line.split(" ")
			match args.pop(0):
				case "s":
					self._parse_spawn(args)
				case "r4":
					self._parse_quad_room(args)
				case "d":
					self._parse_door(args)

	def into_level(self) -> Level:
		return self.level
