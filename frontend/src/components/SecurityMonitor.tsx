import { useState, useEffect } from 'react';
import { predictSecurityAnomaly, SecurityResponse, SecurityAnnotation } from '../utils/api';

interface CameraTemplate {
  name: string;
  annotations: SecurityAnnotation[];
}

export default function SecurityMonitor() {
  const [selectedCamera, setSelectedCamera] = useState<'CAM-101' | 'CAM-102' | 'CAM-103'>('CAM-101');
  const [activeTemplate, setActiveTemplate] = useState<string>('clear');
  const [confidenceInput, setConfidenceInput] = useState(0.85);
  
  const [customBbox, setCustomBbox] = useState<{ x_min: number; y_min: number; x_max: number; y_max: number } | null>(null);
  const [customLabel, setCustomLabel] = useState<string>('trespassing');
  
  const [prediction, setPrediction] = useState<SecurityResponse | null>(null);
  const [, setLoading] = useState(false);

  // Predefined templates
  const templates: Record<string, CameraTemplate> = {
    clear: {
      name: 'Standard Operations (Clear)',
      annotations: []
    },
    trespasser: {
      name: 'Intruder detected on tracks',
      annotations: [
        {
          label: 'person_on_track',
          bbox: { x_min: 42, y_min: 35, x_max: 58, y_max: 85 },
          confidence: confidenceInput
        }
      ]
    },
    unattended: {
      name: 'Unattended parcel left on platform',
      annotations: [
        {
          label: 'unattended_object',
          bbox: { x_min: 22, y_min: 60, x_max: 38, y_max: 80 },
          confidence: confidenceInput
        }
      ]
    },
    restricted: {
      name: 'Restricted area perimeter breach',
      annotations: [
        {
          label: 'restricted_zone',
          bbox: { x_min: 68, y_min: 20, x_max: 95, y_max: 60 },
          confidence: confidenceInput
        }
      ]
    }
  };

  const runSecurityPrediction = async () => {
    setLoading(true);
    let annotations: SecurityAnnotation[] = [];
    
    if (activeTemplate === 'custom' && customBbox) {
      annotations = [
        {
          label: customLabel,
          bbox: customBbox,
          confidence: confidenceInput
        }
      ];
    } else if (templates[activeTemplate]) {
      annotations = templates[activeTemplate].annotations.map(ann => ({
        ...ann,
        confidence: confidenceInput // dynamically bind confidence slider
      }));
    }

    try {
      const response = await predictSecurityAnomaly({
        event: {
          camera_id: selectedCamera,
          timestamp: new Date().toISOString(),
          annotations
        }
      });
      setPrediction(response);
    } catch (err) {
      console.error('Failed to predict security anomaly', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSecurityPrediction();
  }, [selectedCamera, activeTemplate, confidenceInput, customBbox, customLabel]);

  // Click on camera viewport to draw box
  const handleViewportClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    if (!customBbox || activeTemplate !== 'custom') {
      // Start drawing
      setCustomBbox({ x_min: Math.round(x), y_min: Math.round(y), x_max: Math.min(100, Math.round(x + 15)), y_max: Math.min(100, Math.round(y + 25)) });
      setActiveTemplate('custom');
    } else {
      // Clear custom
      setCustomBbox(null);
      setActiveTemplate('clear');
    }
  };

  return (
    <div className="security-monitor-grid">
      {/* Viewport Camera Card */}
      <div className="card camera-feed-card">
        <div className="camera-header">
          <h3 className="camera-title">📹 live security monitor: {selectedCamera}</h3>
          <div className="camera-actions">
            <button className={`camera-btn ${selectedCamera === 'CAM-101' ? 'active' : ''}`} onClick={() => setSelectedCamera('CAM-101')}>Cam-101 (Crossing)</button>
            <button className={`camera-btn ${selectedCamera === 'CAM-102' ? 'active' : ''}`} onClick={() => setSelectedCamera('CAM-102')}>Cam-102 (Tunnel)</button>
            <button className={`camera-btn ${selectedCamera === 'CAM-103' ? 'active' : ''}`} onClick={() => setSelectedCamera('CAM-103')}>Cam-103 (Platform)</button>
          </div>
        </div>

        {/* Viewport canvas */}
        <div className="canvas-viewport" onClick={handleViewportClick} style={{ cursor: 'crosshair' }}>
          {/* Cyberpunk SVG vector landscape grid instead of placeholder image */}
          <svg width="100%" height="100%" style={{ background: '#070a14', display: 'block' }}>
            <defs>
              <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#080e1e" />
                <stop offset="100%" stopColor="#0a1226" />
              </linearGradient>
              <linearGradient id="laserGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
                <stop offset="50%" stopColor="#06b6d4" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
              </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#skyGrad)" />
            
            {/* Draw railway track perspective lines */}
            <path d="M 150 180 L 0 360" stroke="#1e293b" strokeWidth="2" />
            <path d="M 490 180 L 640 360" stroke="#1e293b" strokeWidth="2" />
            
            {/* Main tracks */}
            <path d="M 280 180 L 160 360" stroke="#475569" strokeWidth="4" />
            <path d="M 360 180 L 480 360" stroke="#475569" strokeWidth="4" />
            
            {/* Ties / sleepers */}
            <line x1="270" y1="200" x2="370" y2="200" stroke="#334155" strokeWidth="3" />
            <line x1="250" y1="230" x2="390" y2="230" stroke="#334155" strokeWidth="4" />
            <line x1="225" y1="265" x2="415" y2="265" stroke="#334155" strokeWidth="5" />
            <line x1="195" y1="305" x2="445" y2="305" stroke="#334155" strokeWidth="6" />
            <line x1="160" y1="350" x2="480" y2="350" stroke="#334155" strokeWidth="7" />

            {/* Platform indicator lines (if platform camera) */}
            {selectedCamera === 'CAM-103' && (
              <polygon points="0,220 230,180 140,360 0,360" fill="rgba(37,99,235,0.06)" stroke="rgba(37,99,235,0.15)" strokeWidth="1" />
            )}

            {/* Radar / Scanning Grid overlay */}
            <line x1="0" y1="120" x2="640" y2="120" stroke="url(#laserGrad)" strokeWidth="3" opacity="0.4" />
            <circle cx="320" cy="180" r="140" fill="none" stroke="rgba(6,182,212,0.05)" strokeWidth="1" />
            <circle cx="320" cy="180" r="80" fill="none" stroke="rgba(6,182,212,0.03)" strokeWidth="1" />
          </svg>

          {/* Render Bounding Boxes */}
          {prediction?.detections.map((det, idx) => (
            <div 
              key={idx}
              className={`bbox-label ${det.severity}`}
              style={{
                left: `${det.bbox.x_min}%`,
                top: `${det.bbox.y_min}%`,
                width: `${det.bbox.x_max - det.bbox.x_min}%`,
                height: `${det.bbox.y_max - det.bbox.y_min}%`
              }}
            >
              <span className="bbox-text">
                {det.anomaly_type.toUpperCase()} ({Math.round(det.confidence * 100)}%)
              </span>
            </div>
          ))}

          {/* Scanning lines */}
          <div style={{
            position: 'absolute',
            left: 0,
            width: '100%',
            height: '2px',
            background: 'rgba(6, 182, 212, 0.4)',
            boxShadow: '0 0 10px rgba(6, 182, 212, 0.8)',
            animation: 'pulse 3s infinite linear',
            top: '40%'
          }}></div>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
          * Click anywhere inside the feed to draw a custom bounding box.
        </span>
      </div>

      {/* Control panel and output */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <h3 className="segment-map-title">⚙️ Anomaly Simulation controls</h3>

        {/* Templates Selection */}
        <div className="slider-item">
          <span className="slider-name" style={{ fontSize: '0.85rem' }}>Simulation Presets</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.25rem' }}>
            <button className={`toggle-btn ${activeTemplate === 'clear' ? 'active' : ''}`} style={{ textAlign: 'left', padding: '0.5rem 0.75rem' }} onClick={() => setActiveTemplate('clear')}>
              🟢 Clear View (Normal)
            </button>
            <button className={`toggle-btn ${activeTemplate === 'trespasser' ? 'active' : ''}`} style={{ textAlign: 'left', padding: '0.5rem 0.75rem' }} onClick={() => setActiveTemplate('trespasser')}>
              🔴 Person on track (High Risk)
            </button>
            <button className={`toggle-btn ${activeTemplate === 'restricted' ? 'active' : ''}`} style={{ textAlign: 'left', padding: '0.5rem 0.75rem' }} onClick={() => setActiveTemplate('restricted')}>
              🟡 restricted area intrusion (Caution)
            </button>
            <button className={`toggle-btn ${activeTemplate === 'unattended' ? 'active' : ''}`} style={{ textAlign: 'left', padding: '0.5rem 0.75rem' }} onClick={() => setActiveTemplate('unattended')}>
              🟡 Unattended object (Caution)
            </button>
          </div>
        </div>

        {/* Custom drawing controls */}
        {activeTemplate === 'custom' && (
          <div className="slider-item" style={{ background: 'rgba(255,255,255,0.02)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <span className="slider-name" style={{ fontSize: '0.8rem', color: 'var(--color-brand-cyan)' }}>✏️ Custom Bounding Box Drawn</span>
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
              <select 
                value={customLabel} 
                onChange={e => setCustomLabel(e.target.value)}
                style={{ background: '#1f2937', color: '#fff', border: '1px solid var(--border-color)', borderRadius: '4px', padding: '0.25rem', fontSize: '0.8rem' }}
              >
                <option value="trespassing">trespassing</option>
                <option value="person_on_track">person_on_track</option>
                <option value="unattended_object">unattended_object</option>
                <option value="restricted_zone">restricted_zone</option>
              </select>
              <button className="camera-btn" onClick={() => { setCustomBbox(null); setActiveTemplate('clear'); }}>Clear Box</button>
            </div>
          </div>
        )}

        {/* Confidence slider */}
        <div className="slider-item">
          <div className="slider-label-row">
            <span className="slider-name">Detector Confidence</span>
            <span className="slider-val">{Math.round(confidenceInput * 100)}%</span>
          </div>
          <input type="range" min="0.1" max="1.0" step="0.01" value={confidenceInput} onChange={e => setConfidenceInput(Number(e.target.value))} />
        </div>

        {/* Output prediction card */}
        {prediction && (
          <div className="results-container" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem', marginTop: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className={`severity-badge ${prediction.severity}`}>
                {prediction.severity.replace('_', ' ')}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                {prediction.model_version}
              </span>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Composite Risk Score:</span>
              <span className="metric-value" style={{ fontSize: '1.75rem', fontFamily: 'var(--font-mono)' }}>
                {(prediction.risk_score * 100).toFixed(1)}%
              </span>
            </div>

            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', display: 'block' }}>Recommended Action:</span>
              <span className="action-val" style={{ color: prediction.severity === 'high_risk' ? 'var(--status-high)' : 'inherit' }}>
                {prediction.recommended_action}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
