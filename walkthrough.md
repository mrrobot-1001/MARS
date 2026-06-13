# 🚂 Engine Predictive Maintenance Refactor & Deployment

We have successfully pivoted the MARS project to focus on **Engine Predictive Maintenance**. The system is fully operational locally and has been pushed to GitHub. Here is a summary of the achievements:

## 1. Machine Learning Model Training
- **Dataset**: Downloaded `MohammedSohail/predictive-maintenance-dataset` from Hugging Face.
- **Model Training**: Created `src/mars_ml_pipeline/training/train_engine_risk.py` to train a Scikit-Learn `GradientBoostingClassifier` on engine telemetries (RPM, lubrication oil pressure/temp, coolant pressure/temp, etc.).
- **Result**: The model is saved as `mars-engine-risk.joblib` with an F1-Macro score of ~0.59 on the test split.

## 2. Backend API Refactor
- Rewrote `schemas.py` and `features.py` to accept `EngineRiskRequest` with the corresponding engine telemetry structure instead of track vibrations.
- Reconfigured `app.py` FastAPI server to expose a unified `/engine-risk/predict` endpoint.
- Adapted the Explanation generation to evaluate factors like excessive Coolant Temperature and low Lubrication Oil Pressure.

## 3. Frontend Dashboard & Simulator Updates
- **API integration (`api.ts`)**: Replaced all track logic with the engine risk endpoints. Included a mathematical offline fallback if the API disconnects.
- **`Dashboard.tsx`**: Displays a Live Fleet map with locomotives (e.g., ENG-101, ENG-102) and active alerts.
- **`RiskEvaluator.tsx`**: Replaced vibration and speed sliders with RPM, Pressure, and Temperature sliders for engine simulation.
- **`simulate_sensors.py`**: Refactored the Python script to stream random telemetry vectors for the active engines into the FastAPI endpoint continuously.

## 4. Colab Training Template
- Created [engine_risk_colab_template.md](file:///Users/zephyr/Dev/Rail project/MARS/notebooks/engine_risk_colab_template.md).
- This template can be executed directly in Google Colab to download the dataset, train the `mars-engine-risk.joblib`, and evaluate it seamlessly.

## 5. Hugging Face Deployment Package
- Created the `huggingface_space/` directory containing a dedicated `app.py` Gradio application tailored for the Engine Risk Model.
- Included the required `README.md` metadata blocks and `requirements.txt`.
- Copied the trained `.joblib` model into this directory so that it can be instantly deployed as a Space.

## 6. GitHub Push
- All changes were committed to `main`.
- Successfully pushed the codebase to your repository: `https://github.com/mrrobot-1001/MARS.git`.

### Running Locally
1. Start the backend: `python src/mars_ml_pipeline/services/app.py`
2. Start the simulation data: `python scripts/simulate_sensors.py`
3. Start the frontend: `cd frontend && npm run dev`
