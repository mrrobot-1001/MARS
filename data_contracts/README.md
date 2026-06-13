# Data Contracts

MARS model services consume normalized events. Keep raw source-specific payloads outside model endpoints and transform them into these contracts during ingestion.

## Canonical Events

- `sensor_event`: timestamped train and track telemetry for one segment.
- `weather_event`: timestamped regional weather readings mapped to a segment or region.
- `video_event`: one frame or clip reference plus optional annotations.

The executable source of truth is `mars_ml_pipeline.schemas`. Generate OpenAPI contracts by running the FastAPI service and visiting `/docs`.
