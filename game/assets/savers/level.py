from datetime import datetime
from os.path import exists
from pygame import Vector2
from game.world import Level, Plane, Sector, Spawn

def parse_spawn(spawn: Spawn) -> str:
	return f"spawn {spawn.sector} {spawn.position.x:.2f} {spawn.position.y:.2f} {spawn.angle:.2f}\n"

def parse_vertex(vertex: Vector2) -> str:
	return f"vertex {vertex.x:.2f} {vertex.y:.2f}\n"

def parse_color(color: str | None) -> str:
	return "-" if color is None else color

def parse_plane(plane: Plane) -> str:
	return f"{plane.height}:{parse_color(plane.color)}"

def parse_sector(sector: Sector) -> str:
	floor = parse_plane(sector.floor)
	ceiling = parse_plane(sector.ceiling)
	init = f"sector {floor} {ceiling}"

	walls = []
	for wall in sector.walls:
		if wall.color is None: neighbor = "-"
		elif wall.neighbor is None: neighbor = "x"
		else: neighbor = str(neighbor)
		walls.append((str(wall.vertex), neighbor))
	vertexes, neighbors = zip(*walls)
	vertexes = ",".join(vertexes)
	neighbors = ",".join(neighbor)

	return f"{init} {vertexes} {neighbors}\n"

def save(name: str, level: Level) -> str:
	path = f"assets/levels/{name}.txt"
	if exists(path):
		now = datetime.now().strftime("%y%m%d-%H%M%S")
		path = f"assets/levels/{name}-{now}.txt"
	if exists(path): raise RuntimeError("Both save paths exist")
	with open(path, "w", encoding="utf-8") as file:
		for spawn in level.spawns:
			file.write(parse_spawn(spawn))
		file.write("\n")
		for vertex in level.vertexes:
			file.write(parse_vertex(vertex))
		file.write("\n")
		for sector in level.sectors:
			file.write(parse_sector(sector))
	return path
