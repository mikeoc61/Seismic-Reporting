"""Great-circle distance between two coordinates (Haversine formula)."""

from __future__ import annotations

import math

# IUGG mean radius of the Earth, in kilometres.
EARTH_RADIUS_KM: float = 6371.0088


def calc_dist(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    radius: float = EARTH_RADIUS_KM,
) -> float:
    """Return the great-circle distance between two points.

    Coordinates are decimal degrees; the result is in the same unit as
    ``radius`` (kilometres by default).
    """
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    h = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return radius * 2 * math.asin(math.sqrt(h))
