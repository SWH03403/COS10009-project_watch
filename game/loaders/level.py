from pygame import Vector2
from game.world import Fog, Level, Sector, Spawn, default_fog

def parse_spawn(args: list[str]) -> Spawn:
	position = Vector2(float(args[1]), float(args[2]))
	sector = int(args[3])
	return Spawn(position=position, sector=sector)

def parse_vertex(args: list[str]) -> list[Vector2]:
	vertexes = []
	xs = [float(num) for num in args[1].split(",")]
	ys = [float(num) for num in args[2].split(",")]
	for x in xs:
		for y in ys:
			vertexes.append(Vector2(x, y))
	return vertexes

def parse_fog(args: list[str]) -> Fog:
	raise NotImplementedError() # TODO:

def parse_sector(args: list[str]) -> Sector:
	floor, ceiling = float(args[1]), float(args[2])
	vertexes = [int(num) for num in args[3].split(",")]
	connects = [None if num == "x" else int(num) for num in args[4].split(",")]
	fog = default_fog() if len(args) < 6 else parse_fog(args[5].split(","))
	return Sector(floor=floor, ceiling=ceiling, vertexes=vertexes, connects=connects, fog=fog)

def load(name: str) -> Level:
	spawns = []
	vertexes = []
	sectors = []

	with open(f"assets/levels/{name}.txt", "r", encoding="utf-8") as file:
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
