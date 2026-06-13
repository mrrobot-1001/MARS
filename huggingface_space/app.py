import gradio as gr
import pandas as pd
import joblib
import os

# --- Model Loading ---
MODEL_PATH = "mars-engine-risk.joblib"
feature_order = [
    "Engine rpm", "Lub oil pressure", "Fuel pressure", 
    "Coolant pressure", "lub oil temp", "Coolant temp"
]

try:
    model = joblib.load(MODEL_PATH)
    MODEL_LOADED = True
except Exception as e:
    MODEL_LOADED = False
    print(f"Failed to load joblib model: {e}")

# --- Prediction Logic ---
def _clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, float(value)))

def rule_based_engine_score(features):
    rpm_risk = _clamp(features["Engine rpm"] / 3000.0)
    lub_temp_risk = _clamp((features["lub oil temp"] - 60) / 60.0)
    coolant_temp_risk = _clamp((features["Coolant temp"] - 70) / 40.0)
    
    lub_pressure_risk = _clamp((3.0 - features["Lub oil pressure"]) / 2.0)
    
    return _clamp(rpm_risk * 0.2 + lub_temp_risk * 0.2 + coolant_temp_risk * 0.3 + lub_pressure_risk * 0.3)

def predict_score(features_dict):
    if MODEL_LOADED:
        row = pd.DataFrame([{name: float(features_dict[name]) for name in feature_order}])
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(row)[0]
            classes = list(getattr(model, "classes_", range(len(probabilities))))
            weighted = sum(float(cls) * float(prob) for cls, prob in zip(classes, probabilities))
            return max(0.0, min(1.0, weighted / 2.0))
        prediction = float(model.predict(row)[0])
        return max(0.0, min(1.0, prediction / 2.0))
    else:
        return rule_based_engine_score(features_dict)

def classify(score):
    if score >= 0.68:
        return "🔴 HIGH RISK (Stop Engine Immediately)", 2
    elif score >= 0.35:
        return "🟡 CAUTION (Schedule Maintenance)", 1
    return "🟢 NORMAL (Standard Operations)", 0

# --- Gradio UI Logic ---
def evaluate_engine(rpm, lub_pressure, fuel_pressure, coolant_pressure, lub_temp, coolant_temp):
    features = {
        "Engine rpm": rpm,
        "Lub oil pressure": lub_pressure,
        "Fuel pressure": fuel_pressure,
        "Coolant pressure": coolant_pressure,
        "lub oil temp": lub_temp,
        "Coolant temp": coolant_temp
    }
    score = predict_score(features)
    severity_text, risk_class = classify(score)
    
    return round(score, 2), severity_text, risk_class, features

# --- Gradio App ---
with gr.Blocks(theme=gr.themes.Soft(), title="🚂 MARS — Engine Predictive Maintenance") as demo:
    gr.Markdown("# 🚂 MARS — Engine Predictive Maintenance")
    gr.Markdown("AI-powered real-time risk prediction for train engines based on sensor telemetry.")
    if not MODEL_LOADED:
        gr.Markdown("⚠️ **Note**: Using fallback mathematical simulator since `mars-engine-risk.joblib` was not found.")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Engine Parameters")
            rpm = gr.Slider(0, 3000, value=1200, label="Engine RPM")
            lub_pressure = gr.Slider(0, 8, step=0.1, value=3.5, label="Lubrication Oil Pressure (bar)")
            fuel_pressure = gr.Slider(0, 20, step=0.1, value=10.0, label="Fuel Pressure (bar)")
            coolant_pressure = gr.Slider(0, 5, step=0.1, value=2.5, label="Coolant Pressure (bar)")
            lub_temp = gr.Slider(0, 150, value=75, label="Lubrication Oil Temp (°C)")
            coolant_temp = gr.Slider(0, 150, value=80, label="Coolant Temp (°C)")
            btn = gr.Button("Evaluate Engine Health", variant="primary")
            
        with gr.Column():
            gr.Markdown("### Risk Assessment")
            out_score = gr.Number(label="Risk Score (0.0 to 1.0)")
            out_severity = gr.Textbox(label="Severity & Action")
            out_class = gr.Number(label="Risk Class")
            out_json = gr.JSON(label="Feature Vector")
            
    btn.click(
        fn=evaluate_engine,
        inputs=[rpm, lub_pressure, fuel_pressure, coolant_pressure, lub_temp, coolant_temp],
        outputs=[out_score, out_severity, out_class, out_json]
    )

    gr.Markdown("---")
    gr.Markdown("*Built with MARS ML Pipeline | Powered by scikit-learn & Gradio*")

if __name__ == "__main__":
    demo.launch()
