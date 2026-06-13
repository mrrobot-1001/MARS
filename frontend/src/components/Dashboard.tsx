import { useState, useEffect } from 'react';
import { checkBackendHealth } from '../utils/api';

interface Engine {
  id: string;
  type: string;
  status: 'normal' | 'caution' | 'high_risk';
  rpm: number;
  oil_pressure: number;
  coolant_temp: number;
}

interface Alert {
  id: string;
  engineId: string;
  title: string;
  desc: string;
  severity: 'normal' | 'caution' | 'high_risk';
  time: string;
}

export default function Dashboard() {
  const [backendOnline, setBackendOnline] = useState(false);
  const [activeEngine, setActiveEngine] = useState<Engine | null>(null);
  
  const [engines, setEngines] = useState<Engine[]>([
    { id: 'ENG-101', type: 'Locomotive', status: 'normal', rpm: 1200, oil_pressure: 3.5, coolant_temp: 82 },
    { id: 'ENG-102', type: 'Locomotive', status: 'high_risk', rpm: 2800, oil_pressure: 1.5, coolant_temp: 95 },
    { id: 'ENG-103', type: 'Locomotive', status: 'caution', rpm: 2100, oil_pressure: 2.1, coolant_temp: 88 },
    { id: 'ENG-104', type: 'Shunter', status: 'normal', rpm: 900, oil_pressure: 4.0, coolant_temp: 75 },
    { id: 'ENG-105', type: 'Locomotive', status: 'normal', rpm: 1150, oil_pressure: 3.8, coolant_temp: 78 },
  ]);

  const [alerts, setAlerts] = useState<Alert[]>([
    { id: 'A-001', engineId: 'ENG-102', title: 'Critical Coolant Temp', desc: 'Engine coolant has exceeded 90°C. Immediate shutdown required.', severity: 'high_risk', time: new Date().toLocaleTimeString() },
    { id: 'A-002', engineId: 'ENG-103', title: 'Low Oil Pressure', desc: 'Lubrication oil pressure dropped below 2.5 bar.', severity: 'caution', time: new Date().toLocaleTimeString() },
  ]);

  useEffect(() => {
    // Health check polling
    const pollHealth = async () => {
      const { online } = await checkBackendHealth();
      setBackendOnline(online);
    };
    pollHealth();
    const intv = setInterval(pollHealth, 5000);
    return () => clearInterval(intv);
  }, []);

  return (
    <div className="dashboard-grid">
      <div className="card full-width">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 className="dashboard-title">Fleet Operations Center</h2>
            <p className="dashboard-subtitle">Real-time predictive maintenance for train engines.</p>
          </div>
          <div className="status-badge" style={{ background: backendOnline ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)' }}>
            <div className={`pulse-dot ${backendOnline ? 'online' : 'offline'}`}></div>
            <span style={{ color: backendOnline ? 'var(--color-success)' : 'var(--color-danger)' }}>
              {backendOnline ? 'API Connected' : 'Offline Mode (Simulator)'}
            </span>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="segment-map-title">🚂 Engine Fleet Status</h3>
        <div className="segment-list">
          {engines.map(eng => (
            <div 
              key={eng.id} 
              className={`segment-card ${activeEngine?.id === eng.id ? 'active' : ''}`}
              onClick={() => setActiveEngine(eng)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: 'bold' }}>{eng.id}</span>
                <span className={`severity-badge ${eng.status}`}>{eng.status.replace('_', ' ')}</span>
              </div>
              <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                <span>RPM: {eng.rpm}</span>
                <span>Oil: {eng.oil_pressure} bar</span>
                <span>Temp: {eng.coolant_temp}°C</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 className="segment-map-title">⚠️ Active Maintenance Alerts</h3>
        <div className="alerts-list">
          {alerts.map(al => (
            <div key={al.id} className="alert-item">
              <div className="alert-icon-col">
                <span className={`alert-icon ${al.severity}`}>
                  {al.severity === 'high_risk' ? '🔴' : '🟡'}
                </span>
              </div>
              <div className="alert-content">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="alert-title">{al.title} ({al.engineId})</span>
                  <span className="alert-time">{al.time}</span>
                </div>
                <div className="alert-desc">{al.desc}</div>
              </div>
            </div>
          ))}
          {alerts.length === 0 && (
            <div style={{ color: 'var(--color-text-muted)', textAlign: 'center', marginTop: '2rem' }}>
              No active alerts.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
