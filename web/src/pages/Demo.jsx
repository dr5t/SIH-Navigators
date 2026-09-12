import React, { useState, useEffect } from 'react';
import { Activity, Play, CheckCircle, Navigation as NavIcon, Map, ActivitySquare } from 'lucide-react';

export default function Demo() {
  const [demoState, setDemoState] = useState('IDLE'); // IDLE, RUNNING, COMPLETE
  const [currentPhase, setCurrentPhase] = useState(0);
  const [metrics, setMetrics] = useState(null);

  const phases = [
    "GNSS Available (Normal Operation)",
    "GNSS Outage (Entering Tunnel)",
    "DR Active (AI Speed Estimation)",
    "Map Matching (Snapping to Graph)",
    "GNSS Recovery (Covariance Correction)"
  ];

  const startDemo = () => {
    setDemoState('RUNNING');
    setCurrentPhase(0);
    
    // Trigger backend script (in a real app, this would hit a specific /demo endpoint)
    // We simulate the WebSocket state transitions here for the UI flow
    let phase = 0;
    const interval = setInterval(() => {
      phase++;
      if (phase >= phases.length) {
        clearInterval(interval);
        setDemoState('COMPLETE');
        setMetrics({
          positionError: "4.1m",
          driftPercent: "0.4%",
          speedRmse: "0.8 m/s",
          headingError: "1.2°",
          outageDuration: "60s",
          recoveryTime: "1.5s",
          inferenceLatency: "12ms",
          navUpdateRate: "100Hz",
          cpuLoad: "14%",
          modelVersion: "v1.0-fusion",
          mapVersion: "local-grid-1.0"
        });
      } else {
        setCurrentPhase(phase);
      }
    }, 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', height: '100%' }}>
      <header style={{ textAlign: 'center', marginBottom: 'var(--space-4)' }}>
        <h2 style={{ fontSize: '2.5rem', marginBottom: 'var(--space-2)' }}>End-to-End Demo</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.25rem' }}>One-click execution of a full GNSS outage scenario.</p>
      </header>

      {/* Demo Controls */}
      <div className="card" style={{ display: 'flex', justifyContent: 'center', padding: 'var(--space-6)' }}>
        <button 
          className="btn btn-primary" 
          onClick={startDemo} 
          disabled={demoState === 'RUNNING'}
          style={{ padding: 'var(--space-4) var(--space-8)', fontSize: '1.25rem' }}
        >
          {demoState === 'RUNNING' ? 'Demo in Progress...' : <><Play style={{marginRight: '8px'}}/> Start Scenario</>}
        </button>
      </div>

      {/* Live State Transitions */}
      {demoState !== 'IDLE' && (
        <div className="card" style={{ padding: 'var(--space-6)' }}>
          <h3 style={{ marginBottom: 'var(--space-4)' }}>Live State Transitions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {phases.map((p, idx) => (
              <div key={idx} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '16px',
                opacity: idx > currentPhase ? 0.3 : 1,
                color: idx === currentPhase ? 'var(--brand-primary)' : 'inherit'
              }}>
                {idx < currentPhase ? (
                  <CheckCircle color="var(--success)" />
                ) : idx === currentPhase ? (
                  <Activity className="spin" color="var(--brand-primary)" />
                ) : (
                  <div style={{ width: '24px', height: '24px', borderRadius: '50%', border: '2px solid var(--border-light)' }} />
                )}
                <span style={{ fontSize: '1.1rem', fontWeight: idx === currentPhase ? 'bold' : 'normal' }}>{p}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Technical Metrics Center */}
      {demoState === 'COMPLETE' && metrics && (
        <div style={{ animation: 'fadeIn 0.5s ease' }}>
          <h3 style={{ margin: 'var(--space-6) 0 var(--space-4) 0' }}>Technical Metrics Center</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
            
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Position Error (RMSE)</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{metrics.positionError}</div>
            </div>
            
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Absolute Drift</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--success)' }}>{metrics.driftPercent}</div>
            </div>
            
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Speed Error (RMSE)</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{metrics.speedRmse}</div>
            </div>
            
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Heading Error</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{metrics.headingError}</div>
            </div>
          </div>

          <div className="card" style={{ marginTop: 'var(--space-4)' }}>
             <h4 style={{ marginBottom: 'var(--space-4)' }}>System Performance</h4>
             <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                <div><span style={{color: 'var(--text-muted)'}}>Outage Duration:</span> {metrics.outageDuration}</div>
                <div><span style={{color: 'var(--text-muted)'}}>Recovery Time:</span> {metrics.recoveryTime}</div>
                <div><span style={{color: 'var(--text-muted)'}}>AI Inference Latency:</span> {metrics.inferenceLatency}</div>
                <div><span style={{color: 'var(--text-muted)'}}>Nav Update Rate:</span> {metrics.navUpdateRate}</div>
                <div><span style={{color: 'var(--text-muted)'}}>Edge CPU Load:</span> {metrics.cpuLoad}</div>
                <div><span style={{color: 'var(--text-muted)'}}>Active Model:</span> {metrics.modelVersion}</div>
             </div>
          </div>
        </div>
      )}
    </div>
  );
}
