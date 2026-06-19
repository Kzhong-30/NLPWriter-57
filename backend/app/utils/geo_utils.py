from math import radians, sin, cos, sqrt, atan2
from typing import Optional
from geopy.distance import geodesic


def calculate_distance_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def calculate_distance_geopy(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers


def is_within_radius(user_lat, user_lon, target_lat, target_lon, radius_meters=100.0):
    if None in [user_lat, user_lon, target_lat, target_lon]:
        return False
    distance_km = calculate_distance_geopy(user_lat, user_lon, target_lat, target_lon)
    return (distance_km * 1000) <= radius_meters


def get_address_coordinates(address):
    try:
        from geopy.geocoders import Nominatim
        g = Nominatim(user_agent="volunteer_app")
        loc = g.geocode(address)
        return (loc.latitude, loc.longitude) if loc else None
    except Exception:
        return None
