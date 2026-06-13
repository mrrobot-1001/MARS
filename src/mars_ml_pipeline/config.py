from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


DEFAULT_THRESHOLDS_PATH = Path("configs/risk_thresholds.yaml")


@dataclass(frozen=True)
class SeverityThresholds:
    caution: float
    high_risk: float


@dataclass(frozen=True)
class RiskThresholdConfig:
    track: SeverityThresholds
    weather: SeverityThresholds
    security: SeverityThresholds
    actions: Mapping[str, str]


@dataclass(frozen=True)
class ServiceSettings:
    track_model_path: str | None
    weather_model_path: str | None
    thresholds_path: Path
    event_bus_url: str | None
    enable_event_publish: bool


def load_settings() -> ServiceSettings:
    return ServiceSettings(
        track_model_path=os.getenv("MARS_TRACK_MODEL_PATH"),
        weather_model_path=os.getenv("MARS_WEATHER_MODEL_PATH"),
        thresholds_path=Path(os.getenv("MARS_THRESHOLDS_PATH", str(DEFAULT_THRESHOLDS_PATH))),
        event_bus_url=os.getenv("MARS_EVENT_BUS_URL"),
        enable_event_publish=os.getenv("MARS_ENABLE_EVENT_PUBLISH", "false").lower() == "true",
    )


def load_thresholds(path: Path | str = DEFAULT_THRESHOLDS_PATH) -> RiskThresholdConfig:
    payload = _read_yaml(Path(path))
    return RiskThresholdConfig(
        track=_thresholds(payload["track"]),
        weather=_thresholds(payload["weather"]),
        security=_thresholds(payload["security"]),
        actions=dict(payload.get("actions", {})),
    )


def _read_yaml(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, Mapping):
        raise ValueError(f"YAML config must be a mapping: {path}")
    return loaded


def _thresholds(payload: Mapping[str, Any]) -> SeverityThresholds:
    caution = float(payload["caution"])
    high_risk = float(payload["high_risk"])
    if not 0 <= caution <= high_risk <= 1:
        raise ValueError("thresholds must satisfy 0 <= caution <= high_risk <= 1")
    return SeverityThresholds(caution=caution, high_risk=high_risk)
