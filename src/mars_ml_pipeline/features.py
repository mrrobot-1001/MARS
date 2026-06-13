from __future__ import annotations

from collections.abc import Iterable, Mapping
from statistics import mean, pstdev
from typing import Any


ENGINE_FEATURE_ORDER: list[str] = [
    "Engine rpm",
    "Lub oil pressure",
    "Fuel pressure",
    "Coolant pressure",
    "lub oil temp",
    "Coolant temp",
]


def build_engine_features(event_dict: dict) -> dict[str, float]:
    """Convert an engine telemetry event into model features."""
    return {feature: float(event_dict.get(feature, 0.0)) for feature in ENGINE_FEATURE_ORDER}


def vectorize(features: Mapping[str, float], order: list[str]) -> list[float]:
    return [float(features[name]) for name in order]


def _values(events: Iterable[Mapping[str, Any]], key: str) -> list[float]:
    values = [float(event[key]) for event in events]
    if not values:
        raise ValueError(f"missing values for {key}")
    return values


def _std(values: list[float]) -> float:
    return pstdev(values) if len(values) > 1 else 0.0
