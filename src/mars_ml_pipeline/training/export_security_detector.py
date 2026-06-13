from __future__ import annotations

import argparse
from pathlib import Path

from mars_ml_pipeline.artifact import write_deployment_card


def main() -> None:
    parser = argparse.ArgumentParser(description="Register a pretrained/fine-tuned security detector.")
    parser.add_argument("--artifact-path", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--model-version", default="0.1.0")
    parser.add_argument("--map50", type=float, default=0.0)
    parser.add_argument("--f1", type=float, default=0.0)
    args = parser.parse_args()

    write_deployment_card(
        artifact_dir=args.artifact_dir,
        model_name="mars-security-anomaly",
        model_version=args.model_version,
        artifact_path=args.artifact_path,
        training_data_snapshot="manual-label-export",
        metrics={"map50": args.map50, "f1": args.f1},
        feature_order=[],
        expected_inputs={"schema": "SecurityAnomalyRequest", "image_size": "model-dependent"},
        expected_outputs={"schema": "SecurityPrediction"},
    )
    print(f"registered {args.artifact_path}")


if __name__ == "__main__":
    main()
