from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic MARS Phase 1 tabular data.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/generated"))
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sensor_path = args.output_dir / "track_sensor_events.csv"
    weather_path = args.output_dir / "weather_events.csv"

    segments = [_segment(i) for i in range(1, 51)]
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    with sensor_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "timestamp",
                "segment_id",
                "train_id",
                "speed",
                "acceleration",
                "vibration_vertical",
                "vibration_lateral",
                "track_temperature",
                "age_years",
                "maintenance_score",
                "curvature_degree",
                "max_permitted_speed",
                "risk_label",
            ],
        )
        writer.writeheader()
        for i in range(args.rows):
            segment = random.choice(segments)
            risky = random.random() > segment["maintenance_score"] or segment["age_years"] > 42
            speed = random.gauss(segment["max_permitted_speed"] * (1.02 if risky else 0.75), 11)
            vertical = max(0.02, random.gauss(0.85 if risky else 0.24, 0.16))
            lateral = max(0.02, random.gauss(0.65 if risky else 0.18, 0.14))
            temp = random.gauss(42 if risky else 32, 6)
            score = (
                min(speed / segment["max_permitted_speed"], 1.4) * 0.22
                + min(vertical, 1.2) * 0.30
                + min(lateral, 1.2) * 0.18
                + (1 - segment["maintenance_score"]) * 0.20
                + min(segment["age_years"] / 60, 1) * 0.10
            )
            writer.writerow(
                {
                    "timestamp": (start + timedelta(minutes=i * 5)).isoformat(),
                    "segment_id": segment["segment_id"],
                    "train_id": f"T-{100 + (i % 80)}",
                    "speed": round(max(0, speed), 3),
                    "acceleration": round(random.gauss(0, 0.9), 3),
                    "vibration_vertical": round(vertical, 3),
                    "vibration_lateral": round(lateral, 3),
                    "track_temperature": round(temp, 3),
                    "age_years": segment["age_years"],
                    "maintenance_score": segment["maintenance_score"],
                    "curvature_degree": segment["curvature_degree"],
                    "max_permitted_speed": segment["max_permitted_speed"],
                    "risk_label": _label(score),
                }
            )

    with weather_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "timestamp",
                "segment_id",
                "region",
                "rainfall_mm",
                "visibility_m",
                "temperature_c",
                "wind_speed_kmph",
                "hazard_flags",
            ],
        )
        writer.writeheader()
        for i in range(args.rows):
            segment = random.choice(segments)
            storm = random.random() < 0.18
            fog = random.random() < 0.12
            heat = random.random() < 0.10
            flags = []
            if storm:
                flags.append("flood")
            if fog:
                flags.append("fog")
            if heat:
                flags.append("heat")
            writer.writerow(
                {
                    "timestamp": (start + timedelta(minutes=i * 5)).isoformat(),
                    "segment_id": segment["segment_id"],
                    "region": segment["region"],
                    "rainfall_mm": round(random.uniform(35, 130) if storm else random.uniform(0, 18), 3),
                    "visibility_m": round(random.uniform(120, 900) if fog else random.uniform(1200, 12000), 3),
                    "temperature_c": round(random.uniform(40, 52) if heat else random.uniform(18, 38), 3),
                    "wind_speed_kmph": round(random.uniform(20, 115) if storm else random.uniform(0, 45), 3),
                    "hazard_flags": "|".join(flags),
                }
            )

    print(f"wrote {sensor_path}")
    print(f"wrote {weather_path}")


def _segment(index: int) -> dict[str, float | str]:
    return {
        "segment_id": f"SEG-{index:03d}",
        "region": random.choice(["north", "south", "east", "west", "central"]),
        "age_years": round(random.uniform(2, 65), 2),
        "maintenance_score": round(random.uniform(0.25, 0.98), 3),
        "curvature_degree": round(random.uniform(0, 7), 3),
        "max_permitted_speed": random.choice([60, 80, 100, 110, 130]),
    }


def _label(score: float) -> int:
    if score >= 0.72:
        return 2
    if score >= 0.48:
        return 1
    return 0


if __name__ == "__main__":
    main()
