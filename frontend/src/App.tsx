import { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import RiskEvaluator from './components/RiskEvaluator';
import SecurityMonitor from './components/SecurityMonitor';
import ModelPerformance from './components/ModelPerformance';
import { checkBackendHealth } from './utils/api';

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'evaluator' | 'security' | 'performance'>('dashboard');
  const [backendStatus, setBackendStatus] = useState<{ online: boolean; engine_version?: string }>({ online: false });

  useEffect(() => {
    // Poll backend health every 5 seconds
    const checkStatus = () => {
      checkBackendHealth().then(status => {
        setBackendStatus({ online: status.online, engine_version: status.engine_version });
      });
    };
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'evaluator':
        return <RiskEvaluator />;
      case 'security':
        return <SecurityMonitor />;
      case 'performance':
        return <ModelPerformance />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      {/* Premium Header */}
      <header className="app-header">
        <div className="logo-section">
          <span className="logo-icon">🚂</span>
          <div>
            <h1 className="logo-text">MARS</h1>
            <div className="logo-sub">Anomaly & Safety System</div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Live Monitor
          </button>
          <button 
            className={`nav-tab ${activeTab === 'evaluator' ? 'active' : ''}`}
            onClick={() => setActiveTab('evaluator')}
          >
            ⚙️ Risk Evaluator
          </button>
          <button 
            className={`nav-tab ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            📹 Security Feed
          </button>
          <button 
            className={`nav-tab ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => setActiveTab('performance')}
          >
            📈 Model Performance
          </button>
        </nav>

        {/* System Status badge */}
        <div className="system-status">
          <span className={`status-indicator ${backendStatus.online ? 'online' : 'offline'}`}></span>
          <span>
            {backendStatus.online 
              ? `API ONLINE (${backendStatus.engine_version || 'v0.1'})` 
              : 'OFFLINE (SIM MODE)'}
          </span>
        </div>
      </header>

      {/* Main Section */}
      <main className="app-main">
        {renderTabContent()}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Built with MARS ML Pipeline | Powered by React, TypeScript, and scikit-learn | Version 0.2.0</p>
      </footer>
    </div>
  );
}
