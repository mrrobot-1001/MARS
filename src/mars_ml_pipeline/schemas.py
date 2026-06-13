from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


AssetType = Literal["track", "bridge", "tunnel", "platform", "yard"]
RiskSeverity = Literal["normal", "caution", "high_risk"]


class EngineEvent(BaseModel):
    engine_id: str
    timestamp: datetime
    engine_rpm: int
    lub_oil_pressure: float
    fuel_pressure: float
    coolant_pressure: float
    lub_oil_temp: float
    coolant_temp: float

class EngineRiskRequest(BaseModel):
    event: EngineEvent


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
