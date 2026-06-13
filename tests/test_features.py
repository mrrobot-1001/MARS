from __future__ import annotations

import unittest

from mars_ml_pipeline.features import build_track_features, build_weather_features
from mars_ml_pipeline.recommendations import classify_score


class FeatureTests(unittest.TestCase):
    def test_build_track_features_aggregates_window(self) -> None:
        events = [
            {
                "speed": 80,
                "acceleration": -0.2,
                "vibration_vertical": 0.2,
                "vibration_lateral": 0.1,
                "track_temperature": 31,
            },
            {
                "speed": 100,
                "acceleration": 0.4,
                "vibration_vertical": 0.4,
                "vibration_lateral": 0.3,
                "track_temperature": 35,
            },
        ]
        segment = {
            "age_years": 20,
            "maintenance_score": 0.8,
            "curvature_degree": 2,
            "max_permitted_speed": 110,
        }

        features = build_track_features(events, segment)

        self.assertEqual(features["speed_mean"], 90)
        self.assertEqual(features["speed_max"], 100)
        self.assertAlmostEqual(features["acceleration_abs_mean"], 0.3)

    def test_build_weather_features_encodes_flags(self) -> None:
        track = {"speed_mean": 80}
        weather = {
            "rainfall_mm": 50,
            "visibility_m": 500,
            "temperature_c": 44,
            "wind_speed_kmph": 70,
            "hazard_flags": ["fog", "heat"],
        }

        features = build_weather_features(track, weather)

        self.assertEqual(features["fog_flag"], 1)
        self.assertEqual(features["heat_flag"], 1)
        self.assertEqual(features["flood_flag"], 0)


class RecommendationTests(unittest.TestCase):
    def test_classify_score(self) -> None:
        self.assertEqual(classify_score(0.2, 0.3, 0.7).severity, "normal")
        self.assertEqual(classify_score(0.4, 0.3, 0.7).severity, "caution")
        self.assertEqual(classify_score(0.8, 0.3, 0.7).severity, "high_risk")


if __name__ == "__main__":
    unittest.main()
