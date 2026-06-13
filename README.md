# MARS ML Pipeline - Risk & Anomaly Models

Production-oriented starter implementation for the MARS Phase 1 ML pipeline. It covers canonical data schemas, synthetic data generation, tabular model training, model artifact metadata, FastAPI inference endpoints, event-bus publishing hooks, observability, and containerization.

## What Is Included

- Canonical Pydantic schemas for `sensor_event`, `weather_event`, `video_event`, and model outputs.
- Synthetic CSV data generator for Track and Weather use cases.
- Training scripts for Track Risk and Weather-Track Fusion models using scikit-learn.
- FastAPI inference service with:
  - `POST /track-risk/predict`
  - `POST /weather-risk/predict`
  - `POST /security-anomaly/predict`
  - `GET /health`
  - `GET /metrics`
- Configurable thresholds in `configs/risk_thresholds.yaml`.
- Event bus abstraction with in-memory and HTTP publisher implementations.
- Deployment cards for model governance.
- Dockerfile and docker-compose skeleton.

## Repository Layout

```text
configs/                    Runtime configuration
data_contracts/             JSON schema examples and contract notes
notebooks/                  Colab workflow templates
scripts/                    Local developer commands
src/mars_ml_pipeline/       Pipeline, model, and service code
tests/                      Lightweight unit tests
```

## Quick Start

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generate local synthetic data:

```bash
python -m mars_ml_pipeline.data.generate_synthetic --output-dir data/generated --rows 5000
```

Train tabular models:

```bash
python -m mars_ml_pipeline.training.train_track_risk \
  --input data/generated/track_sensor_events.csv \
  --artifact-dir artifacts/track-risk/v0.1.0

python -m mars_ml_pipeline.training.train_weather_risk \
  --sensor-input data/generated/track_sensor_events.csv \
  --weather-input data/generated/weather_events.csv \
  --artifact-dir artifacts/weather-risk/v0.1.0
```

Run the inference service:

```bash
uvicorn mars_ml_pipeline.services.app:create_app --factory --reload --port 8000
```

Try a prediction:

```bash
curl -X POST http://localhost:8000/track-risk/predict \
  -H 'content-type: application/json' \
  -d '{
    "segment": {"segment_id": "SEG-001", "line_id": "L1", "region": "north", "asset_type": "track", "age_years": 18, "maintenance_score": 0.72, "curvature_degree": 1.8, "max_permitted_speed": 110},
    "events": [
      {"timestamp": "2026-06-13T08:00:00Z", "segment_id": "SEG-001", "train_id": "T-102", "speed": 92, "acceleration": 0.2, "vibration_vertical": 0.35, "vibration_lateral": 0.26, "track_temperature": 36}
    ]
  }'
```

## Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `MARS_TRACK_MODEL_PATH` | unset | Path to a trained Track Risk `.joblib` artifact. |
| `MARS_WEATHER_MODEL_PATH` | unset | Path to a trained Weather Risk `.joblib` artifact. |
| `MARS_THRESHOLDS_PATH` | `configs/risk_thresholds.yaml` | Severity threshold configuration. |
| `MARS_EVENT_BUS_URL` | unset | HTTP endpoint for publishing normalized risk events. |
| `MARS_ENABLE_EVENT_PUBLISH` | `false` | Enables event publishing when set to `true`. |

When model paths are not provided, the service uses deterministic rule-based fallback models. That keeps local demos and CI smoke tests useful before trained artifacts exist.

## Colab Workflow

The `notebooks/` directory contains notebook templates with the expected Colab flow: mount storage, load processed data, train/evaluate, export artifacts, and write deployment cards. They are intentionally lightweight so they can be copied into Colab and connected to your storage bucket.

## Production Notes

- Put raw data under `raw/sensors/`, `raw/weather/`, and `raw/video/`.
- Put derived tabular/image data under `processed/tabular/` and `processed/images/`.
- Version model artifacts by semantic model version and data snapshot hash.
- Deploy services behind the MARS API gateway. Do not expose model endpoints directly.
- Forward prediction logs and operator feedback into retraining datasets.
