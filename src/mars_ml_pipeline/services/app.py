from __future__ import annotations

from collections.abc import Mapping
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST

from mars_ml_pipeline.config import load_settings, load_thresholds
from mars_ml_pipeline.event_bus import HttpEventPublisher, NoopPublisher
from mars_ml_pipeline.features import ENGINE_FEATURE_ORDER, build_engine_features
from mars_ml_pipeline.recommendations import classify_score
from mars_ml_pipeline.models.sklearn_adapter import SklearnRiskModel
from mars_ml_pipeline.schemas import (
    ExplanationItem,
    PublishedEvent,
    RiskPrediction,
    SecurityAnomalyRequest,
    SecurityPrediction,
    EngineRiskRequest,
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

    engine_model = SklearnRiskModel(
        settings.track_model_path.replace("track-risk", "engine-risk").replace("mars-track-risk", "mars-engine-risk") if settings.track_model_path else "artifacts/engine-risk/mars-engine-risk.joblib",
        ENGINE_FEATURE_ORDER,
        "engine-risk-sklearn"
    )

    security_detector = AnnotationSecurityDetector()
    publisher = (
        HttpEventPublisher(settings.event_bus_url)
        if settings.enable_event_publish and settings.event_bus_url
        else NoopPublisher()
    )

    app = FastAPI(
        title="MARS Engine Health Inference",
        version="0.1.0",
        description="Predictive maintenance endpoints for train engines.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "engine_model_version": engine_model.model_version,
            "security_model_version": security_detector.model_version,
        }

    @app.get("/metrics")
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.post("/engine-risk/predict", response_model=RiskPrediction)
    def predict_engine_risk(request: EngineRiskRequest) -> RiskPrediction:
        started = time.perf_counter()
        try:
            features = build_engine_features(request.event.model_dump())
            score = engine_model.predict_score(features)
            # Use track thresholds as generic thresholds for now
            decision = classify_score(score, thresholds.track.caution, thresholds.track.high_risk)
            response = RiskPrediction(
                segment_id=request.event.engine_id,
                risk_score=score,
                risk_class=decision.risk_class,
                severity=decision.severity,
                recommended_action=decision.recommended_action,
                explanation=_engine_explanation(features),
                model_version=engine_model.model_version,
            )
            _publish("engine_risk.predicted", response.model_dump(mode="json"))
            REQUEST_COUNT.labels("/engine-risk/predict", "success").inc()
            return response
        except Exception as exc:
            REQUEST_COUNT.labels("/engine-risk/predict", "error").inc()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        finally:
            REQUEST_LATENCY.labels("/engine-risk/predict").observe(time.perf_counter() - started)

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


def _engine_explanation(features: dict[str, float]) -> list[ExplanationItem]:
    items: list[ExplanationItem] = []
    if features.get("Coolant temp", 0) > 90:
        items.append(
            ExplanationItem(
                feature="Coolant temp",
                value=round(features["Coolant temp"], 2),
                reason="Coolant temperature is dangerously high",
            )
        )
    if features.get("Lub oil pressure", 10) < 2.0:
        items.append(
            ExplanationItem(
                feature="Lub oil pressure",
                value=round(features["Lub oil pressure"], 3),
                reason="Lubrication oil pressure is too low",
            )
        )
    return items


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("mars_ml_pipeline.services.app:create_app", factory=True, host="0.0.0.0", port=8000)
