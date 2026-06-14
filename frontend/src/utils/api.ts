// MARS API client and simulator fallback

const API_BASE_URL = 'http://localhost:8000';

export interface RegionProfile {
  code: string;
  name: string;
  headquarters: string;
  divisions: string[];
  terrain: string;
  operating_condition: string;
  climate_hazards: string[];
  speed_factor: number;
  vibration_factor: number;
  weather_factor: number;
  maintenance_factor: number;
  max_speed_bias: number;
  rainfall_baseline_mm: number;
  temperature_baseline_c: number;
  visibility_baseline_m: number;
}

export const REGION_PROFILES: RegionProfile[] = [
  {
    code: 'NR',
    name: 'Northern Railway',
    headquarters: 'New Delhi',
    divisions: ['Delhi', 'Ambala', 'Firozpur', 'Lucknow', 'Moradabad'],
    terrain: 'Dense junctions, fog-prone plains, high passenger density',
    operating_condition: 'Winter fog, congestion, mixed-speed corridors',
    climate_hazards: ['fog', 'cold_wave', 'heat'],
    speed_factor: 0.98,
    vibration_factor: 1.05,
    weather_factor: 1.12,
    maintenance_factor: 1.03,
    max_speed_bias: 0,
    rainfall_baseline_mm: 18,
    temperature_baseline_c: 31,
    visibility_baseline_m: 4200,
  },
  {
    code: 'CR',
    name: 'Central Railway',
    headquarters: 'Mumbai CSMT',
    divisions: ['Mumbai', 'Bhusawal', 'Nagpur', 'Pune', 'Solapur'],
    terrain: 'Ghat sections, suburban density, heavy freight interfaces',
    operating_condition: 'Steep gradients, curve wear, monsoon disruption',
    climate_hazards: ['flood', 'landslide', 'heat'],
    speed_factor: 0.95,
    vibration_factor: 1.16,
    weather_factor: 1.18,
    maintenance_factor: 1.08,
    max_speed_bias: -5,
    rainfall_baseline_mm: 34,
    temperature_baseline_c: 32,
    visibility_baseline_m: 5200,
  },
  {
    code: 'WR',
    name: 'Western Railway',
    headquarters: 'Mumbai Churchgate',
    divisions: ['Mumbai Central', 'Vadodara', 'Ahmedabad', 'Ratlam', 'Rajkot', 'Bhavnagar'],
    terrain: 'Coastal belts, desert approaches, high-speed trunk routes',
    operating_condition: 'Salinity, heat, dust, long-distance express traffic',
    climate_hazards: ['heat', 'dust', 'cyclone'],
    speed_factor: 1.04,
    vibration_factor: 1.02,
    weather_factor: 1.07,
    maintenance_factor: 1.02,
    max_speed_bias: 10,
    rainfall_baseline_mm: 22,
    temperature_baseline_c: 35,
    visibility_baseline_m: 6800,
  },
  {
    code: 'ER',
    name: 'Eastern Railway',
    headquarters: 'Kolkata',
    divisions: ['Howrah', 'Sealdah', 'Asansol', 'Malda'],
    terrain: 'Deltaic plains, bridges, dense suburban operations',
    operating_condition: 'Waterlogging, bridge approaches, crowding',
    climate_hazards: ['flood', 'fog', 'cyclone'],
    speed_factor: 0.96,
    vibration_factor: 1.09,
    weather_factor: 1.2,
    maintenance_factor: 1.07,
    max_speed_bias: -5,
    rainfall_baseline_mm: 42,
    temperature_baseline_c: 31,
    visibility_baseline_m: 4700,
  },
  {
    code: 'SR',
    name: 'Southern Railway',
    headquarters: 'Chennai',
    divisions: ['Chennai', 'Tiruchirappalli', 'Madurai', 'Salem', 'Palakkad', 'Thiruvananthapuram'],
    terrain: 'Coastal sections, humid climate, hill approaches',
    operating_condition: 'Humidity, coastal corrosion, monsoon bursts',
    climate_hazards: ['flood', 'cyclone', 'heat'],
    speed_factor: 0.98,
    vibration_factor: 1.04,
    weather_factor: 1.14,
    maintenance_factor: 1.05,
    max_speed_bias: 0,
    rainfall_baseline_mm: 30,
    temperature_baseline_c: 33,
    visibility_baseline_m: 6200,
  },
  {
    code: 'NFR',
    name: 'Northeast Frontier Railway',
    headquarters: 'Maligaon',
    divisions: ['Katihar', 'Alipurduar', 'Rangiya', 'Lumding', 'Tinsukia'],
    terrain: 'Hills, forests, rivers, landslide-prone formations',
    operating_condition: 'Washouts, landslides, tight curves, remote maintenance',
    climate_hazards: ['flood', 'landslide', 'fog'],
    speed_factor: 0.88,
    vibration_factor: 1.22,
    weather_factor: 1.3,
    maintenance_factor: 1.14,
    max_speed_bias: -15,
    rainfall_baseline_mm: 58,
    temperature_baseline_c: 27,
    visibility_baseline_m: 3600,
  },
  {
    code: 'NWR',
    name: 'North Western Railway',
    headquarters: 'Jaipur',
    divisions: ['Jaipur', 'Jodhpur', 'Bikaner', 'Ajmer'],
    terrain: 'Desert, heat, sand ingress, long sparse routes',
    operating_condition: 'Thermal stress, dust, sparse emergency access',
    climate_hazards: ['heat', 'dust'],
    speed_factor: 1.02,
    vibration_factor: 1.03,
    weather_factor: 1.08,
    maintenance_factor: 1.06,
    max_speed_bias: 5,
    rainfall_baseline_mm: 8,
    temperature_baseline_c: 38,
    visibility_baseline_m: 7200,
  },
];

export function getRegionProfile(code: string): RegionProfile {
  return REGION_PROFILES.find(profile => profile.code === code) || REGION_PROFILES[1];
}

export interface PredictTrackRequest {
  segment: {
    segment_id: string;
    line_id: string;
    region: string;
    division?: string;
    asset_type: 'track' | 'bridge' | 'tunnel' | 'platform' | 'yard';
    age_years: number;
    maintenance_score: number;
    curvature_degree: number;
    max_permitted_speed: number;
  };
  events: Array<{
    timestamp: string;
    segment_id: string;
    train_id: string;
    speed: number;
    acceleration: number;
    vibration_vertical: number;
    vibration_lateral: number;
    track_temperature: number;
  }>;
}

export interface PredictWeatherRequest {
  segment: PredictTrackRequest['segment'];
  sensor_events: PredictTrackRequest['events'];
  weather: {
    timestamp: string;
    region: string;
    rainfall_mm: number;
    visibility_m: number;
    temperature_c: number;
    wind_speed_kmph: number;
    hazard_flags: string[];
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
    frame_path?: string;
    frame_url?: string;
    zone_polygon?: Array<[number, number]>;
    annotations: SecurityAnnotation[];
  };
}

export interface PredictionResponse {
  segment_id: string;
  region?: string;
  division?: string;
  regional_profile?: RegionProfile;
  risk_score: number;
  risk_class: number;
  severity: 'normal' | 'caution' | 'high_risk';
  recommended_action: string;
  explanation: Array<{
    feature?: string;
    value?: number | string;
    reason?: string;
    factor?: string;
    score?: number;
    description?: string;
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
export async function checkBackendHealth(): Promise<{ online: boolean; track_version?: string; weather_version?: string; security_version?: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(1500) });
    if (res.ok) {
      const data = await res.json();
      return {
        online: true,
        track_version: data.track_model_version,
        weather_version: data.weather_model_version,
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
    return { severity: 'high_risk', risk_class: 2, action: 'Restrict Speed' };
  } else if (score >= 0.35) {
    return { severity: 'caution', risk_class: 1, action: 'Caution Advisory' };
  }
  return { severity: 'normal', risk_class: 0, action: 'Normal Operations' };
}

export function simulateTrackRisk(req: PredictTrackRequest): PredictionResponse {
  const seg = req.segment;
  const ev = req.events[0] || { speed: 85, vibration_vertical: 0.25, vibration_lateral: 0.18, track_temperature: 32 };
  const region = getRegionProfile(seg.region);
  
  const speedRatio = clamp((ev.speed / Math.max(seg.max_permitted_speed, 1.0)) / region.speed_factor);
  const vibration = clamp((ev.vibration_vertical * 0.55 + ev.vibration_lateral * 0.45) * region.vibration_factor);
  const age = clamp(seg.age_years / 60.0);
  const maintenanceRisk = clamp((1.0 - clamp(seg.maintenance_score)) * region.maintenance_factor);
  const heat = clamp((ev.track_temperature - 35.0) / 35.0);
  const curve = clamp(seg.curvature_degree / 8.0);
  
  const score = clamp(
    speedRatio * 0.18 +
    vibration * 0.30 +
    age * 0.15 +
    maintenanceRisk * 0.22 +
    heat * 0.08 +
    curve * 0.07
  );
  
  const cls = classifyScore(score);
  
  return {
    segment_id: seg.segment_id,
    region: region.code,
    division: seg.division || region.divisions[0],
    regional_profile: region,
    risk_score: score,
    risk_class: cls.risk_class,
    severity: cls.severity,
    recommended_action: cls.action,
    explanation: [
      { factor: 'Speed Ratio', score: speedRatio * 0.18, description: `Speed is ${Math.round(ev.speed)} km/h vs permitted ${seg.max_permitted_speed} km/h` },
      { factor: 'Vibration Profile', score: vibration * 0.30, description: `Vibration vertical: ${ev.vibration_vertical}g, lateral: ${ev.vibration_lateral}g` },
      { factor: 'Segment Age', score: age * 0.15, description: `Segment is ${seg.age_years} years old` },
      { factor: 'Maintenance Status', score: maintenanceRisk * 0.22, description: `Maintenance score is ${seg.maintenance_score}` },
      { factor: 'Track Temperature', score: heat * 0.08, description: `Temperature is ${ev.track_temperature}°C` },
      { factor: 'Curvature degree', score: curve * 0.07, description: `Curvature is ${seg.curvature_degree}°` },
      { factor: `${region.code} regional profile`, score: Math.max(0, region.vibration_factor - 1) * 0.18, description: region.operating_condition }
    ],
    model_version: 'offline-simulator-v1'
  };
}

export function simulateWeatherRisk(req: PredictWeatherRequest): PredictionResponse {
  const seg = req.segment;
  const ev = req.sensor_events[0] || { speed: 85, vibration_vertical: 0.25, vibration_lateral: 0.18, track_temperature: 32 };
  const w = req.weather;
  const region = getRegionProfile(seg.region);
  
  const trackResponse = simulateTrackRisk({ segment: seg, events: [ev] });
  const trackBase = trackResponse.risk_score;
  
  const rainfall = clamp((w.rainfall_mm / 120.0) * region.weather_factor);
  const lowVis = clamp((1200.0 - w.visibility_m) / 1200.0);
  const wind = clamp(w.wind_speed_kmph / 120.0);
  const heat = clamp((w.temperature_c - 38.0) / 18.0);
  
  let flagsCount = 0;
  if (w.hazard_flags.includes('flood')) flagsCount++;
  if (w.hazard_flags.includes('fog')) flagsCount++;
  if (w.hazard_flags.includes('heat')) flagsCount++;
  const flags = clamp((flagsCount / 2.0) * region.weather_factor);
  
  const score = clamp(
    trackBase * 0.42 +
    rainfall * 0.22 +
    lowVis * 0.14 +
    wind * 0.08 +
    heat * 0.06 +
    flags * 0.08
  );
  
  const cls = classifyScore(score);
  
  return {
    segment_id: seg.segment_id,
    region: region.code,
    division: seg.division || region.divisions[0],
    regional_profile: region,
    risk_score: score,
    risk_class: cls.risk_class,
    severity: cls.severity,
    recommended_action: cls.action,
    explanation: [
      { factor: 'Track Base Risk', score: trackBase * 0.42, description: `Track structural risk contribution is ${Math.round(trackBase * 100)}%` },
      { factor: 'Rainfall intensity', score: rainfall * 0.22, description: `Rainfall is ${w.rainfall_mm} mm` },
      { factor: 'Visibility restriction', score: lowVis * 0.14, description: `Visibility is ${w.visibility_m} m` },
      { factor: 'Wind Speed force', score: wind * 0.08, description: `Wind speed is ${w.wind_speed_kmph} km/h` },
      { factor: 'Extreme Heat risk', score: heat * 0.06, description: `Ambient temperature is ${w.temperature_c}°C` },
      { factor: 'Hazard Flags active', score: flags * 0.08, description: `Active warnings: ${w.hazard_flags.join(', ') || 'None'}` }
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
export async function predictTrackRisk(req: PredictTrackRequest): Promise<PredictionResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/track-risk/predict`, {
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
  return simulateTrackRisk(req);
}

export async function predictWeatherRisk(req: PredictWeatherRequest): Promise<PredictionResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/weather-risk/predict`, {
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
  return simulateWeatherRisk(req);
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
