# Haversine formula for calculating distances on a sphere, in this case earth

import math

EARTH_RADIUS_KM = 6371.0088   # IUGG mean radius

def calc_dist(lat1, lon1, lat2, lon2, radius=EARTH_RADIUS_KM):
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return radius * 2 * math.asin(math.sqrt(h))
