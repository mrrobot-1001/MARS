import { useState, useEffect } from 'react';
import { checkBackendHealth } from '../utils/api';

interface Segment {
  id: string;
  line: string;
  region: string;
  status: 'normal' | 'caution' | 'high_risk';
  vibration: number;
  speed: number;
  temp: number;
  maintenance: number;
}

interface Alert {
  id: string;
  segmentId: string;
  title: string;
  desc: string;
  severity: 'normal' | 'caution' | 'high_risk';
  time: string;
}

export default function Dashboard() {
  const [backendOnline, setBackendOnline] = useState(false);
  const [activeSegment, setActiveSegment] = useState<Segment | null>(null);
  
  // Seed segments data
  const [segments, setSegments] = useState<Segment[]>([
    { id: 'SEG-001', line: 'Northern Link', region: 'north', status: 'normal', vibration: 0.22, speed: 105, temp: 32.5, maintenance: 0.82 },
    { id: 'SEG-002', line: 'Northern Link', region: 'north', status: 'caution', vibration: 0.65, speed: 115, temp: 38.0, maintenance: 0.61 },
    { id: 'SEG-003', line: 'Western Trunk', region: 'west', status: 'normal', vibration: 0.18, speed: 85, temp: 29.2, maintenance: 0.91 },
    { id: 'SEG-004', line: 'Western Trunk', region: 'west', status: 'high_risk', vibration: 0.95, speed: 135, temp: 44.8, maintenance: 0.35 },
    { id: 'SEG-005', line: 'Southern Line', region: 'south', status: 'normal', vibration: 0.28, speed: 90, temp: 35.1, maintenance: 0.76 },
    { id: 'SEG-006', line: 'Southern Line', region: 'south', status: 'normal', vibration: 0.31, speed: 88, temp: 34.0, maintenance: 0.74 },
    { id: 'SEG-007', line: 'Eastern Express', region: 'east', status: 'caution', vibration: 0.58, speed: 110, temp: 36.5, maintenance: 0.52 },
    { id: 'SEG-008', line: 'Eastern Express', region: 'east', status: 'normal', vibration: 0.25, speed: 95, temp: 31.0, maintenance: 0.88 },
  ]);

  // Seed alerts
  const [alerts, setAlerts] = useState<Alert[]>([
    { id: '1', segmentId: 'SEG-004', title: 'Critical Vibration Peak', desc: 'Vibration reached 0.95g, speed exceeds permitted speed limit', severity: 'high_risk', time: '12:24:15' },
    { id: '2', segmentId: 'SEG-002', title: 'Caution Speed Advisory', desc: 'Slightly high track vibration profile detected', severity: 'caution', time: '12:21:40' },
    { id: '3', segmentId: 'SEG-007', title: 'Maintenance Overdue Warning', desc: 'Track segment age exceeds 45 years with low maintenance score', severity: 'caution', time: '12:15:10' },
    { id: '4', segmentId: 'SEG-003', title: 'Standard Maintenance Log', desc: 'Periodic check completed, status stable', severity: 'normal', time: '12:02:00' },
  ]);

  useEffect(() => {
    // Check backend health
    checkBackendHealth().then(status => setBackendOnline(status.online));

    // Simulate real-time data changes
    const interval = setInterval(() => {
      setSegments(prev => prev.map(s => {
        if (Math.random() > 0.7) {
          // Add small fluctuations
          const speedChange = Math.round((Math.random() - 0.5) * 6);
          const vibChange = parseFloat(((Math.random() - 0.5) * 0.08).toFixed(2));
          const tempChange = parseFloat(((Math.random() - 0.5) * 1.5).toFixed(1));
          
          const newSpeed = Math.max(0, s.speed + speedChange);
          const newVib = Math.max(0.02, parseFloat((s.vibration + vibChange).toFixed(2)));
          const newTemp = Math.max(-10, parseFloat((s.temp + tempChange).toFixed(1)));
          
          let status: 'normal' | 'caution' | 'high_risk' = 'normal';
          if (newVib > 0.8 || newSpeed > 130) {
            status = 'high_risk';
          } else if (newVib > 0.5 || newSpeed > 110) {
            status = 'caution';
          }

          const updated = {
            ...s,
            speed: newSpeed,
            vibration: newVib,
            temp: newTemp,
            status,
          };

          // If the segment status escalated to caution/high, add an alert
          if (status !== s.status && status !== 'normal') {
            const timeStr = new Date().toTimeString().split(' ')[0];
            setAlerts(prevAlerts => [
              {
                id: Math.random().toString(),
                segmentId: s.id,
                title: status === 'high_risk' ? 'High Risk Status Threshold' : 'Caution Status Warning',
                desc: `Segment ${s.id} vibration: ${newVib}g, speed: ${newSpeed}km/h`,
                severity: status,
                time: timeStr,
              },
              ...prevAlerts.slice(0, 8) // Limit to last 9 alerts
            ]);
          }

          if (activeSegment && activeSegment.id === s.id) {
            setActiveSegment(updated);
          }

          return updated;
        }
        return s;
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, [activeSegment]);

  const stats = {
    total: segments.length,
    normal: segments.filter(s => s.status === 'normal').length,
    caution: segments.filter(s => s.status === 'caution').length,
    high_risk: segments.filter(s => s.status === 'high_risk').length,
  };

  return (
    <div className="dashboard-grid">
      <div className="dashboard-main">
        {/* Network Map Card */}
        <div className="card segment-map-container">
          <div className="camera-header">
            <h3 className="segment-map-title">🚂 Railway Network Node Monitor</h3>
            <span style={{ fontSize: '0.8rem', color: backendOnline ? 'var(--status-normal)' : 'var(--color-text-muted)' }}>
              {backendOnline ? '● Backend API Connected' : '○ Standalone Simulator Mode'}
            </span>
          </div>

          <div className="railway-network-map">
            <div className="railway-track-line"></div>
            <div className="railway-segments-wrapper">
              {segments.map((seg) => (
                <div 
                  key={seg.id}
                  className={`map-node ${seg.status}`}
                  onClick={() => setActiveSegment(seg)}
                  style={{ transform: activeSegment?.id === seg.id ? 'scale(1.4)' : 'none' }}
                >
                  <span className="map-node-tooltip">{seg.id} ({seg.status.toUpperCase()})</span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Stats Grid */}
          <div className="performance-grid" style={{ marginTop: '0.5rem' }}>
            <div className="metric-card" style={{ padding: '0.75rem 1rem' }}>
              <span className="metric-title" style={{ fontSize: '0.7rem' }}>Total Monitored Segments</span>
              <span className="metric-value" style={{ fontSize: '1.5rem' }}>{stats.total}</span>
            </div>
            <div className="metric-card" style={{ padding: '0.75rem 1rem', borderLeft: '3px solid var(--status-normal)' }}>
              <span className="metric-title" style={{ fontSize: '0.7rem' }}>Normal Status</span>
              <span className="metric-value" style={{ fontSize: '1.5rem', color: 'var(--status-normal)' }}>{stats.normal}</span>
            </div>
            <div className="metric-card" style={{ padding: '0.75rem 1rem', borderLeft: '3px solid var(--status-caution)' }}>
              <span className="metric-title" style={{ fontSize: '0.7rem' }}>Caution advisories</span>
              <span className="metric-value" style={{ fontSize: '1.5rem', color: 'var(--status-caution)' }}>{stats.caution}</span>
            </div>
            <div className="metric-card" style={{ padding: '0.75rem 1rem', borderLeft: '3px solid var(--status-high)' }}>
              <span className="metric-title" style={{ fontSize: '0.7rem' }}>High-Risk Restrictions</span>
              <span className="metric-value" style={{ fontSize: '1.5rem', color: 'var(--status-high)' }}>{stats.high_risk}</span>
            </div>
          </div>
        </div>

        {/* Selected Segment Detail Card */}
        {activeSegment ? (
          <div className="card" style={{ animation: 'pulse 0.3s ease-out' }}>
            <div className="camera-header" style={{ marginBottom: '1rem' }}>
              <h4 className="camera-title" style={{ color: 'var(--color-brand-cyan)' }}>📊 Segment Details: {activeSegment.id}</h4>
              <button className="camera-btn" onClick={() => setActiveSegment(null)}>Close</button>
            </div>
            <div className="performance-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
              <div className="metric-card">
                <span className="metric-title">Operating Speed</span>
                <span className="metric-value" style={{ fontSize: '1.5rem' }}>{activeSegment.speed} km/h</span>
              </div>
              <div className="metric-card">
                <span className="metric-title">Track Vibration</span>
                <span className="metric-value" style={{ fontSize: '1.5rem' }}>{activeSegment.vibration} g</span>
              </div>
              <div className="metric-card">
                <span className="metric-title">Temperature</span>
                <span className="metric-value" style={{ fontSize: '1.5rem' }}>{activeSegment.temp} °C</span>
              </div>
              <div className="metric-card">
                <span className="metric-title">Safety Status</span>
                <span className={`severity-badge ${activeSegment.status}`} style={{ margin: '0.2rem 0', fontSize: '0.7rem' }}>
                  {activeSegment.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100px', color: 'var(--color-text-muted)' }}>
            <span>Click any node in the Railway Node Monitor to inspect live telemetry</span>
          </div>
        )}
      </div>

      {/* Side Alert Panel */}
      <div className="card">
        <h3 className="segment-map-title" style={{ marginBottom: '1rem' }}>🔔 Live Safety Alerts</h3>
        <div className="alerts-list">
          {alerts.map(alert => (
            <div key={alert.id} className={`alert-item ${alert.severity}`}>
              <div className="alert-meta">
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                  <span className="alert-title">{alert.title}</span>
                  <span className="alert-time">{alert.time}</span>
                </div>
                <span className="alert-desc">{alert.desc}</span>
                <span style={{ fontSize: '0.65rem', color: 'var(--color-brand-cyan)', marginTop: '0.35rem', fontFamily: 'var(--font-mono)' }}>
                  SEGMENT REF: {alert.segmentId}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
