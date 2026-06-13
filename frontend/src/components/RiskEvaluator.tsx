import React, { useState, useEffect } from 'react';
import { predictEngineRisk, PredictionResponse } from '../utils/api';

export default function RiskEvaluator() {
  const [engineRpm, setEngineRpm] = useState(1200);
  const [lubOilPressure, setLubOilPressure] = useState(3.5);
  const [fuelPressure, setFuelPressure] = useState(10.0);
  const [coolantPressure, setCoolantPressure] = useState(2.5);
  const [lubOilTemp, setLubOilTemp] = useState(75);
  const [coolantTemp, setCoolantTemp] = useState(80);

  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handlePredict = async () => {
      setLoading(true);
      const res = await predictEngineRisk({
        event: {
          engine_id: 'ENG-101',
          timestamp: new Date().toISOString(),
          engine_rpm: engineRpm,
          lub_oil_pressure: lubOilPressure,
          fuel_pressure: fuelPressure,
          coolant_pressure: coolantPressure,
          lub_oil_temp: lubOilTemp,
          coolant_temp: coolantTemp,
        }
      });
      setPrediction(res);
      setLoading(false);
    };

    const debounce = setTimeout(handlePredict, 400);
    return () => clearTimeout(debounce);
  }, [engineRpm, lubOilPressure, fuelPressure, coolantPressure, lubOilTemp, coolantTemp]);

  const strokeDashArray = 2 * Math.PI * 50;
  const strokeDashOffset = prediction 
    ? strokeDashArray - (Math.max(0, Math.min(1, prediction.risk_score)) * strokeDashArray)
    : strokeDashArray;

  return (
    <div className="risk-evaluator">
      <div className="card params-card">
        <h3 className="segment-map-title">⚙️ Engine Parameter Controls</h3>
        <p className="dashboard-subtitle" style={{marginBottom: '1rem'}}>Modify engine telemetry values to test the predictive maintenance model.</p>
        
        <div className="sliders-container">
          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Engine RPM</span>
              <span className="slider-val">{engineRpm}</span>
            </div>
            <input type="range" min="0" max="3000" step="10" value={engineRpm} onChange={e => setEngineRpm(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Lubrication Oil Pressure</span>
              <span className="slider-val">{lubOilPressure} bar</span>
            </div>
            <input type="range" min="0" max="8" step="0.1" value={lubOilPressure} onChange={e => setLubOilPressure(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Fuel Pressure</span>
              <span className="slider-val">{fuelPressure} bar</span>
            </div>
            <input type="range" min="0" max="20" step="0.1" value={fuelPressure} onChange={e => setFuelPressure(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Coolant Pressure</span>
              <span className="slider-val">{coolantPressure} bar</span>
            </div>
            <input type="range" min="0" max="5" step="0.1" value={coolantPressure} onChange={e => setCoolantPressure(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Lubrication Oil Temp</span>
              <span className="slider-val">{lubOilTemp} °C</span>
            </div>
            <input type="range" min="0" max="150" step="1" value={lubOilTemp} onChange={e => setLubOilTemp(Number(e.target.value))} />
          </div>

          <div className="slider-item">
            <div className="slider-label-row">
              <span className="slider-name">Coolant Temp</span>
              <span className="slider-val">{coolantTemp} °C</span>
            </div>
            <input type="range" min="0" max="150" step="1" value={coolantTemp} onChange={e => setCoolantTemp(Number(e.target.value))} />
          </div>
        </div>
      </div>

      <div className="card">
        {prediction ? (
          <div className="results-container">
            <h3 className="segment-map-title">🛡️ Maintenance Assessment Output</h3>
            
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

            <div>
              <h4 className="explanations-header">Failure Risk Factors</h4>
              <div className="explanations-list">
                {prediction.explanation.map((item, idx) => {
                  return (
                    <div key={idx} className="explanation-item">
                      <div className="explanation-row">
                        <span className="explanation-factor">{item.feature}</span>
                      </div>
                      <span className="explanation-desc">{item.reason}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--color-text-muted)' }}>
            {loading ? 'Analyzing telemetry...' : 'Awaiting parameters...'}
          </div>
        )}
      </div>
    </div>
  );
}
