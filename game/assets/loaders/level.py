from os.path import exists
from pygame import Vector2
from game.world import Fog, Level, Plane, Sector, Spawn, Wall, default_fog
from game.world.sector import CEILING_COLOR, FLOOR_COLOR, Material, WALL_COLOR

def parse_spawn(args: list[str]) -> Spawn:
	sector = int(args[1])
	position = Vector2(float(args[2]), float(args[3]))
	angle = float(args[4]) if len(args) > 4 else 0
	return Spawn(sector=sector, position=position, angle=angle)

def parse_vertex(args: list[str]) -> list[Vector2]:
	vertexes = []
	xs = [float(num) for num in args[1].split(",")]
	ys = [float(num) for num in args[2].split(",")]
	for x in xs:
		for y in ys:
			vertexes.append(Vector2(x, y))
	return vertexes

def parse_plane(arg: str, default_color: str) -> Plane:
	if ":" not in arg:
		return Plane(height=float(arg), color=default_color)
	height, color = arg.split(":", 2)[:2]
	return Plane(height=float(height), color=None if color == "-" else color)

def parse_wall(data: tuple[str, str]) -> Wall:
	vertex, neighbor = data
	color = WALL_COLOR
	if ":" in vertex: vertex, color = vertex.split(":", 1)
	color = None if neighbor == "-" else color.split(":", 1)[0]
	neighbor = None if neighbor in ["-", "x"] else int(neighbor)
	return Wall(vertex=int(vertex), neighbor=neighbor, color=color)

def parse_fog(args: list[str]) -> Fog:
	raise NotImplementedError() # TODO:

def parse_sector(args: list[str]) -> Sector:
	floor = parse_plane(args[1], FLOOR_COLOR)
	material = Material.TILE
	floor_args = args[1].split(":", 2)
	if len(floor_args) > 2:
		material = Material[floor_args[2].upper()]

	ceiling = parse_plane(args[2], CEILING_COLOR)
	walls = [parse_wall(data) for data in zip(args[3].split(","), args[4].split(","))]
	fog = default_fog() if len(args) < 6 else parse_fog(args[5].split(","))
	return Sector(floor=floor, ceiling=ceiling, walls=walls, material=material, fog=fog)

def load(name: str) -> Level | None:
	spawns = []
	vertexes = []
	sectors = []

	path = f"assets/levels/{name}.txt"
	if not exists(path): return None
	with open(path, "r", encoding="utf-8") as file:
		for num, line in enumerate(file.readlines()):
			line = line.split("#", 1)[0].strip()
			if len(line) == 0: continue
			args = [w for w in line.split(" ") if len(w) > 0]
			match args[0]:
				case "s" | "spawn":
					spawns.append(parse_spawn(args))
				case "v" | "vertex":
					vertexes.extend(parse_vertex(args))
				case "r" | "room" | "sector":
					sectors.append(parse_sector(args))
				case cmd:
					raise RuntimeError(f"Unknown command {cmd} in level \"{name}\" on line {num + 1}")

	if len(spawns) == 0:
		raise RuntimeError("Level does not define a spawn point!")
	return Level(spawns=spawns, vertexes=vertexes, sectors=sectors)
