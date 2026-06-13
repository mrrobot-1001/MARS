from __future__ import annotations

from mars_ml_pipeline.recommendations import security_action
from mars_ml_pipeline.schemas import SecurityAnomalyRequest, SecurityDetection, SecurityPrediction


class AnnotationSecurityDetector:
    model_version = "annotation-security-v0"
    anomaly_labels = {"trespassing", "unattended_object", "person_on_track", "restricted_zone"}

    def predict(
        self,
        request: SecurityAnomalyRequest,
        caution_threshold: float,
        high_risk_threshold: float,
    ) -> SecurityPrediction:
        detections: list[SecurityDetection] = []
        for annotation in request.event.annotations:
            label = annotation.label.strip().lower()
            if label not in self.anomaly_labels:
                continue
            decision = security_action(annotation.confidence, caution_threshold, high_risk_threshold)
            detections.append(
                SecurityDetection(
                    anomaly_type=label,
                    bbox=annotation.bbox,
                    confidence=annotation.confidence,
                    severity=decision.severity,
                )
            )

        risk_score = max((detection.confidence for detection in detections), default=0.0)
        decision = security_action(risk_score, caution_threshold, high_risk_threshold)
        return SecurityPrediction(
            camera_id=request.event.camera_id,
            detections=detections,
            risk_score=risk_score,
            risk_class=decision.risk_class,
            severity=decision.severity,
            recommended_action=decision.recommended_action,
            model_version=self.model_version,
        )
