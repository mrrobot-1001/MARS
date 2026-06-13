---
title: MARS Railway Risk Prediction
emoji: 🚂
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 5.34.2
app_file: app.py
pinned: false
license: mit
short_description: AI-powered railway track risk assessment
---

# MARS — Railway Risk & Anomaly Detection

Real-time risk prediction for railway track segments using machine learning. This system assesses track safety based on sensor data and weather conditions.

## Models
- **Track Risk Model**: GradientBoosting classifier trained on vibration, speed, temperature, and track metadata
- **Weather-Track Fusion Model**: Combines track sensor features with weather data for comprehensive risk assessment

## Risk Levels
- 🟢 **Normal** (score < 0.35): Standard operations
- 🟡 **Caution** (0.35 ≤ score < 0.68): Reduced speed advisory
- 🔴 **High Risk** (score ≥ 0.68): Speed restriction required
