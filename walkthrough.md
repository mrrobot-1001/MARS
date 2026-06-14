# 🚂 MARS Track Monitoring & Risk Deployment

We have successfully restored the MARS project to focus on **Track Monitoring** and generated a highly realistic synthetic dataset. The system is fully operational locally and has been pushed to GitHub. Here is a summary of the achievements:

## 1. Machine Learning & Dataset
- **Synthetic Track Dataset**: Used the built-in mathematical physics engine to generate a high-quality dataset (`data/track_sensor_dataset.csv`) that models railway segment behavior, vibrations, maintenance scores, and weather impacts. 
- **Model Training**: Retrained the `GradientBoostingClassifier` for the Track Risk and Weather Risk models using the generated dataset. They achieve ~87% F1 macro score.
- **Result**: The updated models are saved as `mars-track-risk.joblib` and `mars-weather-risk.joblib`.

## 2. Backend & Frontend
- The original robust Track Risk architecture (predicting risk across multiple track segments) is back online.
- The React Dashboard and Risk Evaluator sliders for track speed, acceleration, and temperature are fully functional. 
- The `simulate_sensors.py` is firing random track telemetry into the `uvicorn` backend, and the React map displays live hazard severity for segments like `SEG-101`.

## 3. Colab Training Template
- Created [track_risk_colab_template.md](file:///Users/zephyr/Dev/Rail project/MARS/notebooks/track_risk_colab_template.md).
- This template can be executed directly in Google Colab. It pulls the generated dataset seamlessly from your GitHub, trains the `mars-track-risk.joblib`, and evaluates it.

## 4. Hugging Face Deployment Package
- Updated the `huggingface_space/` directory. It contains a dedicated `app.py` Gradio application tailored for Track Risk and Weather Fusion models, complete with tabs and sliders.
- Re-copied the trained `.joblib` models into this directory so that it can be instantly deployed as a Space.

## 5. GitHub Push
- All changes were committed to `main` and pushed to your repository: `https://github.com/mrrobot-1001/MARS.git`.

### Running Locally
1. Start the backend: `PYTHONPATH=src MARS_TRACK_MODEL_PATH=artifacts/track-risk/mars-track-risk.joblib MARS_WEATHER_MODEL_PATH=artifacts/weather-risk/mars-weather-risk.joblib uvicorn mars_ml_pipeline.services.app:create_app --factory --port 8000`
2. Start the simulation data: `python scripts/simulate_sensors.py`
3. Start the frontend: `cd frontend && npm run dev`
