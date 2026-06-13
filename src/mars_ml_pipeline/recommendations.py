from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeverityDecision:
    risk_class: int
    severity: str
    recommended_action: str


def classify_score(score: float, caution: float, high_risk: float) -> SeverityDecision:
    if score >= high_risk:
        return SeverityDecision(2, "high_risk", "restrict_speed")
    if score >= caution:
        return SeverityDecision(1, "caution", "caution")
    return SeverityDecision(0, "normal", "normal")


def security_action(score: float, caution: float, high_risk: float) -> SeverityDecision:
    if score >= high_risk:
        return SeverityDecision(2, "high_risk", "dispatch_security")
    if score >= caution:
        return SeverityDecision(1, "caution", "review_camera")
    return SeverityDecision(0, "normal", "normal")
