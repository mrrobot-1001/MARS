
export default function ModelPerformance() {
  const trackFeatures = [
    { name: 'vibration_vertical_mean', val: 30 },
    { name: 'maintenance_score', val: 22 },
    { name: 'speed_max', val: 18 },
    { name: 'segment_age_years', val: 15 },
    { name: 'track_temperature_mean', val: 8 },
    { name: 'curvature_degree', val: 7 },
  ];

  const weatherFeatures = [
    { name: 'track_base_score', val: 42 },
    { name: 'rainfall_mm', val: 22 },
    { name: 'visibility_m', val: 14 },
    { name: 'wind_speed_kmph', val: 8 },
    { name: 'hazard_flags', val: 8 },
    { name: 'temperature_c', val: 6 },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Metrics Grid */}
      <div className="performance-grid">
        {/* Track model */}
        <div className="card">
          <span className="logo-sub" style={{ display: 'block', marginBottom: '0.25rem' }}>Gradient Boosting Classifier</span>
          <h3 className="camera-title" style={{ color: 'var(--color-brand)' }}>🚂 Track Risk Model</h3>
          <div style={{ margin: '1rem 0', display: 'flex', gap: '2rem' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Validation Accuracy</span>
              <div className="metric-value" style={{ fontSize: '2rem' }}>84.8%</div>
            </div>
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>F1 Macro Score</span>
              <div className="metric-value" style={{ fontSize: '2rem', color: 'var(--color-brand-cyan)' }}>86.5%</div>
            </div>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            Trained on 10,000 synthetic track events (50 segments) using scikit-learn.
          </span>
        </div>

        {/* Weather Fusion model */}
        <div className="card">
          <span className="logo-sub" style={{ display: 'block', marginBottom: '0.25rem' }}>Gradient Boosting Classifier</span>
          <h3 className="camera-title" style={{ color: 'var(--color-brand-purple)' }}>🌦️ Weather-Track Fusion</h3>
          <div style={{ margin: '1rem 0', display: 'flex', gap: '2rem' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Validation Accuracy</span>
              <div className="metric-value" style={{ fontSize: '2rem' }}>86.0%</div>
            </div>
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>F1 Macro Score</span>
              <div className="metric-value" style={{ fontSize: '2rem', color: 'var(--color-brand-cyan)' }}>87.3%</div>
            </div>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            Trained on 50,000 merged sensor-weather events using downsampling optimization.
          </span>
        </div>

        {/* Security model */}
        <div className="card">
          <span className="logo-sub" style={{ display: 'block', marginBottom: '0.25rem' }}>Object Detection & Heuristics</span>
          <h3 className="camera-title" style={{ color: 'var(--status-caution)' }}>🛡️ Security Anomaly Detector</h3>
          <div style={{ margin: '1rem 0', display: 'flex', gap: '2rem' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Supported Classes</span>
              <div className="metric-value" style={{ fontSize: '2rem' }}>4</div>
            </div>
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Engine</span>
              <div className="metric-value" style={{ fontSize: '2rem', color: 'var(--color-brand-cyan)' }}>YOLO</div>
            </div>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            Detects trespassing, person on track, restricted area breach, and unattended objects.
          </span>
        </div>
      </div>

      {/* Feature Importance charts */}
      <div className="dashboard-grid">
        {/* Track GBDT Importances */}
        <div className="card">
          <h4 className="explanations-header" style={{ marginBottom: '1rem' }}>Track Model Feature Importances</h4>
          <div className="explanations-list">
            {trackFeatures.map((feat, idx) => (
              <div key={idx} className="explanation-item">
                <div className="explanation-row">
                  <span className="explanation-factor" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{feat.name}</span>
                  <span className="explanation-score">{feat.val}%</span>
                </div>
                <div className="explanation-bar-bg" style={{ height: '6px' }}>
                  <div className="explanation-bar-fill" style={{ width: `${feat.val * 2}%`, background: 'var(--color-brand)' }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Weather GBDT Importances */}
        <div className="card">
          <h4 className="explanations-header" style={{ marginBottom: '1rem' }}>Weather Model Feature Importances</h4>
          <div className="explanations-list">
            {weatherFeatures.map((feat, idx) => (
              <div key={idx} className="explanation-item">
                <div className="explanation-row">
                  <span className="explanation-factor" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{feat.name}</span>
                  <span className="explanation-score" style={{ color: 'var(--color-brand-purple)' }}>{feat.val}%</span>
                </div>
                <div className="explanation-bar-bg" style={{ height: '6px' }}>
                  <div className="explanation-bar-fill" style={{ width: `${feat.val * 2}%`, background: 'var(--color-brand-purple)' }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Resources & Notebook links */}
      <div className="card" style={{ background: 'linear-gradient(135deg, rgba(37,99,235,0.05) 0%, rgba(139,92,246,0.05) 100%)', border: '1px solid rgba(59,130,246,0.15)' }}>
        <h4 className="camera-title" style={{ color: '#fff', marginBottom: '0.5rem' }}>🔗 Training & Governance Resources</h4>
        <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', marginBottom: '1rem', lineHeight: '1.5' }}>
          Retrain both risk prediction models using the Google Colab training notebook template. The notebook downloads data, builds training pipelines, plots confusion matrices, and exports new `.joblib` model weights ready for production.
        </p>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <a 
            href="https://colab.research.google.com/" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="camera-btn active" 
            style={{ padding: '0.6rem 1.25rem', textDecoration: 'none', display: 'inline-block' }}
          >
            🚀 Open Colab Notebook
          </a>
          <a 
            href="https://github.com/mrrobot-1001/MARS" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="camera-btn" 
            style={{ padding: '0.6rem 1.25rem', textDecoration: 'none', display: 'inline-block' }}
          >
            💻 View GitHub Repository
          </a>
        </div>
      </div>
    </div>
  );
}
