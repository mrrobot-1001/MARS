from __future__ import annotations

import unittest

from mars_ml_pipeline.features import build_track_features, build_weather_features
from mars_ml_pipeline.models.rule_based import RuleBasedTrackRiskModel
from mars_ml_pipeline.regions import get_region_profile
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
            "region": "CR",
            "age_years": 20,
            "maintenance_score": 0.8,
            "curvature_degree": 2,
            "max_permitted_speed": 110,
        }

        features = build_track_features(events, segment)

        self.assertEqual(features["speed_mean"], 90)
        self.assertEqual(features["speed_max"], 100)
        self.assertAlmostEqual(features["acceleration_abs_mean"], 0.3)
        self.assertEqual(features["regional_weather_factor"], get_region_profile("CR").weather_factor)

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

    def test_region_aliases_map_to_indian_railway_zones(self) -> None:
        self.assertEqual(get_region_profile("central").code, "CR")
        self.assertEqual(get_region_profile("north east").code, "NFR")
        self.assertEqual(get_region_profile("WR").name, "Western Railway")

    def test_regional_profile_changes_rule_based_track_score(self) -> None:
        events = [
            {
                "speed": 95,
                "acceleration": 0.2,
                "vibration_vertical": 0.42,
                "vibration_lateral": 0.32,
                "track_temperature": 34,
            }
        ]
        base_segment = {
            "age_years": 28,
            "maintenance_score": 0.66,
            "curvature_degree": 3.5,
            "max_permitted_speed": 110,
        }

        western = build_track_features(events, {**base_segment, "region": "WR"})
        northeast = build_track_features(events, {**base_segment, "region": "NFR"})

        model = RuleBasedTrackRiskModel()
        self.assertGreater(model.predict_score(northeast), model.predict_score(western))


class RecommendationTests(unittest.TestCase):
    def test_classify_score(self) -> None:
        self.assertEqual(classify_score(0.2, 0.3, 0.7).severity, "normal")
        self.assertEqual(classify_score(0.4, 0.3, 0.7).severity, "caution")
        self.assertEqual(classify_score(0.8, 0.3, 0.7).severity, "high_risk")


if __name__ == "__main__":
    unittest.main()
