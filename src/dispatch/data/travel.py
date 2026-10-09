"""Travel-time model: straight-line distance × detour factor ÷ average speed (config.travel)."""
from __future__ import annotations

import numpy as np

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km. Works on scalars or numpy arrays (broadcasting)."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def travel_hours(lat1, lon1, lat2, lon2, cfg) -> np.ndarray | float:
    """τ(a, b) in hours."""
    return haversine_km(lat1, lon1, lat2, lon2) * cfg.travel.detour_factor / cfg.travel.speed_kmh


def travel_matrix(origins: np.ndarray, destinations: np.ndarray, cfg) -> np.ndarray:
    """origins (n, 2) and destinations (m, 2) as [lat, lon] -> (n, m) matrix of hours."""
    return travel_hours(origins[:, None, 0], origins[:, None, 1],
                        destinations[None, :, 0], destinations[None, :, 1], cfg)
