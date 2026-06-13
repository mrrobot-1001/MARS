# Security Anomaly Colab Template

Phase 1 security uses a pretrained detector and a small manually labeled station-like dataset.

Recommended workflow:

1. Label frames in CVAT or Label Studio.
2. Export YOLO format labels.
3. Fine-tune a small YOLO model in Colab.
4. Export ONNX or TorchScript.
5. Register a deployment card with input size, classes, mAP/F1, and severity mapping.

```python
!pip install ultralytics
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model.train(data="/content/drive/MyDrive/mars/security/data.yaml", epochs=25, imgsz=640)
model.export(format="onnx")
```
