from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mars_ml_pipeline.artifact import write_deployment_card
from mars_ml_pipeline.features import ENGINE_FEATURE_ORDER
from mars_ml_pipeline.training.common import file_sha256


def main() -> None:
    parser = argparse.ArgumentParser(description="Train MARS Engine Risk model.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--model-version", default="0.1.0")
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    # The dataset features are: 'Engine rpm', 'Lub oil pressure', 'Fuel pressure', 'Coolant pressure', 'lub oil temp', 'Coolant temp'
    # Target: 'Engine Condition' (1=Good, 0=Faulty). We want risk, so we flip it: 1=Faulty, 0=Good
    X = frame[ENGINE_FEATURE_ORDER]
    y = 1 - frame["Engine Condition"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            ("classifier", GradientBoostingClassifier(random_state=42)),
        ]
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision_macro": float(precision_score(y_test, predictions, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_test, predictions, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_test, predictions, average="macro", zero_division=0)),
    }

    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = args.artifact_dir / "mars-engine-risk.joblib"
    joblib.dump(model, artifact_path)
    write_deployment_card(
        artifact_dir=args.artifact_dir,
        model_name="mars-engine-risk",
        model_version=args.model_version,
        artifact_path=artifact_path,
        training_data_snapshot=file_sha256(args.input),
        metrics=metrics,
        feature_order=ENGINE_FEATURE_ORDER,
        expected_inputs={"schema": "EngineRiskRequest"},
        expected_outputs={"schema": "RiskPrediction"},
    )
    print(metrics)
    print(f"wrote {artifact_path}")


if __name__ == "__main__":
    main()
