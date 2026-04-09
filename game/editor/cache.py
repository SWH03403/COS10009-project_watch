from collections import defaultdict
from dataclasses import dataclass

import game
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
	walls_expired: bool = True

I: Cache

def init() -> None:
	global I
	I = Cache(walls=defaultdict(list))

def lazy_cache_walls() -> None:
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

def get_walls() -> WallCache:
	lazy_cache_walls()
	return I.walls

def get_sectors(left: int, right: int) -> list[SectorRef]:
	lazy_cache_walls()
	if (left, right) in I.walls: return I.walls[left, right]
	return I.wallss[right, left]

def expire_walls() -> None:
	I.walls_expired = True
