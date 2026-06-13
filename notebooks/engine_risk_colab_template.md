# MARS Engine Predictive Maintenance Model Training

This notebook trains the GradientBoosting model for Engine Predictive Maintenance using the dataset from Hugging Face.

## 1. Setup

```python
!pip install -q scikit-learn pandas numpy datasets joblib
```

## 2. Download Dataset

```python
from datasets import load_dataset
import pandas as pd

print("Downloading dataset from Hugging Face...")
dataset = load_dataset("MohammedSohail/predictive-maintenance-dataset", split="train")
df = dataset.to_pandas()
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
    "Engine rpm", "Lub oil pressure", "Fuel pressure", 
    "Coolant pressure", "lub oil temp", "Coolant temp"
]

X = df[FEATURE_ORDER]
# 1 = Faulty, 0 = Good
y = 1 - df["Engine Condition"].astype(int)

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
joblib.dump(model, "mars-engine-risk.joblib")
print("Saved to mars-engine-risk.joblib")
```
