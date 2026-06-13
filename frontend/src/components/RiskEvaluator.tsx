import { useState, useEffect } from 'react';
import { predictTrackRisk, predictWeatherRisk, PredictionResponse } from '../utils/api';

export default function RiskEvaluator() {
  const [activeTab, setActiveTab] = useState<'track' | 'weather'>('track');
  
  // Track parameters
  const [speed, setSpeed] = useState(85);
  const [acceleration] = useState(0.2);
  const [vibrationVertical, setVibrationVertical] = useState(0.25);
  const [vibrationLateral, setVibrationLateral] = useState(0.18);
  const [trackTemp, setTrackTemp] = useState(32);
  const [segmentAge, setSegmentAge] = useState(15);
  const [maintenanceScore, setMaintenanceScore] = useState(0.75);
  const [curvature, setCurvature] = useState(2.0);
  const [maxPermittedSpeed, setMaxPermittedSpeed] = useState(110);

  // Weather parameters
  const [rainfall, setRainfall] = useState(5);
  const [visibility, setVisibility] = useState(5000);
  const [weatherTemp, setWeatherTemp] = useState(28);
  const [windSpeed, setWindSpeed] = useState(20);
  const [floodFlag, setFloodFlag] = useState(false);
  const [fogFlag, setFogFlag] = useState(false);
  const [heatFlag, setHeatFlag] = useState(false);

  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);

  // Function to run the evaluation
  const runEvaluation = async () => {
    setLoading(true);
    
    // Prep segment metadata
    const segment = {
      segment_id: 'SEG-EVAL',
      line_id: 'LINE-A',
      region: 'central',
      asset_type: 'track' as const,
      age_years: segmentAge,
      maintenance_score: maintenanceScore,
      curvature_degree: curvature,
      max_permitted_speed: maxPermittedSpeed,
    };

    // Prep sensor event (simulating single event window)
    const events = [{
      timestamp: new Date().toISOString(),
      segment_id: 'SEG-EVAL',
      train_id: 'T-SIM',
      speed,
      acceleration,
      vibration_vertical: vibrationVertical,
      vibration_lateral: vibrationLateral,
      track_temperature: trackTemp,
    }];

    try {
      if (activeTab === 'track') {
        const result = await predictTrackRisk({ segment, events });
        setPrediction(result);
      } else {
        const hazard_flags: string[] = [];
        if (floodFlag) hazard_flags.push('flood');
        if (fogFlag) hazard_flags.push('fog');
        if (heatFlag) hazard_flags.push('heat');

        const weather = {
          timestamp: new Date().toISOString(),
          region: 'central',
          rainfall_mm: rainfall,
          visibility_m: visibility,
          temperature_c: weatherTemp,
          wind_speed_kmph: windSpeed,
          hazard_flags,
        };

        const result = await predictWeatherRisk({ segment, sensor_events: events, weather });
        setPrediction(result);
      }
    } catch (err) {
      console.error('Failed to run prediction', err);
    } finally {
      setLoading(false);
    }
  };

  // Run evaluation automatically when inputs change
  useEffect(() => {
    runEvaluation();
  }, [
    activeTab, speed, acceleration, vibrationVertical, vibrationLateral,
    trackTemp, segmentAge, maintenanceScore, curvature, maxPermittedSpeed,
    rainfall, visibility, weatherTemp, windSpeed, floodFlag, fogFlag, heatFlag
  ]);

  // Gauge calculations
  const strokeDashArray = 2 * Math.PI * 50; // Radius = 50
  const riskScore = prediction?.risk_score ?? 0;
  const strokeDashOffset = strokeDashArray - (riskScore * strokeDashArray);

  return (
    <div className="evaluator-grid">
      {/* Input Sliders Card */}
      <div className="card">
        {/* Toggle Mode */}
        <div className="toggle-buttons">
          <button 
            className={`toggle-btn ${activeTab === 'track' ? 'active' : ''}`}
            onClick={() => setActiveTab('track')}
          >
            🚂 Track Sensor Risk
          </button>
          <button 
            className={`toggle-btn ${activeTab === 'weather' ? 'active' : ''}`}
            onClick={() => setActiveTab('weather')}
          >
            🌦️ Weather Fusion
          </button>
        </div>

        {/* Input sliders */}
        <div className="slider-group">
          <h4 className="explanations-header">Track Telemetry & Metadata</h4>
          
          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Train Speed</span>
              <span className="slider-val">{speed} km/h</span>
            </div>
            <input type="range" min="0" max="250" value={speed} onChange={e => setSpeed(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Max Permitted Speed</span>
              <span className="slider-val">{maxPermittedSpeed} km/h</span>
            </div>
            <input type="range" min="40" max="250" step="10" value={maxPermittedSpeed} onChange={e => setMaxPermittedSpeed(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Vibration Vertical</span>
              <span className="slider-val">{vibrationVertical} g</span>
            </div>
            <input type="range" min="0" max="2" step="0.01" value={vibrationVertical} onChange={e => setVibrationVertical(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Vibration Lateral</span>
              <span className="slider-val">{vibrationLateral} g</span>
            </div>
            <input type="range" min="0" max="2" step="0.01" value={vibrationLateral} onChange={e => setVibrationLateral(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Track Temperature</span>
              <span className="slider-val">{trackTemp} °C</span>
            </div>
            <input type="range" min="-20" max="80" value={trackTemp} onChange={e => setTrackTemp(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Segment Age</span>
              <span className="slider-val">{segmentAge} years</span>
            </div>
            <input type="range" min="0" max="70" value={segmentAge} onChange={e => setSegmentAge(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Maintenance Score</span>
              <span className="slider-val">{maintenanceScore}</span>
            </div>
            <input type="range" min="0" max="1" step="0.01" value={maintenanceScore} onChange={e => setMaintenanceScore(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Track Curvature</span>
              <span className="slider-val">{curvature} °</span>
            </div>
            <input type="range" min="0" max="10" step="0.1" value={curvature} onChange={e => setCurvature(Number(e.target.value))} />
          </div>

          {/* Conditional Weather sliders */}
          {activeTab === 'weather' && (
            <>
              <h4 className="explanations-header" style={{ marginTop: '1rem' }}>Ambient Weather Conditions</h4>
              
              <div className="slider-item">
                <div className="slider-label-row">
                  <span className="slider-name">Rainfall</span>
                  <span className="slider-val">{rainfall} mm</span>
                </div>
                <input type="range" min="0" max="200" value={rainfall} onChange={e => setRainfall(Number(e.target.value))} />
              </div>

              <div className="slider-item">
                <div className="slider-label-row">
                  <span className="slider-name">Visibility</span>
                  <span className="slider-val">{visibility} m</span>
                </div>
                <input type="range" min="50" max="15000" step="50" value={visibility} onChange={e => setVisibility(Number(e.target.value))} />
              </div>

              <div className="slider-item">
                <div className="slider-label-row">
                  <span className="slider-name">Wind Speed</span>
                  <span className="slider-val">{windSpeed} km/h</span>
                </div>
                <input type="range" min="0" max="150" value={windSpeed} onChange={e => setWindSpeed(Number(e.target.value))} />
              </div>

              <div className="slider-item">
                <div className="slider-label-row">
                  <span className="slider-name">Ambient Temperature</span>
                  <span className="slider-val">{weatherTemp} °C</span>
                </div>
                <input type="range" min="-30" max="60" value={weatherTemp} onChange={e => setWeatherTemp(Number(e.target.value))} />
              </div>

              {/* Hazard flags Checkboxes */}
              <div className="checkbox-grid" style={{ marginTop: '0.5rem' }}>
                <label className="checkbox-item">
                  <input type="checkbox" checked={floodFlag} onChange={e => setFloodFlag(e.target.checked)} />
                  🌊 Flood Warning
                </label>
                <label className="checkbox-item">
                  <input type="checkbox" checked={fogFlag} onChange={e => setFogFlag(e.target.checked)} />
                  🌫️ Fog Warning
                </label>
                <label className="checkbox-item">
                  <input type="checkbox" checked={heatFlag} onChange={e => setHeatFlag(e.target.checked)} />
                  🔥 Heat Warning
                </label>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Prediction Output Card */}
      <div className="card">
        {prediction ? (
          <div className="results-container">
            <h3 className="segment-map-title">🛡️ Safety Assessment Output</h3>
            
            {/* Risk Gauge Header */}
            <div className="gauge-row">
              <div className="gauge-canvas-wrapper">
                <svg className="gauge-svg" viewBox="0 0 120 120">
                  <circle className="gauge-bg" cx="60" cy="60" r="50" />
                  <circle 
                    className={`gauge-fill ${prediction.severity}`}
                    cx="60" 
                    cy="60" 
                    r="50" 
                    strokeDasharray={strokeDashArray}
                    strokeDashoffset={strokeDashOffset}
                  />
                </svg>
                <span className="gauge-value">{Math.round(prediction.risk_score * 100)}%</span>
              </div>
              <div className="risk-summary">
                <span className={`severity-badge ${prediction.severity}`}>
                  {prediction.severity.replace('_', ' ')}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                  Active model: {prediction.model_version}
                </span>
                <div style={{ marginTop: '0.5rem' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', display: 'block' }}>Recommended Action:</span>
                  <span className="action-val">{prediction.recommended_action}</span>
                </div>
              </div>
            </div>

            {/* Feature explanations */}
            <div>
              <h4 className="explanations-header">Risk Contribution Breakdown</h4>
              <div className="explanations-list">
                {prediction.explanation.map((item, idx) => {
                  const percent = Math.min(100, Math.max(0, (item.score / 0.35) * 100)); // normalized scale
                  return (
                    <div key={idx} className="explanation-item">
                      <div className="explanation-row">
                        <span className="explanation-factor">{item.factor}</span>
                        <span className="explanation-score">+{Math.round(item.score * 100)}%</span>
                      </div>
                      <span className="explanation-desc">{item.description}</span>
                      <div className="explanation-bar-bg">
                        <div className="explanation-bar-fill" style={{ width: `${percent}%` }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--color-text-muted)' }}>
            {loading ? 'Analyzing telemetries...' : 'Awaiting parameters...'}
          </div>
        )}
      </div>
    </div>
  );
}
