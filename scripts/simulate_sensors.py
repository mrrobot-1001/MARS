from __future__ import annotations

import argparse
import asyncio
import random
from datetime import datetime, timezone
from pathlib import Path
import sys

import httpx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mars_ml_pipeline.regions import REGION_PROFILES, RegionProfile  # noqa: E402


API_BASE_URL = "http://localhost:8000"


def build_segments() -> list[dict[str, object]]:
    segments: list[dict[str, object]] = []
    index = 1
    for profile in REGION_PROFILES.values():
        for division in profile.divisions[:3]:
            max_speed = random.choice([80, 100, 110, 120, 130]) + profile.max_speed_bias
            segments.append(
                {
                    "segment_id": f"{profile.code}-SEG-{index:03d}",
                    "line_id": f"{profile.code}-{division.upper().replace(' ', '-')}",
                    "region": profile.code,
                    "division": division,
                    "asset_type": random.choice(["track", "bridge", "tunnel", "yard"]),
                    "age_years": round(random.uniform(5, 58), 1),
                    "maintenance_score": round(random.uniform(0.34, 0.92), 2),
                    "curvature_degree": round(random.uniform(0.4, 7.8) * profile.vibration_factor, 2),
                    "max_permitted_speed": max(45, min(160, max_speed)),
                }
            )
            index += 1
    return segments


def sensor_event(segment: dict[str, object], profile: RegionProfile) -> dict[str, object]:
    risky_window = random.random() < (
        0.18 + (profile.vibration_factor - 1.0) * 0.22 + (profile.maintenance_factor - 1.0) * 0.18
    )
    max_speed = float(segment["max_permitted_speed"])
    speed_ratio = random.gauss(1.04 if risky_window else 0.78, 0.08)
    vibration_base = 0.72 if risky_window else 0.22
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "segment_id": segment["segment_id"],
        "train_id": f"IR-{random.randint(10000, 99999)}",
        "speed": round(max(0, min(245, max_speed * speed_ratio)), 2),
        "acceleration": round(random.gauss(0, 0.7), 3),
        "vibration_vertical": round(max(0.03, random.gauss(vibration_base, 0.11) * profile.vibration_factor), 3),
        "vibration_lateral": round(max(0.02, random.gauss(vibration_base * 0.72, 0.09) * profile.vibration_factor), 3),
        "track_temperature": round(random.gauss(profile.temperature_baseline_c + (5 if risky_window else 0), 4), 2),
    }


def weather_event(segment: dict[str, object], profile: RegionProfile) -> dict[str, object]:
    storm = random.random() < min(0.45, 0.08 + profile.weather_factor * 0.12)
    fog = "fog" in profile.climate_hazards and random.random() < 0.22
    heat = "heat" in profile.climate_hazards and random.random() < 0.24
    flags = []
    if storm and "flood" in profile.climate_hazards:
        flags.append("flood")
    if storm and "landslide" in profile.climate_hazards:
        flags.append("landslide")
    if fog:
        flags.append("fog")
    if heat:
        flags.append("heat")
    if storm and "cyclone" in profile.climate_hazards and random.random() < 0.18:
        flags.append("cyclone")

    rainfall = profile.rainfall_baseline_mm + (random.uniform(40, 150) if storm else random.uniform(0, 12))
    visibility = random.uniform(150, 900) if fog else random.gauss(profile.visibility_baseline_m, 950)
    temperature = profile.temperature_baseline_c + (random.uniform(6, 14) if heat else random.uniform(-4, 4))
    wind = random.uniform(45, 115) if storm else random.uniform(4, 42)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "segment_id": segment["segment_id"],
        "region": profile.code,
        "rainfall_mm": round(max(0, rainfall), 2),
        "visibility_m": round(max(50, visibility), 2),
        "temperature_c": round(temperature, 2),
        "wind_speed_kmph": round(wind, 2),
        "hazard_flags": flags,
    }


async def simulate_sensor_data(base_url: str, interval: float) -> None:
    print(f"Starting Indian Railways regional sensor simulation -> {base_url}")
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{base_url}/health")
            print(f"Backend health: {response.status_code} {response.json()}")
        except Exception as exc:
            print(f"Failed to connect to backend: {exc}")
            return

        segments = build_segments()
        while True:
            segment = random.choice(segments)
            profile = REGION_PROFILES[str(segment["region"])]
            event_window = [sensor_event(segment, profile) for _ in range(4)]
            weather = weather_event(segment, profile)

            track_payload = {"segment": segment, "events": event_window}
            weather_payload = {
                "segment": segment,
                "sensor_events": event_window,
                "weather": weather,
            }

            try:
                track_result, weather_result = await asyncio.gather(
                    client.post(f"{base_url}/track-risk/predict", json=track_payload),
                    client.post(f"{base_url}/weather-risk/predict", json=weather_payload),
                )
                if track_result.status_code == 200 and weather_result.status_code == 200:
                    track = track_result.json()
                    fusion = weather_result.json()
                    division = segment["division"]
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] "
                        f"{profile.code}/{division} {segment['segment_id']} "
                        f"track={track['severity']}:{track['risk_score']:.2f} "
                        f"weather={fusion['severity']}:{fusion['risk_score']:.2f} "
                        f"hazards={weather['hazard_flags'] or ['clear']}"
                    )
                else:
                    print(f"Track error {track_result.status_code}: {track_result.text}")
                    print(f"Weather error {weather_result.status_code}: {weather_result.text}")
            except Exception as exc:
                print(f"Request failed: {exc}")

            await asyncio.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate regional Indian Railways sensor data.")
    parser.add_argument("--base-url", default=API_BASE_URL)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    asyncio.run(simulate_sensor_data(args.base_url.rstrip("/"), args.interval))


if __name__ == "__main__":
    main()
