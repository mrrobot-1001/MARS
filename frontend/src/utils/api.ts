// MARS API client and simulator fallback

const API_BASE_URL = 'http://localhost:8000';

export interface PredictEngineRequest {
  event: {
    engine_id: string;
    timestamp: string;
    engine_rpm: number;
    lub_oil_pressure: number;
    fuel_pressure: number;
    coolant_pressure: number;
    lub_oil_temp: number;
    coolant_temp: number;
  };
}

export interface SecurityAnnotation {
  label: string;
  bbox: {
    x_min: number;
    y_min: number;
    x_max: number;
    y_max: number;
  };
  confidence: number;
}

export interface PredictSecurityRequest {
  event: {
    camera_id: string;
    timestamp: string;
    frame_url?: string;
    zone_polygon?: Array<[number, number]>;
    annotations: SecurityAnnotation[];
  };
}

export interface PredictionResponse {
  segment_id: string;
  risk_score: number;
  risk_class: number;
  severity: 'normal' | 'caution' | 'high_risk';
  recommended_action: string;
  explanation: Array<{
    factor?: string;
    feature?: string;
    score?: number;
    value?: number | string;
    description?: string;
    reason?: string;
  }>;
  model_version: string;
}

export interface SecurityResponse {
  camera_id: string;
  detections: Array<{
    anomaly_type: string;
    bbox: {
      x_min: number;
      y_min: number;
      x_max: number;
      y_max: number;
    };
    confidence: number;
    severity: 'normal' | 'caution' | 'high_risk';
  }>;
  risk_score: number;
  risk_class: number;
  severity: 'normal' | 'caution' | 'high_risk';
  recommended_action: string;
  model_version: string;
}

// Check if backend FastAPI is online
export async function checkBackendHealth(): Promise<{ online: boolean; engine_version?: string; security_version?: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(1500) });
    if (res.ok) {
      const data = await res.json();
      return {
        online: true,
        engine_version: data.engine_model_version,
        security_version: data.security_model_version,
      };
    }
  } catch {
    // Ignore error, return offline state
  }
  return { online: false };
}

// Local simulation logic (mathematical mirror of backend models for offline usability)
function clamp(val: number, min = 0.0, max = 1.0): number {
  return Math.max(min, Math.min(max, val));
}

function classifyScore(score: number): { severity: 'normal' | 'caution' | 'high_risk'; risk_class: number; action: string } {
  if (score >= 0.68) {
    return { severity: 'high_risk', risk_class: 2, action: 'Stop Engine Immediately' };
  } else if (score >= 0.35) {
    return { severity: 'caution', risk_class: 1, action: 'Schedule Maintenance' };
  }
  return { severity: 'normal', risk_class: 0, action: 'Normal Operations' };
}

export function simulateEngineRisk(req: PredictEngineRequest): PredictionResponse {
  const ev = req.event;
  
  // Dummy math logic for offline simulation
  const tempRisk = clamp((ev.coolant_temp - 80) / 20.0);
  const pressureRisk = clamp((3.0 - ev.lub_oil_pressure) / 2.0);
  const rpmRisk = clamp(ev.engine_rpm / 1500.0);
  
  const score = clamp(tempRisk * 0.4 + pressureRisk * 0.4 + rpmRisk * 0.2);
  const cls = classifyScore(score);
  
  return {
    segment_id: ev.engine_id,
    risk_score: score,
    risk_class: cls.risk_class,
    severity: cls.severity,
    recommended_action: cls.action,
    explanation: [
      { feature: 'Coolant temp', value: ev.coolant_temp, reason: `Coolant temp at ${ev.coolant_temp}°C` },
      { feature: 'Lub oil pressure', value: ev.lub_oil_pressure, reason: `Oil pressure at ${ev.lub_oil_pressure} bar` },
      { feature: 'Engine rpm', value: ev.engine_rpm, reason: `RPM at ${ev.engine_rpm}` }
    ],
    model_version: 'offline-simulator-v1'
  };
}

export function simulateSecurityAnomaly(req: PredictSecurityRequest): SecurityResponse {
  const ev = req.event;
  
  const detections = ev.annotations.map(ann => {
    let severity: 'normal' | 'caution' | 'high_risk' = 'normal';
    if (ann.confidence >= 0.75) {
      severity = 'high_risk';
    } else if (ann.confidence >= 0.4) {
      severity = 'caution';
    }
    return {
      anomaly_type: ann.label,
      bbox: ann.bbox,
      confidence: ann.confidence,
      severity
    };
  });
  
  const maxConf = Math.max(...ev.annotations.map(a => a.confidence), 0);
  
  let severity: 'normal' | 'caution' | 'high_risk' = 'normal';
  let action = 'Normal Operations';
  let riskClass = 0;
  
  if (maxConf >= 0.7) {
    severity = 'high_risk';
    riskClass = 2;
    action = 'Restrict Speed & Notify Security';
  } else if (maxConf >= 0.4) {
    severity = 'caution';
    riskClass = 1;
    action = 'Caution Advisory & Monitor Camera';
  }
  
  return {
    camera_id: ev.camera_id,
    detections,
    risk_score: maxConf,
    risk_class: riskClass,
    severity,
    recommended_action: action,
    model_version: 'offline-simulator-v1'
  };
}

// Client predict functions
export async function predictEngineRisk(req: PredictEngineRequest): Promise<PredictionResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/engine-risk/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('FastAPI backend request failed, running offline simulator.', err);
  }
  return simulateEngineRisk(req);
}

export async function predictSecurityAnomaly(req: PredictSecurityRequest): Promise<SecurityResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/security-anomaly/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('FastAPI backend request failed, running offline simulator.', err);
  }
  return simulateSecurityAnomaly(req);
}
