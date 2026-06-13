from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


class SklearnRiskModel:
    def __init__(self, artifact_path: str | Path, feature_order: list[str], model_version: str) -> None:
        self.artifact_path = Path(artifact_path)
        self.feature_order = feature_order
        self.model_version = model_version
        self.model = joblib.load(self.artifact_path)

    def predict_score(self, features: dict[str, float]) -> float:
        row = pd.DataFrame([{name: float(features[name]) for name in self.feature_order}])
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(row)[0]
            classes = list(getattr(self.model, "classes_", range(len(probabilities))))
            weighted = sum(float(cls) * float(prob) for cls, prob in zip(classes, probabilities))
            return max(0.0, min(1.0, weighted / 2.0))
        prediction = float(self.model.predict(row)[0])
        return max(0.0, min(1.0, prediction / 2.0))
