from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DeploymentCard:
    model_name: str
    model_version: str
    artifact_path: str
    training_data_snapshot: str
    metrics: dict[str, float]
    feature_order: list[str]
    created_at: str
    expected_inputs: dict[str, Any]
    expected_outputs: dict[str, Any]


def write_deployment_card(
    artifact_dir: Path,
    model_name: str,
    model_version: str,
    artifact_path: Path,
    training_data_snapshot: str,
    metrics: dict[str, float],
    feature_order: list[str],
    expected_inputs: dict[str, Any],
    expected_outputs: dict[str, Any],
) -> Path:
    card = DeploymentCard(
        model_name=model_name,
        model_version=model_version,
        artifact_path=str(artifact_path),
        training_data_snapshot=training_data_snapshot,
        metrics=metrics,
        feature_order=feature_order,
        created_at=datetime.now(timezone.utc).isoformat(),
        expected_inputs=expected_inputs,
        expected_outputs=expected_outputs,
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    card_path = artifact_dir / "deployment_card.json"
    card_path.write_text(json.dumps(asdict(card), indent=2), encoding="utf-8")
    return card_path
