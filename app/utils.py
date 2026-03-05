def map_range(value: float, b1: float, e1: float, b2: float, e2: float) -> float:
	dist = (value - b1) / (e1 - b1)
	return b2 + (e2 - b2) * dist
