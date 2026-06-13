from __future__ import annotations

from collections.abc import Iterable, Mapping
from statistics import mean, pstdev
from typing import Any


TRACK_FEATURE_ORDER = [
    "speed_mean",
    "speed_std",
    "speed_max",
    "acceleration_abs_mean",
    "vibration_vertical_mean",
    "vibration_vertical_std",
    "vibration_lateral_mean",
    "vibration_lateral_std",
    "track_temperature_mean",
    "segment_age_years",
    "maintenance_score",
    "curvature_degree",
    "max_permitted_speed",
]

WEATHER_FEATURE_ORDER = [
    *TRACK_FEATURE_ORDER,
    "rainfall_mm",
    "visibility_m",
    "temperature_c",
    "wind_speed_kmph",
    "flood_flag",
    "fog_flag",
    "heat_flag",
]


def build_track_features(events: Iterable[Mapping[str, Any]], segment: Mapping[str, Any]) -> dict[str, float]:
    event_list = list(events)
    if not event_list:
        raise ValueError("at least one sensor event is required")

    speeds = _values(event_list, "speed")
    accelerations = [abs(value) for value in _values(event_list, "acceleration")]
    vertical = _values(event_list, "vibration_vertical")
    lateral = _values(event_list, "vibration_lateral")
    temperatures = _values(event_list, "track_temperature")

    return {
        "speed_mean": mean(speeds),
        "speed_std": _std(speeds),
        "speed_max": max(speeds),
        "acceleration_abs_mean": mean(accelerations),
        "vibration_vertical_mean": mean(vertical),
        "vibration_vertical_std": _std(vertical),
        "vibration_lateral_mean": mean(lateral),
        "vibration_lateral_std": _std(lateral),
        "track_temperature_mean": mean(temperatures),
        "segment_age_years": float(segment["age_years"]),
        "maintenance_score": float(segment["maintenance_score"]),
        "curvature_degree": float(segment["curvature_degree"]),
        "max_permitted_speed": float(segment["max_permitted_speed"]),
    }


def build_weather_features(
    track_features: Mapping[str, float],
    weather_event: Mapping[str, Any],
) -> dict[str, float]:
    features = dict(track_features)
    hazard_flags = set(weather_event.get("hazard_flags") or [])
    features.update(
        {
            "rainfall_mm": float(weather_event["rainfall_mm"]),
            "visibility_m": float(weather_event["visibility_m"]),
            "temperature_c": float(weather_event["temperature_c"]),
            "wind_speed_kmph": float(weather_event["wind_speed_kmph"]),
            "flood_flag": float("flood" in hazard_flags),
            "fog_flag": float("fog" in hazard_flags),
            "heat_flag": float("heat" in hazard_flags),
        }
    )
    return features


def vectorize(features: Mapping[str, float], order: list[str]) -> list[float]:
    return [float(features[name]) for name in order]


def _values(events: Iterable[Mapping[str, Any]], key: str) -> list[float]:
    values = [float(event[key]) for event in events]
    if not values:
        raise ValueError(f"missing values for {key}")
    return values


def _std(values: list[float]) -> float:
    return pstdev(values) if len(values) > 1 else 0.0
