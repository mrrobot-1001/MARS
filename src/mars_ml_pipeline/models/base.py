from __future__ import annotations

from typing import Protocol


class RiskModel(Protocol):
    model_version: str

    def predict_score(self, features: dict[str, float]) -> float:
        """Return a calibrated risk score in [0, 1]."""
