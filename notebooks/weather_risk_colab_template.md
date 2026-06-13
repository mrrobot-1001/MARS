# Weather-Track Fusion Colab Template

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
!python -m mars_ml_pipeline.training.train_weather_risk \
  --sensor-input /content/drive/MyDrive/mars/processed/tabular/track_sensor_events.csv \
  --weather-input /content/drive/MyDrive/mars/processed/tabular/weather_events.csv \
  --artifact-dir /content/drive/MyDrive/mars/artifacts/weather-risk/v0.1.0
```
