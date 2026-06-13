from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from mars_ml_pipeline.config import load_settings, load_thresholds
from mars_ml_pipeline.event_bus import HttpEventPublisher, NoopPublisher
from mars_ml_pipeline.features import (
    TRACK_FEATURE_ORDER,
    WEATHER_FEATURE_ORDER,
    build_track_features,
    build_weather_features,
)
from mars_ml_pipeline.models.rule_based import RuleBasedTrackRiskModel, RuleBasedWeatherRiskModel
from mars_ml_pipeline.models.sklearn_adapter import SklearnRiskModel
from mars_ml_pipeline.recommendations import classify_score
from mars_ml_pipeline.schemas import (
    ExplanationItem,
    PublishedEvent,
    RiskPrediction,
    SecurityAnomalyRequest,
    SecurityPrediction,
    TrackRiskRequest,
    WeatherRiskRequest,
)
from mars_ml_pipeline.services.security import AnnotationSecurityDetector


REQUEST_COUNT = Counter(
    "mars_ml_requests_total",
    "Total MARS ML inference requests",
    ["endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "mars_ml_request_latency_seconds",
    "MARS ML inference request latency",
    ["endpoint"],
)


def create_app() -> FastAPI:
    settings = load_settings()
    thresholds = load_thresholds(settings.thresholds_path)

    track_model = (
        SklearnRiskModel(settings.track_model_path, TRACK_FEATURE_ORDER, "track-risk-sklearn")
        if settings.track_model_path
        else RuleBasedTrackRiskModel()
    )
    weather_model = (
        SklearnRiskModel(settings.weather_model_path, WEATHER_FEATURE_ORDER, "weather-risk-sklearn")
        if settings.weather_model_path
        else RuleBasedWeatherRiskModel()
    )
    security_detector = AnnotationSecurityDetector()
    publisher = (
        HttpEventPublisher(settings.event_bus_url)
        if settings.enable_event_publish and settings.event_bus_url
        else NoopPublisher()
    )

    app = FastAPI(
        title="MARS ML Inference",
        version="0.1.0",
        description="Risk and anomaly model endpoints for MARS agents.",
    )

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "track_model_version": track_model.model_version,
            "weather_model_version": weather_model.model_version,
            "security_model_version": security_detector.model_version,
        }

    @app.get("/metrics")
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.post("/track-risk/predict", response_model=RiskPrediction)
    def predict_track_risk(request: TrackRiskRequest) -> RiskPrediction:
        started = time.perf_counter()
        try:
            features = build_track_features(
                [event.model_dump() for event in request.events],
                request.segment.model_dump(),
            )
            score = track_model.predict_score(features)
            decision = classify_score(score, thresholds.track.caution, thresholds.track.high_risk)
            response = RiskPrediction(
                segment_id=request.segment.segment_id,
                risk_score=score,
                risk_class=decision.risk_class,
                severity=decision.severity,
                recommended_action=decision.recommended_action,
                explanation=_track_explanation(features),
                model_version=track_model.model_version,
            )
            _publish("track_risk.predicted", response.model_dump(mode="json"))
            REQUEST_COUNT.labels("/track-risk/predict", "success").inc()
            return response
        except Exception as exc:
            REQUEST_COUNT.labels("/track-risk/predict", "error").inc()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        finally:
            REQUEST_LATENCY.labels("/track-risk/predict").observe(time.perf_counter() - started)

    @app.post("/weather-risk/predict", response_model=RiskPrediction)
    def predict_weather_risk(request: WeatherRiskRequest) -> RiskPrediction:
        started = time.perf_counter()
        try:
            track_features = build_track_features(
                [event.model_dump() for event in request.sensor_events],
                request.segment.model_dump(),
            )
            features = build_weather_features(track_features, request.weather.model_dump())
            score = weather_model.predict_score(features)
            decision = classify_score(score, thresholds.weather.caution, thresholds.weather.high_risk)
            response = RiskPrediction(
                segment_id=request.segment.segment_id,
                risk_score=score,
                risk_class=decision.risk_class,
                severity=decision.severity,
                recommended_action=decision.recommended_action,
                explanation=_weather_explanation(features),
                model_version=weather_model.model_version,
            )
            _publish("weather_risk.predicted", response.model_dump(mode="json"))
            REQUEST_COUNT.labels("/weather-risk/predict", "success").inc()
            return response
        except Exception as exc:
            REQUEST_COUNT.labels("/weather-risk/predict", "error").inc()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        finally:
            REQUEST_LATENCY.labels("/weather-risk/predict").observe(time.perf_counter() - started)

    @app.post("/security-anomaly/predict", response_model=SecurityPrediction)
    def predict_security_anomaly(request: SecurityAnomalyRequest) -> SecurityPrediction:
        started = time.perf_counter()
        try:
            response = security_detector.predict(
                request,
                thresholds.security.caution,
                thresholds.security.high_risk,
            )
            _publish("security_anomaly.predicted", response.model_dump(mode="json"))
            REQUEST_COUNT.labels("/security-anomaly/predict", "success").inc()
            return response
        except Exception as exc:
            REQUEST_COUNT.labels("/security-anomaly/predict", "error").inc()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        finally:
            REQUEST_LATENCY.labels("/security-anomaly/predict").observe(time.perf_counter() - started)

    def _publish(event_type: str, payload: dict) -> None:
        publisher.publish(
            PublishedEvent(
                event_type=event_type,
                timestamp=datetime.now(timezone.utc),
                payload=payload,
            )
        )

    return app


def _track_explanation(features: dict[str, float]) -> list[ExplanationItem]:
    items: list[ExplanationItem] = []
    if features["speed_max"] > features["max_permitted_speed"]:
        items.append(
            ExplanationItem(
                feature="speed_max",
                value=round(features["speed_max"], 2),
                reason="speed exceeds segment limit",
            )
        )
    if features["vibration_vertical_mean"] >= 0.7:
        items.append(
            ExplanationItem(
                feature="vibration_vertical_mean",
                value=round(features["vibration_vertical_mean"], 3),
                reason="elevated vertical vibration",
            )
        )
    if features["maintenance_score"] <= 0.45:
        items.append(
            ExplanationItem(
                feature="maintenance_score",
                value=round(features["maintenance_score"], 3),
                reason="low maintenance health score",
            )
        )
    return items


def _weather_explanation(features: dict[str, float]) -> list[ExplanationItem]:
    items = _track_explanation(features)
    if features["rainfall_mm"] >= 40:
        items.append(
            ExplanationItem(
                feature="rainfall_mm",
                value=round(features["rainfall_mm"], 2),
                reason="heavy rainfall increases track risk",
            )
        )
    if features["visibility_m"] <= 800:
        items.append(
            ExplanationItem(
                feature="visibility_m",
                value=round(features["visibility_m"], 2),
                reason="low visibility affects operations",
            )
        )
    if features["flood_flag"]:
        items.append(ExplanationItem(feature="flood_flag", value=1, reason="flood hazard active"))
    return items


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("mars_ml_pipeline.services.app:create_app", factory=True, host="0.0.0.0", port=8000)
