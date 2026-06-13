# Track Risk Colab Template

```python
!pip install pandas scikit-learn joblib pyyaml
!git clone https://github.com/your-org/mars-ml-pipeline.git
%cd mars-ml-pipeline
!pip install -e .
```

```python
from google.colab import drive
drive.mount('/content/drive')
```

```python
!python -m mars_ml_pipeline.training.train_track_risk \
  --input /content/drive/MyDrive/mars/processed/tabular/track_sensor_events.csv \
  --artifact-dir /content/drive/MyDrive/mars/artifacts/track-risk/v0.1.0
```
