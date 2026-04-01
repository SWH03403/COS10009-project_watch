from game.world import Fog, Level, Sector, Spawn, default_fog
from game.utils.math import Vec2

def parse_spawn(args: list[str]) -> Spawn:
	position = Vec2(float(args[1]), float(args[2]))
	sector = int(args[3])
	return Spawn(position=position, sector=sector)

def parse_vertex(args: list[str]) -> list[Vec2]:
	vertexes = []
	xs = [float(num) for num in args[1].split(",")]
	ys = [float(num) for num in args[2].split(",")]
	for x in xs:
		for y in ys:
			vertexes.append(Vec2(x, y))
	return vertexes

def parse_sector(args: list[str]) -> Sector:
	floor, ceiling = float(args[1]), float(args[2])
	vertexes = [int(num) for num in args[3].split(",")]
	connects = [None if num == "x" else int(num) for num in args[4].split(",")]
	return Sector(floor=floor, ceiling=ceiling, vertexes=vertexes, connects=connects)

def load(name: str) -> Level:
	vertexes = []
	sectors = []
	spawn: Spawn | None = None
	fog: Fog | None = None

	with open(f"assets/levels/{name}.txt", "r", encoding="utf-8") as file:
		for line in file.readlines():
			args = line.strip().split(" ")
			match args[0]:
				case "spawn":
					spawn = parse_spawn(args)
				case "vertex":
					vertexes.extend(parse_vertex(args))
				case "sector":
					sectors.append(parse_sector(args))

	if spawn is None:
		raise Exception("Level does not define a spawn point!")
	fog = default_fog() if fog is None else fog
	return Level(spawn=spawn, vertexes=vertexes, sectors=sectors, fog=fog)
