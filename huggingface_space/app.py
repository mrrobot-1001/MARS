from __future__ import annotations

import joblib
import gradio as gr
import pandas as pd


TRACK_MODEL_PATH = "mars-track-risk.joblib"
WEATHER_MODEL_PATH = "mars-weather-risk.joblib"

TRACK_FEATURE_ORDER = [
    "speed_mean",
    "speed_std",
    "speed_max",
    "acceleration_abs_mean",
    "vibration_vertical_mean",
    "vibration_vertical_std",
    "vibration_lateral_mean",
    "vibration_lateral_std",
    "track_temperature_mean",
    "segment_age_years",
    "maintenance_score",
    "curvature_degree",
    "max_permitted_speed",
]

WEATHER_FEATURE_ORDER = [
    *TRACK_FEATURE_ORDER,
    "rainfall_mm",
    "visibility_m",
    "temperature_c",
    "wind_speed_kmph",
    "flood_flag",
    "fog_flag",
    "heat_flag",
]

REGION_PROFILES = {
    "NR": {
        "name": "Northern Railway",
        "headquarters": "New Delhi",
        "divisions": ["Delhi", "Ambala", "Firozpur", "Lucknow", "Moradabad"],
        "condition": "Winter fog, congestion, mixed-speed corridors",
        "hazards": ["fog", "cold wave", "heat"],
        "speed_factor": 0.98,
        "vibration_factor": 1.05,
        "weather_factor": 1.12,
        "maintenance_factor": 1.03,
    },
    "CR": {
        "name": "Central Railway",
        "headquarters": "Mumbai CSMT",
        "divisions": ["Mumbai", "Bhusawal", "Nagpur", "Pune", "Solapur"],
        "condition": "Steep gradients, curve wear, ghat sections, monsoon disruption",
        "hazards": ["flood", "landslide", "heat"],
        "speed_factor": 0.95,
        "vibration_factor": 1.16,
        "weather_factor": 1.18,
        "maintenance_factor": 1.08,
    },
    "WR": {
        "name": "Western Railway",
        "headquarters": "Mumbai Churchgate",
        "divisions": ["Mumbai Central", "Vadodara", "Ahmedabad", "Ratlam", "Rajkot", "Bhavnagar"],
        "condition": "Coastal salinity, heat, dust, high-speed trunk traffic",
        "hazards": ["heat", "dust", "cyclone"],
        "speed_factor": 1.04,
        "vibration_factor": 1.02,
        "weather_factor": 1.07,
        "maintenance_factor": 1.02,
    },
    "ER": {
        "name": "Eastern Railway",
        "headquarters": "Kolkata",
        "divisions": ["Howrah", "Sealdah", "Asansol", "Malda"],
        "condition": "Deltaic plains, bridges, dense suburban operations, waterlogging",
        "hazards": ["flood", "fog", "cyclone"],
        "speed_factor": 0.96,
        "vibration_factor": 1.09,
        "weather_factor": 1.20,
        "maintenance_factor": 1.07,
    },
    "SR": {
        "name": "Southern Railway",
        "headquarters": "Chennai",
        "divisions": ["Chennai", "Tiruchirappalli", "Madurai", "Salem", "Palakkad", "Thiruvananthapuram"],
        "condition": "Coastal humidity, corrosion, hill approaches, monsoon bursts",
        "hazards": ["flood", "cyclone", "heat"],
        "speed_factor": 0.98,
        "vibration_factor": 1.04,
        "weather_factor": 1.14,
        "maintenance_factor": 1.05,
    },
    "NFR": {
        "name": "Northeast Frontier Railway",
        "headquarters": "Maligaon",
        "divisions": ["Katihar", "Alipurduar", "Rangiya", "Lumding", "Tinsukia"],
        "condition": "Hills, rivers, washouts, landslides, tight curves, remote maintenance",
        "hazards": ["flood", "landslide", "fog"],
        "speed_factor": 0.88,
        "vibration_factor": 1.22,
        "weather_factor": 1.30,
        "maintenance_factor": 1.14,
    },
    "NWR": {
        "name": "North Western Railway",
        "headquarters": "Jaipur",
        "divisions": ["Jaipur", "Jodhpur", "Bikaner", "Ajmer"],
        "condition": "Desert heat, sand ingress, sparse routes, thermal stress",
        "hazards": ["heat", "dust"],
        "speed_factor": 1.02,
        "vibration_factor": 1.03,
        "weather_factor": 1.08,
        "maintenance_factor": 1.06,
    },
}


try:
    track_model = joblib.load(TRACK_MODEL_PATH)
    weather_model = joblib.load(WEATHER_MODEL_PATH)
    MODELS_LOADED = True
except Exception as exc:
    track_model = None
    weather_model = None
    MODELS_LOADED = False
    print(f"Failed to load joblib models: {exc}")


def clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, float(value)))


def region_profile(region):
    return REGION_PROFILES.get(region, REGION_PROFILES["CR"])


def track_features(speed, acc, vib_v, vib_l, temp, age, maint, curve, max_speed):
    return {
        "speed_mean": speed,
        "speed_std": 0,
        "speed_max": speed,
        "acceleration_abs_mean": abs(acc),
        "vibration_vertical_mean": vib_v,
        "vibration_vertical_std": 0,
        "vibration_lateral_mean": vib_l,
        "vibration_lateral_std": 0,
        "track_temperature_mean": temp,
        "segment_age_years": age,
        "maintenance_score": maint,
        "curvature_degree": curve,
        "max_permitted_speed": max_speed,
    }


def rule_track_score(features, profile):
    speed_ratio = clamp((features["speed_max"] / max(features["max_permitted_speed"], 1.0)) / profile["speed_factor"])
    vibration = clamp(
        (features["vibration_vertical_mean"] * 0.55 + features["vibration_lateral_mean"] * 0.45)
        * profile["vibration_factor"]
    )
    age = clamp(features["segment_age_years"] / 60.0)
    maintenance = clamp((1.0 - clamp(features["maintenance_score"])) * profile["maintenance_factor"])
    heat = clamp((features["track_temperature_mean"] - 35.0) / 35.0)
    curve = clamp(features["curvature_degree"] / 8.0)
    return clamp(
        speed_ratio * 0.18
        + vibration * 0.30
        + age * 0.15
        + maintenance * 0.22
        + heat * 0.08
        + curve * 0.07
    )


def rule_weather_score(features, profile):
    base = rule_track_score(features, profile)
    rainfall = clamp((features["rainfall_mm"] / 120.0) * profile["weather_factor"])
    low_vis = clamp((1200.0 - features["visibility_m"]) / 1200.0)
    wind = clamp(features["wind_speed_kmph"] / 120.0)
    heat = clamp((features["temperature_c"] - 38.0) / 18.0)
    flags = clamp(
        (features["flood_flag"] + features["fog_flag"] + features["heat_flag"]) / 2.0
        * profile["weather_factor"]
    )
    return clamp(base * 0.42 + rainfall * 0.22 + low_vis * 0.14 + wind * 0.08 + heat * 0.06 + flags * 0.08)


def model_score(model_obj, features, feature_order):
    row = pd.DataFrame([{name: float(features[name]) for name in feature_order}])
    if hasattr(model_obj, "predict_proba"):
        probabilities = model_obj.predict_proba(row)[0]
        classes = list(getattr(model_obj, "classes_", range(len(probabilities))))
        weighted = sum(float(cls) * float(prob) for cls, prob in zip(classes, probabilities))
        return clamp(weighted / 2.0)
    return clamp(float(model_obj.predict(row)[0]) / 2.0)


def adjusted_score(base_score, profile, mode):
    if mode == "track":
        uplift = ((profile["vibration_factor"] - 1.0) * 0.16) + ((profile["maintenance_factor"] - 1.0) * 0.12)
    else:
        uplift = ((profile["weather_factor"] - 1.0) * 0.18) + ((profile["vibration_factor"] - 1.0) * 0.08)
    return clamp(base_score + max(0, uplift))


def classify(score):
    if score >= 0.68:
        return "HIGH RISK", 2, "Restrict speed, alert control, schedule urgent inspection."
    if score >= 0.35:
        return "CAUTION", 1, "Issue caution advisory and increase inspection frequency."
    return "NORMAL", 0, "Continue normal operations with routine monitoring."


def security_score(trespasser_conf, obstruction_conf, crowding_conf, camera_visibility):
    visibility_penalty = clamp((70 - camera_visibility) / 70.0)
    score = max(trespasser_conf, obstruction_conf, crowding_conf) * 0.78 + visibility_penalty * 0.22
    return clamp(score)


def update_divisions(region):
    profile = region_profile(region)
    return gr.Dropdown(choices=profile["divisions"], value=profile["divisions"][0])


def describe_region(region):
    profile = region_profile(region)
    return {
        "zone": region,
        "name": profile["name"],
        "headquarters": profile["headquarters"],
        "divisions": profile["divisions"],
        "operating_condition": profile["condition"],
        "regional_hazards": profile["hazards"],
        "speed_factor": profile["speed_factor"],
        "vibration_factor": profile["vibration_factor"],
        "weather_factor": profile["weather_factor"],
        "maintenance_factor": profile["maintenance_factor"],
    }


def evaluate_multimodal(
    region,
    division,
    speed,
    acc,
    vib_v,
    vib_l,
    temp,
    age,
    maint,
    curve,
    max_speed,
    rain,
    vis,
    w_temp,
    wind,
    flood,
    fog,
    heat,
    trespasser_conf,
    obstruction_conf,
    crowding_conf,
    camera_visibility,
):
    profile = region_profile(region)
    features = track_features(speed, acc, vib_v, vib_l, temp, age, maint, curve, max_speed)
    weather_features = {
        **features,
        "rainfall_mm": rain,
        "visibility_m": vis,
        "temperature_c": w_temp,
        "wind_speed_kmph": wind,
        "flood_flag": int(flood),
        "fog_flag": int(fog),
        "heat_flag": int(heat),
    }

    if MODELS_LOADED:
        raw_track = model_score(track_model, features, TRACK_FEATURE_ORDER)
        raw_weather = model_score(weather_model, weather_features, WEATHER_FEATURE_ORDER)
        track_risk = adjusted_score(raw_track, profile, "track")
        weather_risk = adjusted_score(raw_weather, profile, "weather")
        model_mode = "joblib model + regional adjustment"
    else:
        track_risk = rule_track_score(features, profile)
        weather_risk = rule_weather_score(weather_features, profile)
        model_mode = "rule-based regional simulator"

    camera_risk = security_score(trespasser_conf, obstruction_conf, crowding_conf, camera_visibility)
    combined = clamp(track_risk * 0.42 + weather_risk * 0.40 + camera_risk * 0.18)
    severity, risk_class, action = classify(combined)

    summary = (
        f"### {severity} | Combined risk: {combined:.2f}\n"
        f"**Recommended action:** {action}\n\n"
        f"**Region context:** {region} / {division} - {profile['name']} ({profile['headquarters']} HQ). "
        f"{profile['condition']}\n\n"
        f"**Modal scores:** Track `{track_risk:.2f}` | Weather `{weather_risk:.2f}` | "
        f"Security/video `{camera_risk:.2f}`"
    )
    details = {
        "model_mode": model_mode,
        "risk_class": risk_class,
        "combined_score": round(combined, 3),
        "track_score": round(track_risk, 3),
        "weather_score": round(weather_risk, 3),
        "security_video_score": round(camera_risk, 3),
        "region": describe_region(region),
        "track_features": features,
        "weather_features": weather_features,
        "security_inputs": {
            "trespasser_confidence": trespasser_conf,
            "obstruction_confidence": obstruction_conf,
            "crowding_confidence": crowding_conf,
            "camera_visibility_percent": camera_visibility,
        },
    }
    return round(combined, 3), severity, action, summary, details


with gr.Blocks(theme=gr.themes.Soft(), title="MARS Railway Multimodal Safety Simulator") as demo:
    gr.Markdown("# MARS Railway Multimodal Safety Simulator")
    gr.Markdown(
        "Change the sensor, weather, video/security, and Indian Railway zone inputs to see how "
        "MARS fuses multiple signals into an operational railway safety decision."
    )
    if MODELS_LOADED:
        gr.Markdown("Using bundled `.joblib` models with regional operating adjustments.")
    else:
        gr.Markdown("Using the built-in regional simulator because model artifacts were not found.")

    with gr.Row():
        with gr.Column(scale=1):
            region = gr.Dropdown(choices=list(REGION_PROFILES.keys()), value="CR", label="Indian Railway Zone")
            division = gr.Dropdown(choices=REGION_PROFILES["CR"]["divisions"], value="Mumbai", label="Division")
            region_info = gr.JSON(value=describe_region("CR"), label="Regional Operating Profile")
        with gr.Column(scale=2):
            final_score = gr.Number(label="Combined Multimodal Risk Score", precision=3)
            final_severity = gr.Textbox(label="Severity")
            final_action = gr.Textbox(label="Recommended Action")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Track Sensor Inputs")
            speed = gr.Slider(0, 250, value=85, label="Train Speed (km/h)")
            acc = gr.Slider(-5, 5, step=0.1, value=0.2, label="Acceleration (m/s²)")
            vib_v = gr.Slider(0, 2, step=0.01, value=0.25, label="Vertical Vibration (g)")
            vib_l = gr.Slider(0, 2, step=0.01, value=0.18, label="Lateral Vibration (g)")
            temp = gr.Slider(-20, 80, value=32, label="Track Temperature (°C)")
            age = gr.Slider(0, 70, value=15, label="Segment Age (years)")
            maint = gr.Slider(0, 1, step=0.01, value=0.75, label="Maintenance Score")
            curve = gr.Slider(0, 10, step=0.1, value=2, label="Curvature (degrees)")
            max_speed = gr.Slider(40, 250, step=10, value=110, label="Max Permitted Speed (km/h)")

        with gr.Column():
            gr.Markdown("### Weather Fusion Inputs")
            rain = gr.Slider(0, 220, value=34, label="Rainfall (mm)")
            vis = gr.Slider(50, 15000, step=50, value=5200, label="Visibility (m)")
            w_temp = gr.Slider(-30, 60, value=32, label="Ambient Temperature (°C)")
            wind = gr.Slider(0, 150, value=20, label="Wind Speed (km/h)")
            flood = gr.Checkbox(label="Flood / Waterlogging Warning")
            fog = gr.Checkbox(label="Fog Warning")
            heat = gr.Checkbox(label="Heat Warning")

            gr.Markdown("### Video / Security Inputs")
            trespasser_conf = gr.Slider(0, 1, step=0.01, value=0.05, label="Trespasser Detection Confidence")
            obstruction_conf = gr.Slider(0, 1, step=0.01, value=0.08, label="Track Obstruction Confidence")
            crowding_conf = gr.Slider(0, 1, step=0.01, value=0.10, label="Platform Crowding Confidence")
            camera_visibility = gr.Slider(0, 100, value=90, label="Camera Visibility (%)")

    run = gr.Button("Run Multimodal Assessment", variant="primary")
    summary = gr.Markdown()
    details = gr.JSON(label="Full Model Inputs and Scores")

    all_inputs = [
        region,
        division,
        speed,
        acc,
        vib_v,
        vib_l,
        temp,
        age,
        maint,
        curve,
        max_speed,
        rain,
        vis,
        w_temp,
        wind,
        flood,
        fog,
        heat,
        trespasser_conf,
        obstruction_conf,
        crowding_conf,
        camera_visibility,
    ]
    run.click(
        evaluate_multimodal,
        inputs=all_inputs,
        outputs=[final_score, final_severity, final_action, summary, details],
    )
    demo.load(
        evaluate_multimodal,
        inputs=all_inputs,
        outputs=[final_score, final_severity, final_action, summary, details],
    )
    region.change(update_divisions, inputs=region, outputs=division)
    region.change(describe_region, inputs=region, outputs=region_info)

    gr.Examples(
        examples=[
            ["CR", "Mumbai", 92, 0.4, 0.42, 0.30, 38, 24, 0.62, 4.5, 105, 80, 900, 34, 70, True, False, False, 0.05, 0.18, 0.12, 72],
            ["NFR", "Lumding", 70, 0.3, 0.55, 0.38, 29, 34, 0.58, 7.0, 80, 120, 650, 27, 82, True, True, False, 0.18, 0.38, 0.10, 58],
            ["WR", "Ahmedabad", 122, 0.1, 0.24, 0.20, 47, 16, 0.78, 1.5, 130, 4, 7000, 45, 18, False, False, True, 0.03, 0.05, 0.16, 94],
        ],
        inputs=all_inputs,
        outputs=[final_score, final_severity, final_action, summary, details],
        fn=evaluate_multimodal,
        cache_examples=False,
    )

    gr.Markdown("---")
    gr.Markdown("Built with MARS ML Pipeline | Track sensors + weather fusion + video/security anomaly signal")


if __name__ == "__main__":
    demo.launch()
