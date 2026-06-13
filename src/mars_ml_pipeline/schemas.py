from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


AssetType = Literal["track", "bridge", "tunnel", "platform", "yard"]
RiskSeverity = Literal["normal", "caution", "high_risk"]


class SegmentMetadata(BaseModel):
    segment_id: str
    line_id: str
    region: str
    asset_type: AssetType = "track"
    age_years: float = Field(ge=0, le=150)
    maintenance_score: float = Field(ge=0, le=1)
    curvature_degree: float = Field(ge=0, le=20)
    max_permitted_speed: float = Field(gt=0, le=250)


class SensorEvent(BaseModel):
    timestamp: datetime
    segment_id: str
    train_id: Optional[str] = None
    speed: float = Field(ge=0, le=250)
    acceleration: float = Field(ge=-10, le=10)
    vibration_vertical: float = Field(ge=0, le=10)
    vibration_lateral: float = Field(ge=0, le=10)
    track_temperature: float = Field(ge=-20, le=90)


class WeatherEvent(BaseModel):
    timestamp: datetime
    segment_id: Optional[str] = None
    region: str
    rainfall_mm: float = Field(ge=0, le=500)
    visibility_m: float = Field(ge=0, le=50000)
    temperature_c: float = Field(ge=-30, le=65)
    wind_speed_kmph: float = Field(ge=0, le=250)
    hazard_flags: list[str] = Field(default_factory=list)

    @field_validator("hazard_flags")
    @classmethod
    def normalize_flags(cls, flags: list[str]) -> list[str]:
        return sorted({flag.strip().lower() for flag in flags if flag.strip()})


class BoundingBox(BaseModel):
    x_min: float = Field(ge=0)
    y_min: float = Field(ge=0)
    x_max: float = Field(ge=0)
    y_max: float = Field(ge=0)

    @field_validator("x_max")
    @classmethod
    def x_bounds(cls, value: float, info: object) -> float:
        data = getattr(info, "data", {})
        if "x_min" in data and value <= data["x_min"]:
            raise ValueError("x_max must be greater than x_min")
        return value

    @field_validator("y_max")
    @classmethod
    def y_bounds(cls, value: float, info: object) -> float:
        data = getattr(info, "data", {})
        if "y_min" in data and value <= data["y_min"]:
            raise ValueError("y_max must be greater than y_min")
        return value


class VideoAnnotation(BaseModel):
    label: str
    bbox: BoundingBox
    confidence: float = Field(ge=0, le=1)


class VideoEvent(BaseModel):
    camera_id: str
    timestamp: datetime
    frame_path: Optional[str] = None
    frame_url: Optional[str] = None
    zone_polygon: list[tuple[float, float]] = Field(default_factory=list)
    annotations: list[VideoAnnotation] = Field(default_factory=list)


class TrackRiskRequest(BaseModel):
    segment: SegmentMetadata
    events: list[SensorEvent] = Field(min_length=1)


class WeatherRiskRequest(BaseModel):
    segment: SegmentMetadata
    sensor_events: list[SensorEvent] = Field(min_length=1)
    weather: WeatherEvent


class SecurityAnomalyRequest(BaseModel):
    event: VideoEvent


class ExplanationItem(BaseModel):
    feature: str
    value: Union[float, str]
    reason: str


class RiskPrediction(BaseModel):
    segment_id: str
    risk_score: float = Field(ge=0, le=1)
    risk_class: int = Field(ge=0, le=2)
    severity: RiskSeverity
    recommended_action: str
    explanation: list[ExplanationItem] = Field(default_factory=list)
    model_version: str


class SecurityDetection(BaseModel):
    anomaly_type: str
    bbox: Optional[BoundingBox] = None
    confidence: float = Field(ge=0, le=1)
    severity: RiskSeverity


class SecurityPrediction(BaseModel):
    camera_id: str
    detections: list[SecurityDetection]
    risk_score: float = Field(ge=0, le=1)
    risk_class: int = Field(ge=0, le=2)
    severity: RiskSeverity
    recommended_action: str
    model_version: str


class PublishedEvent(BaseModel):
    event_type: str
    source: str = "mars-ml-inference"
    timestamp: datetime
    payload: dict
