from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mars_ml_pipeline.artifact import write_deployment_card
from mars_ml_pipeline.features import TRACK_FEATURE_ORDER
from mars_ml_pipeline.training.common import file_sha256


def main() -> None:
    parser = argparse.ArgumentParser(description="Train MARS Track Risk model.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--model-version", default="0.1.0")
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    feature_frame = _to_service_features(frame)
    X = feature_frame[TRACK_FEATURE_ORDER]
    y = frame["risk_label"].astype(int)
    groups = frame["segment_id"]

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups))

    model = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            ("classifier", GradientBoostingClassifier(random_state=42)),
        ]
    )
    model.fit(X.iloc[train_idx], y.iloc[train_idx])
    predictions = model.predict(X.iloc[test_idx])
    metrics = {
        "accuracy": float(accuracy_score(y.iloc[test_idx], predictions)),
        "precision_macro": float(precision_score(y.iloc[test_idx], predictions, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y.iloc[test_idx], predictions, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y.iloc[test_idx], predictions, average="macro", zero_division=0)),
    }

    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = args.artifact_dir / "mars-track-risk.joblib"
    joblib.dump(model, artifact_path)
    write_deployment_card(
        artifact_dir=args.artifact_dir,
        model_name="mars-track-risk",
        model_version=args.model_version,
        artifact_path=artifact_path,
        training_data_snapshot=file_sha256(args.input),
        metrics=metrics,
        feature_order=TRACK_FEATURE_ORDER,
        expected_inputs={"schema": "TrackRiskRequest"},
        expected_outputs={"schema": "RiskPrediction"},
    )
    print(metrics)
    print(f"wrote {artifact_path}")


def _to_service_features(frame: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=frame.index)
    features["speed_mean"] = frame["speed"]
    features["speed_std"] = 0.0
    features["speed_max"] = frame["speed"]
    features["acceleration_abs_mean"] = frame["acceleration"].abs()
    features["vibration_vertical_mean"] = frame["vibration_vertical"]
    features["vibration_vertical_std"] = 0.0
    features["vibration_lateral_mean"] = frame["vibration_lateral"]
    features["vibration_lateral_std"] = 0.0
    features["track_temperature_mean"] = frame["track_temperature"]
    features["segment_age_years"] = frame["age_years"]
    features["maintenance_score"] = frame["maintenance_score"]
    features["curvature_degree"] = frame["curvature_degree"]
    features["max_permitted_speed"] = frame["max_permitted_speed"]
    return features


if __name__ == "__main__":
    main()
