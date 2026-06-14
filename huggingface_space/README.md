---
title: MARS Railway Multimodal Safety Simulator
emoji: 🚂
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 5.34.2
app_file: app.py
pinned: false
license: mit
short_description: Region-aware multimodal railway safety simulator
---

# MARS — Region-Aware Multimodal Railway Safety

Interactive Gradio demo for the MARS railway safety system. Users can change track sensor telemetry, weather hazards, video/security anomaly signals, and Indian Railway zone/division context to see how the system fuses multiple modalities into an operational risk decision.

## What You Can Try
- Select an Indian Railway zone such as `CR`, `WR`, `ER`, `SR`, `NR`, `NFR`, or `NWR`.
- Change division-specific context and see the regional operating profile.
- Adjust track inputs: speed, vibration, curvature, temperature, age, maintenance score.
- Adjust weather inputs: rainfall, visibility, wind, heat, flood, fog.
- Adjust video/security inputs: trespasser, obstruction, crowding, camera visibility.
- Run a multimodal assessment and inspect the individual track, weather, and security scores.

## Modalities
- **Track risk**: speed, acceleration, vibration, temperature, geometry, maintenance.
- **Weather fusion**: rainfall, visibility, wind, ambient temperature, hazard flags.
- **Video/security signal**: detection confidence for trespassers, obstructions, platform crowding, and low-visibility camera conditions.
- **Regional operations**: zone-specific factors for terrain, weather, maintenance difficulty, and permitted speed behavior.

## Risk Levels
- 🟢 **Normal** (score < 0.35): Standard operations
- 🟡 **Caution** (0.35 ≤ score < 0.68): Reduced speed advisory
- 🔴 **High Risk** (score ≥ 0.68): Speed restriction required
