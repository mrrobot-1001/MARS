# MARS Track Risk Predictive Maintenance

Since real-world proprietary track vibration and maintenance data is not publicly available on platforms like Hugging Face, this Colab trains the GradientBoosting model using a highly realistic synthetic dataset mathematically mirroring real railway track dynamics (e.g., speed, vertical/lateral vibrations, temperature, track curvature, maintenance score).

## 1. Setup

```python
!pip install -q scikit-learn pandas numpy joblib
```

## 2. Download Dataset

```python
import pandas as pd
import urllib.request

url = "https://raw.githubusercontent.com/mrrobot-1001/MARS/main/data/track_sensor_dataset.csv"
urllib.request.urlretrieve(url, "track_sensor_dataset.csv")

print("Dataset downloaded!")
df = pd.read_csv("track_sensor_dataset.csv")
df.head()
```

## 3. Train Model

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import joblib

FEATURE_ORDER = [
    "speed_mean", "speed_std", "speed_max", "acceleration_abs_mean",
    "vibration_vertical_mean", "vibration_vertical_std",
    "vibration_lateral_mean", "vibration_lateral_std",
    "track_temperature_mean", "segment_age_years", "maintenance_score",
    "curvature_degree", "max_permitted_speed"
]

# Transform raw row data into service-level features matching the backend logic
def _to_service_features(frame: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=frame.index)
    features["speed_mean"] = frame["speed"]
    features["speed_std"] = 0.0
    features["speed_max"] = frame["speed"]
    features["acceleration_abs_mean"] = frame["acceleration"].abs()
    features["vibration_vertical_mean"] = frame["vibration_vertical"]
    features["vibration_vertical_std"] = 0.0
    features["vibration_lateral_mean"] = frame["vibration_lateral"]
    features["vibration_lateral_std"] = 0.0
    features["track_temperature_mean"] = frame["track_temperature"]
    features["segment_age_years"] = frame["age_years"]
    features["maintenance_score"] = frame["maintenance_score"]
    features["curvature_degree"] = frame["curvature_degree"]
    features["max_permitted_speed"] = frame["max_permitted_speed"]
    return features

features = _to_service_features(df)
X = features[FEATURE_ORDER]
y = df["risk_label"].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Pipeline(
    steps=[
        ("scale", StandardScaler()),
        ("classifier", GradientBoostingClassifier(random_state=42)),
    ]
)

print("Training model...")
model.fit(X_train, y_train)

print("Evaluating...")
predictions = model.predict(X_test)
print(classification_report(y_test, predictions))

# Save
joblib.dump(model, "mars-track-risk.joblib")
print("Saved to mars-track-risk.joblib")
```
