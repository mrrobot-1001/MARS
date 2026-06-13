---
title: MARS Engine Predictive Maintenance
emoji: 🚂
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 5.34.2
app_file: app.py
pinned: false
license: mit
short_description: AI-powered engine predictive maintenance
---

# MARS — Engine Predictive Maintenance

Real-time predictive maintenance for train engines using machine learning. This system assesses engine health based on sensor telemetry.

## Models
- **Engine Risk Model**: GradientBoosting classifier trained on RPM, coolant/oil temperatures, and pressures.

## Risk Levels
- 🟢 **Normal** (score < 0.35): Standard operations
- 🟡 **Caution** (0.35 ≤ score < 0.68): Schedule Maintenance
- 🔴 **High Risk** (score ≥ 0.68): Stop Engine Immediately
