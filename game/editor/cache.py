from collections import defaultdict
from dataclasses import dataclass

import game
from game.utils.math import is_polygon_clockwise
from game.world.sector import WallType, get_wall_type

@dataclass
class SectorRef:
	id: int
	wall_idx: int
	typ: WallType

type WallCache = dict[tuple[int, int], list[SectorRef]]

@dataclass
class Cache:
	walls: WallCache # for faster neighbor lookup
	sectors_convex: list[bool]

	walls_expired: bool = True
	sectors_convex_expired: bool = True

I: Cache

def init() -> None:
	global I
	I = Cache(walls=defaultdict(list), sectors_convex=[])

def _cache_walls() -> None:
	if not I.walls_expired: return
	I.walls_expired = False
	I.walls.clear()

	level = game.get_level()
	for sector_id, sector in enumerate(level.sectors):
		for wall_idx, wall in enumerate(sector.walls):
			left, right = wall.vertex, sector.walls[wall_idx - len(sector.walls) + 1].vertex
			# WARN: try not to share a single wall with >2 sectors
			if (left, right) in I.walls: continue

			ref = SectorRef(id=sector_id, wall_idx=wall_idx, typ=get_wall_type(wall))
			if (right, left) in I.walls: I.walls[right, left].append(ref)
			else: I.walls[left, right].append(ref)

def _cache_sectors_convex() -> None:
	if not I.sectors_convex_expired: return
	I.sectors_convex_expired = False
	I.sectors_convex.clear()

	level = game.get_level()
	for sector in level.sectors:
		points = [level.vertexes[wall.vertex] for wall in sector.walls]
		I.sectors_convex.append(is_polygon_clockwise(points))

def get_walls() -> WallCache:
	_cache_walls()
	return I.walls

def get_sectors(left: int, right: int) -> list[SectorRef]:
	_cache_walls()
	if (left, right) in I.walls: return I.walls[left, right]
	return I.wallss[right, left]

def is_sector_convex(sector: int) -> bool:
	_cache_sectors_convex()
	return I.sectors_convex[sector]

def expire_walls() -> None:
	I.walls_expired = True
