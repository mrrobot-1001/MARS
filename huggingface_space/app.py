"""
MARS — Railway Risk & Anomaly Detection
========================================
Gradio app for real-time railway track risk prediction.
Supports two modes:
  1. Track Risk  — sensor-only assessment (13 features)
  2. Weather-Track Fusion — sensor + weather assessment (20 features)

Models are sklearn Pipeline objects (.joblib). If they are unavailable,
the app falls back to deterministic rule-based scoring that mirrors the
project's RuleBasedTrackRiskModel / RuleBasedWeatherRiskModel.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import gradio as gr
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("mars")

# ---------------------------------------------------------------------------
# Feature ordering (must match training pipeline exactly)
# ---------------------------------------------------------------------------
TRACK_FEATURE_ORDER: list[str] = [
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

WEATHER_FEATURE_ORDER: list[str] = [
    *TRACK_FEATURE_ORDER,
    "rainfall_mm",
    "visibility_m",
    "temperature_c",
    "wind_speed_kmph",
    "flood_flag",
    "fog_flag",
    "heat_flag",
]

# ---------------------------------------------------------------------------
# Model loading (graceful fallback)
# ---------------------------------------------------------------------------
MODEL_DIR = Path(__file__).resolve().parent


def _load_model(filename: str):
    """Attempt to load a joblib model; return *None* on failure."""
    path = MODEL_DIR / filename
    if not path.exists():
        logger.warning("Model file not found: %s — using rule-based fallback", path)
        return None
    try:
        import joblib

        model = joblib.load(path)
        logger.info("Loaded model: %s", path.name)
        return model
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load %s: %s — using rule-based fallback", path.name, exc)
        return None


track_model = _load_model("mars-track-risk.joblib")
weather_model = _load_model("mars-weather-risk.joblib")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """Clamp *value* to [lower, upper]."""
    return max(lower, min(upper, float(value)))


# ---------------------------------------------------------------------------
# Rule-based fallback models
# ---------------------------------------------------------------------------


def rule_based_track_score(f: dict[str, float]) -> float:
    """Deterministic track-risk scoring (mirrors RuleBasedTrackRiskModel)."""
    speed_ratio = _clamp(f["speed_max"] / max(f["max_permitted_speed"], 1.0))
    vibration = _clamp(f["vibration_vertical_mean"] * 0.55 + f["vibration_lateral_mean"] * 0.45)
    age = _clamp(f["segment_age_years"] / 60.0)
    maintenance_risk = 1.0 - _clamp(f["maintenance_score"])
    heat = _clamp((f["track_temperature_mean"] - 35.0) / 35.0)
    curve = _clamp(f["curvature_degree"] / 8.0)
    return _clamp(
        speed_ratio * 0.18
        + vibration * 0.30
        + age * 0.15
        + maintenance_risk * 0.22
        + heat * 0.08
        + curve * 0.07
    )


def rule_based_weather_score(f: dict[str, float]) -> float:
    """Deterministic weather-track fusion scoring (mirrors RuleBasedWeatherRiskModel)."""
    track_base = rule_based_track_score(f)
    rainfall = _clamp(f["rainfall_mm"] / 120.0)
    low_vis = _clamp((1200.0 - f["visibility_m"]) / 1200.0)
    wind = _clamp(f["wind_speed_kmph"] / 120.0)
    heat = _clamp((f["temperature_c"] - 38.0) / 18.0)
    flags = _clamp((f["flood_flag"] + f["fog_flag"] + f["heat_flag"]) / 2.0)
    return _clamp(
        track_base * 0.42
        + rainfall * 0.22
        + low_vis * 0.14
        + wind * 0.08
        + heat * 0.06
        + flags * 0.08
    )


# ---------------------------------------------------------------------------
# ML-based scoring
# ---------------------------------------------------------------------------


def predict_score(model: Any, features_dict: dict[str, float], feature_order: list[str]) -> float:
    """Run the sklearn pipeline and return a [0, 1] risk score."""
    row = pd.DataFrame([{name: float(features_dict[name]) for name in feature_order}])
    probabilities = model.predict_proba(row)[0]
    classes = list(model.classes_)
    weighted = sum(float(cls) * float(prob) for cls, prob in zip(classes, probabilities))
    return _clamp(weighted / 2.0)


# ---------------------------------------------------------------------------
# Severity classification
# ---------------------------------------------------------------------------


def classify_severity(score: float) -> tuple[str, int, str]:
    """Return (severity_label, risk_class, recommended_action)."""
    if score >= 0.68:
        return "🔴 HIGH RISK", 2, "Restrict Speed"
    if score >= 0.35:
        return "🟡 CAUTION", 1, "Caution Advisory"
    return "🟢 NORMAL", 0, "Normal Operations"


# ---------------------------------------------------------------------------
# Build the common track-feature dict from slider values
# ---------------------------------------------------------------------------


def _build_track_features(
    speed: float,
    acceleration: float,
    vib_vert: float,
    vib_lat: float,
    track_temp: float,
    age: float,
    maintenance: float,
    curvature: float,
    max_speed: float,
) -> dict[str, float]:
    """Map single-value slider inputs to the 13-feature vector."""
    return {
        "speed_mean": speed,
        "speed_std": 0.0,
        "speed_max": speed,
        "acceleration_abs_mean": abs(acceleration),
        "vibration_vertical_mean": vib_vert,
        "vibration_vertical_std": 0.0,
        "vibration_lateral_mean": vib_lat,
        "vibration_lateral_std": 0.0,
        "track_temperature_mean": track_temp,
        "segment_age_years": age,
        "maintenance_score": maintenance,
        "curvature_degree": curvature,
        "max_permitted_speed": max_speed,
    }


# ---------------------------------------------------------------------------
# Prediction callbacks
# ---------------------------------------------------------------------------


def predict_track(
    speed: float,
    acceleration: float,
    vib_vert: float,
    vib_lat: float,
    track_temp: float,
    age: float,
    maintenance: float,
    curvature: float,
    max_speed: float,
) -> tuple[float, str, int, str, str]:
    """Track-only risk prediction."""
    features = _build_track_features(
        speed, acceleration, vib_vert, vib_lat, track_temp, age, maintenance, curvature, max_speed
    )

    if track_model is not None:
        score = predict_score(track_model, features, TRACK_FEATURE_ORDER)
    else:
        score = rule_based_track_score(features)

    severity, risk_class, action = classify_severity(score)
    feature_json = json.dumps(features, indent=2)
    return round(score, 4), severity, risk_class, action, feature_json


def predict_weather(
    speed: float,
    acceleration: float,
    vib_vert: float,
    vib_lat: float,
    track_temp: float,
    age: float,
    maintenance: float,
    curvature: float,
    max_speed: float,
    rainfall: float,
    visibility: float,
    temperature: float,
    wind_speed: float,
    flood_flag: bool,
    fog_flag: bool,
    heat_flag: bool,
) -> tuple[float, str, int, str, str]:
    """Weather-track fusion risk prediction."""
    features = _build_track_features(
        speed, acceleration, vib_vert, vib_lat, track_temp, age, maintenance, curvature, max_speed
    )
    # Append weather features
    features.update(
        {
            "rainfall_mm": rainfall,
            "visibility_m": visibility,
            "temperature_c": temperature,
            "wind_speed_kmph": wind_speed,
            "flood_flag": float(flood_flag),
            "fog_flag": float(fog_flag),
            "heat_flag": float(heat_flag),
        }
    )

    if weather_model is not None:
        score = predict_score(weather_model, features, WEATHER_FEATURE_ORDER)
    else:
        score = rule_based_weather_score(features)

    severity, risk_class, action = classify_severity(score)
    feature_json = json.dumps(features, indent=2)
    return round(score, 4), severity, risk_class, action, feature_json


# ---------------------------------------------------------------------------
# Shared output components factory
# ---------------------------------------------------------------------------


def _output_components() -> list[gr.components.Component]:
    """Create the five output components used by both tabs."""
    return [
        gr.Number(label="Risk Score", precision=4),
        gr.Textbox(label="Severity Level"),
        gr.Number(label="Risk Class", precision=0),
        gr.Textbox(label="Recommended Action"),
        gr.JSON(label="Full Feature Vector"),
    ]


# ---------------------------------------------------------------------------
# Shared track-input sliders factory
# ---------------------------------------------------------------------------


def _track_sliders() -> list[gr.components.Component]:
    """Create the nine track-sensor sliders used by both tabs."""
    return [
        gr.Slider(0, 250, value=85, step=1, label="Speed (km/h)"),
        gr.Slider(-5, 5, value=0.2, step=0.1, label="Acceleration (m/s²)"),
        gr.Slider(0, 2, value=0.25, step=0.01, label="Vibration Vertical (g)"),
        gr.Slider(0, 2, value=0.18, step=0.01, label="Vibration Lateral (g)"),
        gr.Slider(-20, 80, value=32, step=1, label="Track Temperature (°C)"),
        gr.Slider(0, 70, value=15, step=1, label="Segment Age (years)"),
        gr.Slider(0, 1, value=0.75, step=0.01, label="Maintenance Score"),
        gr.Slider(0, 10, value=2, step=0.1, label="Curvature (degrees)"),
        gr.Slider(40, 250, value=110, step=10, label="Max Permitted Speed (km/h)"),
    ]


# ---------------------------------------------------------------------------
# Build Gradio UI
# ---------------------------------------------------------------------------

theme = gr.themes.Soft()

with gr.Blocks(theme=theme, title="MARS — Railway Risk Assessment") as demo:
    # ── Header ──────────────────────────────────────────────────────────
    gr.Markdown(
        """
        # 🚂 MARS — Railway Risk Assessment
        *AI-powered real-time risk prediction for railway track segments.
        Select a tab to assess track safety based on sensor data alone or
        combined with weather conditions.*
        """
    )

    model_status = []
    if track_model is None:
        model_status.append("Track model → **rule-based fallback**")
    else:
        model_status.append("Track model → **ML (loaded)**")
    if weather_model is None:
        model_status.append("Weather model → **rule-based fallback**")
    else:
        model_status.append("Weather model → **ML (loaded)**")
    gr.Markdown(f"*Model status: {' · '.join(model_status)}*")

    # ── Tabs ────────────────────────────────────────────────────────────
    with gr.Tabs():
        # ── Tab 1: Track Risk ───────────────────────────────────────────
        with gr.TabItem("🛤️ Track Risk Prediction"):
            gr.Markdown("### Assess risk using track sensor data only")
            with gr.Row():
                with gr.Column(scale=1):
                    track_inputs = _track_sliders()
                    track_btn = gr.Button("Predict Track Risk", variant="primary", size="lg")
                with gr.Column(scale=1):
                    track_outputs = _output_components()

            track_btn.click(fn=predict_track, inputs=track_inputs, outputs=track_outputs)

        # ── Tab 2: Weather-Track Fusion ─────────────────────────────────
        with gr.TabItem("🌦️ Weather-Track Fusion"):
            gr.Markdown("### Assess risk combining track sensors with weather conditions")
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### Track Sensors")
                    weather_track_inputs = _track_sliders()

                    gr.Markdown("#### Weather Conditions")
                    weather_extra_inputs = [
                        gr.Slider(0, 200, value=5, step=1, label="Rainfall (mm)"),
                        gr.Slider(50, 15000, value=5000, step=50, label="Visibility (m)"),
                        gr.Slider(-30, 60, value=28, step=1, label="Temperature (°C)"),
                        gr.Slider(0, 150, value=20, step=1, label="Wind Speed (km/h)"),
                        gr.Checkbox(label="Flood Warning", value=False),
                        gr.Checkbox(label="Fog Warning", value=False),
                        gr.Checkbox(label="Heat Warning", value=False),
                    ]
                    weather_btn = gr.Button(
                        "Predict Fusion Risk", variant="primary", size="lg"
                    )
                with gr.Column(scale=1):
                    weather_outputs = _output_components()

            weather_btn.click(
                fn=predict_weather,
                inputs=weather_track_inputs + weather_extra_inputs,
                outputs=weather_outputs,
            )

    # ── Footer ──────────────────────────────────────────────────────────
    gr.Markdown(
        """
        ---
        <center>
        Built with <b>MARS ML Pipeline</b> · Powered by scikit-learn & Gradio
        </center>
        """
    )

# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo.launch()
