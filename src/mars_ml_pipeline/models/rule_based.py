from __future__ import annotations

from mars_ml_pipeline.features import WEATHER_FEATURE_ORDER


class RuleBasedTrackRiskModel:
    model_version = "rule-based-track-v0"

    def predict_score(self, features: dict[str, float]) -> float:
        speed_ratio = _clamp(features["speed_max"] / max(features["max_permitted_speed"], 1.0))
        regional_speed = features.get("regional_speed_factor", 1.0)
        regional_vibration = features.get("regional_vibration_factor", 1.0)
        regional_maintenance = features.get("regional_maintenance_factor", 1.0)
        vibration = _clamp(
            (
                (features["vibration_vertical_mean"] * 0.55)
                + (features["vibration_lateral_mean"] * 0.45)
            )
            * regional_vibration
        )
        age = _clamp(features["segment_age_years"] / 60.0)
        maintenance_risk = _clamp((1.0 - _clamp(features["maintenance_score"])) * regional_maintenance)
        heat = _clamp((features["track_temperature_mean"] - 35.0) / 35.0)
        curve = _clamp(features["curvature_degree"] / 8.0)

        score = (
            _clamp(speed_ratio / max(regional_speed, 0.1)) * 0.18
            + vibration * 0.30
            + age * 0.15
            + maintenance_risk * 0.22
            + heat * 0.08
            + curve * 0.07
        )
        return _clamp(score)


class RuleBasedWeatherRiskModel:
    model_version = "rule-based-weather-v0"

    def predict_score(self, features: dict[str, float]) -> float:
        missing = [name for name in WEATHER_FEATURE_ORDER if name not in features]
        if missing:
            raise ValueError(f"missing weather features: {missing}")

        track_base = RuleBasedTrackRiskModel().predict_score(features)
        rainfall = _clamp(features["rainfall_mm"] / 120.0)
        low_visibility = _clamp((1200.0 - features["visibility_m"]) / 1200.0)
        wind = _clamp(features["wind_speed_kmph"] / 120.0)
        heat = _clamp((features["temperature_c"] - 38.0) / 18.0)
        flags = _clamp((features["flood_flag"] + features["fog_flag"] + features["heat_flag"]) / 2.0)
        regional_weather = features.get("regional_weather_factor", 1.0)

        score = (
            track_base * 0.42
            + _clamp(rainfall * regional_weather) * 0.22
            + low_visibility * 0.14
            + wind * 0.08
            + heat * 0.06
            + _clamp(flags * regional_weather) * 0.08
        )
        return _clamp(score)


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, float(value)))
