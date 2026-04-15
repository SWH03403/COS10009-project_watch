from datetime import datetime
from pygame import Vector2
from game.world import Level, Plane, Sector, Spawn

def parse_spawn(spawn: Spawn) -> str:
	return f"spawn {spawn.sector} {spawn.position.x:.1f} {spawn.position.y:.1f} {spawn.angle:.1f}\n"

def parse_vertex(vertex: Vector2) -> str:
	return f"vertex {vertex.x:.1f} {vertex.y:.1f}\n"

def parse_color(color: str | None) -> str:
	return "-" if color is None else color

def parse_plane(plane: Plane) -> str:
	return f"{plane.height}:{parse_color(plane.color)}"

def parse_sector(sector: Sector) -> str:
	material = sector.material.name.lower()
	floor = parse_plane(sector.floor)
	ceiling = parse_plane(sector.ceiling)
	init = f"sector {floor}:{material} {ceiling}"

	walls = []
	for wall in sector.walls:
		if wall.color is None: neighbor = "-"
		elif wall.neighbor is None: neighbor = "x"
		else: neighbor = str(wall.neighbor)
		color = "" if wall.color is None else f":{wall.color}"
		walls.append((f"{wall.vertex}{color}", neighbor))
	vertexes, neighbors = zip(*walls)
	vertexes = ",".join(vertexes)
	neighbors = ",".join(neighbors)

	return f"{init} {vertexes} {neighbors}\n"

def save(name: str, level: Level) -> str:
	path = f"assets/levels/{name}.txt"
	header = f"# created in \"watch\" v0.1.0\n# on: {datetime.now()}\n\n"
	with open(path, "w", encoding="utf-8") as file:
		file.write(header)
		for spawn in level.spawns:
			file.write(parse_spawn(spawn))
		file.write("\n")
		for vertex in level.vertexes:
			file.write(parse_vertex(vertex))
		file.write("\n")
		for sector in level.sectors:
			file.write(parse_sector(sector))
	return path
