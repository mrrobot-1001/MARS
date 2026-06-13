import gradio as gr
import pandas as pd
import joblib

# --- Model Loading ---
TRACK_MODEL_PATH = "mars-track-risk.joblib"
WEATHER_MODEL_PATH = "mars-weather-risk.joblib"

TRACK_FEATURE_ORDER = [
    "speed_mean", "speed_std", "speed_max", "acceleration_abs_mean",
    "vibration_vertical_mean", "vibration_vertical_std",
    "vibration_lateral_mean", "vibration_lateral_std",
    "track_temperature_mean", "segment_age_years", "maintenance_score",
    "curvature_degree", "max_permitted_speed",
]

WEATHER_FEATURE_ORDER = [
    *TRACK_FEATURE_ORDER,
    "rainfall_mm", "visibility_m", "temperature_c", "wind_speed_kmph",
    "flood_flag", "fog_flag", "heat_flag",
]

try:
    track_model = joblib.load(TRACK_MODEL_PATH)
    weather_model = joblib.load(WEATHER_MODEL_PATH)
    MODELS_LOADED = True
except Exception as e:
    MODELS_LOADED = False
    print(f"Failed to load joblib models: {e}")

# --- Fallback Logic ---
def _clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, float(value)))

def rule_based_track_score(features):
    speed_ratio = _clamp(features['speed_max'] / max(features['max_permitted_speed'], 1.0))
    vibration = _clamp(features['vibration_vertical_mean'] * 0.55 + features['vibration_lateral_mean'] * 0.45)
    age = _clamp(features['segment_age_years'] / 60.0)
    maintenance_risk = 1.0 - _clamp(features['maintenance_score'])
    heat = _clamp((features['track_temperature_mean'] - 35.0) / 35.0)
    curve = _clamp(features['curvature_degree'] / 8.0)
    return _clamp(speed_ratio * 0.18 + vibration * 0.30 + age * 0.15 + maintenance_risk * 0.22 + heat * 0.08 + curve * 0.07)

def rule_based_weather_score(features):
    track_base = rule_based_track_score(features)
    rainfall = _clamp(features['rainfall_mm'] / 120.0)
    low_vis = _clamp((1200.0 - features['visibility_m']) / 1200.0)
    wind = _clamp(features['wind_speed_kmph'] / 120.0)
    heat = _clamp((features['temperature_c'] - 38.0) / 18.0)
    flags = _clamp((features['flood_flag'] + features['fog_flag'] + features['heat_flag']) / 2.0)
    return _clamp(track_base * 0.42 + rainfall * 0.22 + low_vis * 0.14 + wind * 0.08 + heat * 0.06 + flags * 0.08)

def predict_score(model_obj, features_dict, feature_order, is_weather):
    if MODELS_LOADED:
        row = pd.DataFrame([{name: float(features_dict[name]) for name in feature_order}])
        if hasattr(model_obj, "predict_proba"):
            probabilities = model_obj.predict_proba(row)[0]
            classes = list(getattr(model_obj, "classes_", range(len(probabilities))))
            weighted = sum(float(cls) * float(prob) for cls, prob in zip(classes, probabilities))
            return max(0.0, min(1.0, weighted / 2.0))
        prediction = float(model_obj.predict(row)[0])
        return max(0.0, min(1.0, prediction / 2.0))
    else:
        return rule_based_weather_score(features_dict) if is_weather else rule_based_track_score(features_dict)

def classify(score):
    if score >= 0.68:
        return "🔴 HIGH RISK (Restrict Speed)", 2
    elif score >= 0.35:
        return "🟡 CAUTION (Caution Advisory)", 1
    return "🟢 NORMAL (Normal Operations)", 0

# --- UI Setup ---
def evaluate_track(speed, acc, vib_v, vib_l, temp, age, maint, curve, max_speed):
    features = {
        "speed_mean": speed, "speed_std": 0, "speed_max": speed, "acceleration_abs_mean": abs(acc),
        "vibration_vertical_mean": vib_v, "vibration_vertical_std": 0,
        "vibration_lateral_mean": vib_l, "vibration_lateral_std": 0,
        "track_temperature_mean": temp, "segment_age_years": age, "maintenance_score": maint,
        "curvature_degree": curve, "max_permitted_speed": max_speed
    }
    score = predict_score(track_model if MODELS_LOADED else None, features, TRACK_FEATURE_ORDER, False)
    sev, cls = classify(score)
    return round(score, 2), sev, cls, features

def evaluate_weather(speed, acc, vib_v, vib_l, temp, age, maint, curve, max_speed, rain, vis, w_temp, wind, flood, fog, heat):
    features = {
        "speed_mean": speed, "speed_std": 0, "speed_max": speed, "acceleration_abs_mean": abs(acc),
        "vibration_vertical_mean": vib_v, "vibration_vertical_std": 0,
        "vibration_lateral_mean": vib_l, "vibration_lateral_std": 0,
        "track_temperature_mean": temp, "segment_age_years": age, "maintenance_score": maint,
        "curvature_degree": curve, "max_permitted_speed": max_speed,
        "rainfall_mm": rain, "visibility_m": vis, "temperature_c": w_temp, "wind_speed_kmph": wind,
        "flood_flag": int(flood), "fog_flag": int(fog), "heat_flag": int(heat)
    }
    score = predict_score(weather_model if MODELS_LOADED else None, features, WEATHER_FEATURE_ORDER, True)
    sev, cls = classify(score)
    return round(score, 2), sev, cls, features

with gr.Blocks(theme=gr.themes.Soft(), title="🚂 MARS — Railway Risk Assessment") as demo:
    gr.Markdown("# 🚂 MARS — Railway Risk & Anomaly Detection")
    gr.Markdown("Real-time risk prediction for railway track segments using machine learning. Assesses track safety based on sensor data and weather conditions.")
    if not MODELS_LOADED:
        gr.Markdown("⚠️ **Note**: Using fallback mathematical simulator since `.joblib` models were not found.")

    with gr.Tab("Track Risk Prediction"):
        with gr.Row():
            with gr.Column():
                speed = gr.Slider(0, 250, value=85, label="Speed (km/h)")
                acc = gr.Slider(-5, 5, step=0.1, value=0.2, label="Acceleration (m/s²)")
                vib_v = gr.Slider(0, 2, step=0.01, value=0.25, label="Vibration Vertical (g)")
                vib_l = gr.Slider(0, 2, step=0.01, value=0.18, label="Vibration Lateral (g)")
                temp = gr.Slider(-20, 80, value=32, label="Track Temperature (°C)")
                age = gr.Slider(0, 70, value=15, label="Segment Age (years)")
                maint = gr.Slider(0, 1, step=0.01, value=0.75, label="Maintenance Score")
                curve = gr.Slider(0, 10, step=0.1, value=2, label="Curvature (degrees)")
                max_speed = gr.Slider(40, 250, step=10, value=110, label="Max Permitted Speed (km/h)")
                btn_track = gr.Button("Predict Track Risk", variant="primary")
            with gr.Column():
                out_t_score = gr.Number(label="Risk Score")
                out_t_sev = gr.Textbox(label="Severity Level")
                out_t_cls = gr.Number(label="Risk Class")
                out_t_json = gr.JSON(label="Feature Vector")
        btn_track.click(evaluate_track, inputs=[speed, acc, vib_v, vib_l, temp, age, maint, curve, max_speed], outputs=[out_t_score, out_t_sev, out_t_cls, out_t_json])

    with gr.Tab("Weather-Track Fusion"):
        with gr.Row():
            with gr.Column():
                rain = gr.Slider(0, 200, value=5, label="Rainfall (mm)")
                vis = gr.Slider(50, 15000, step=50, value=5000, label="Visibility (m)")
                w_temp = gr.Slider(-30, 60, value=28, label="Ambient Temperature (°C)")
                wind = gr.Slider(0, 150, value=20, label="Wind Speed (km/h)")
                flood = gr.Checkbox(label="Flood Warning")
                fog = gr.Checkbox(label="Fog Warning")
                heat = gr.Checkbox(label="Heat Warning")
                btn_weather = gr.Button("Predict Fused Risk", variant="primary")
            with gr.Column():
                out_w_score = gr.Number(label="Risk Score")
                out_w_sev = gr.Textbox(label="Severity Level")
                out_w_cls = gr.Number(label="Risk Class")
                out_w_json = gr.JSON(label="Feature Vector")
        btn_weather.click(evaluate_weather, inputs=[speed, acc, vib_v, vib_l, temp, age, maint, curve, max_speed, rain, vis, w_temp, wind, flood, fog, heat], outputs=[out_w_score, out_w_sev, out_w_cls, out_w_json])

    gr.Markdown("---")
    gr.Markdown("*Built with MARS ML Pipeline | Powered by scikit-learn & Gradio*")

if __name__ == "__main__":
    demo.launch()
