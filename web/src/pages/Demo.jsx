import React, { useState, useEffect } from 'react';
import { Activity, Play, CheckCircle, Navigation as NavIcon, Map, ActivitySquare } from 'lucide-react';
import { getConfidenceExplanation } from '../utils/explanation';

export default function Demo() {
  const [demoState, setDemoState] = useState('IDLE'); // IDLE, RUNNING, COMPLETE
  const [currentPhase, setCurrentPhase] = useState(0);
  const [metrics, setMetrics] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);

  const phases = [
    "GNSS Available (Normal Operation)",
    "GNSS Outage (Entering Tunnel)",
    "DR Active (AI Speed Estimation)",
    "Map Matching (Snapping to Graph)",
    "GNSS Recovery (Covariance Correction)"
  ];

  const simulatedStates = [
    { mode: 'GNSS_GOOD', pos_uncertainty: 3.2, speed_source: 'GNSS', map_status: 'UNAVAILABLE' },
    { mode: 'GNSS_DEGRADED', pos_uncertainty: 12.5, speed_source: 'GNSS', map_status: 'UNAVAILABLE' },
    { mode: 'DEAD_RECKONING', pos_uncertainty: 31.0, speed_source: 'AI', map_status: 'UNAVAILABLE' },
    { mode: 'DEAD_RECKONING', pos_uncertainty: 25.0, speed_source: 'AI', map_status: 'MATCHED' },
    { mode: 'GNSS_GOOD', pos_uncertainty: 4.5, speed_source: 'GNSS', map_status: 'MATCHED' }
  ];

  const currentState = simulatedStates[currentPhase] || simulatedStates[0];
  const explanation = getConfidenceExplanation(currentState);

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

      {/* Demo Controls & Status */}
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--space-6)' }}>
        <button 
          className="btn btn-primary" 
          onClick={startDemo} 
          disabled={demoState === 'RUNNING'}
          style={{ padding: 'var(--space-4) var(--space-8)', fontSize: '1.25rem' }}
        >
          {demoState === 'RUNNING' ? 'Demo in Progress...' : <><Play style={{marginRight: '8px'}}/> Start Scenario</>}
        </button>

        {demoState !== 'IDLE' && (
          <div 
            onClick={() => setShowExplanation(true)}
            style={{
              padding: 'var(--space-2) var(--space-4)',
              borderRadius: '24px',
              border: `2px solid ${explanation.confidence === 'HIGH' ? 'var(--status-success)' : explanation.confidence === 'LOW' ? 'var(--status-error)' : 'var(--status-warning)'}`,
              color: explanation.confidence === 'HIGH' ? 'var(--status-success)' : explanation.confidence === 'LOW' ? 'var(--status-error)' : 'var(--status-warning)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: 'bold',
              animation: 'fadeIn 0.3s ease'
            }}
          >
            <Activity size={20} />
            Confidence: {explanation.confidence}
          </div>
        )}
      </div>

      {/* Explanation Modal */}
      {showExplanation && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div className="card" style={{ maxWidth: '500px', width: '100%', padding: 'var(--space-6)', position: 'relative' }}>
            <button 
              onClick={() => setShowExplanation(false)}
              style={{ position: 'absolute', top: '16px', right: '16px', background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.5rem', color: 'var(--text-primary)' }}
            >
              &times;
            </button>
            <h2 style={{ marginBottom: 'var(--space-2)' }}>Navigation Status</h2>
            <div style={{ marginBottom: 'var(--space-6)', color: explanation.confidence === 'HIGH' ? 'var(--status-success)' : explanation.confidence === 'LOW' ? 'var(--status-error)' : 'var(--status-warning)', fontWeight: 'bold' }}>
              Confidence: {explanation.confidence}
            </div>

            <div style={{ marginBottom: 'var(--space-4)' }}>
              <h4 style={{ marginBottom: 'var(--space-2)' }}>Reasons:</h4>
              <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-secondary)' }}>
                {explanation.reasons.map((r, i) => <li key={i} style={{ marginBottom: '4px' }}>{r}</li>)}
              </ul>
            </div>

            <div style={{ marginBottom: 'var(--space-6)' }}>
              <h4 style={{ marginBottom: 'var(--space-2)' }}>Current Mitigation:</h4>
              <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-secondary)', listStyleType: 'none' }}>
                {explanation.mitigations.length > 0 ? explanation.mitigations.map((m, i) => (
                  <li key={i} style={{ marginBottom: '4px', marginLeft: '-20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle size={16} color="var(--status-success)" /> {m}
                  </li>
                )) : <li style={{ marginLeft: '-20px' }}>None</li>}
              </ul>
            </div>

            {explanation.actions.length > 0 && (
              <div style={{ display: 'flex', gap: '12px' }}>
                {explanation.actions.map((act, i) => (
                  <button key={i} className="btn" style={{ flex: 1, backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border-light)' }}>
                    {act}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Live State Transitions Timeline */}
      {demoState !== 'IDLE' && (
        <div className="card" style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ marginBottom: 'var(--space-4)' }}>Navigation Event Timeline</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {phases.map((p, idx) => {
              const eventConfig = [
                { type: 'GNSS_ACQUIRED', category: 'GNSS', severity: 'SUCCESS', desc: 'GNSS acquired', meas: { accuracy: '3.2m' } },
                { type: 'GNSS_LOST', category: 'GNSS', severity: 'ERROR', desc: 'GNSS lost', meas: { last_accuracy: '12.5m' } },
                { type: 'DR_STARTED', category: 'DR', severity: 'WARNING', desc: 'DR started (AI Speed)', meas: { speed: '14.2m/s' } },
                { type: 'MAP_MATCHED', category: 'Map', severity: 'INFO', desc: 'Map matched', meas: { confidence: '0.92' } },
                { type: 'FUSION_COMPLETED', category: 'Fusion', severity: 'SUCCESS', desc: 'Fusion completed (GNSS Recovered)', meas: null }
              ][idx];

              let color = 'var(--brand-primary)';
              if (eventConfig.severity === 'ERROR') color = 'var(--status-error)';
              if (eventConfig.severity === 'WARNING') color = 'var(--status-warning)';
              if (eventConfig.severity === 'SUCCESS') color = 'var(--status-success)';
              
              const isVisible = idx <= currentPhase;
              
              return (
                <div key={idx} style={{ 
                  display: 'flex', 
                  gap: '12px',
                  opacity: isVisible ? 1 : 0.3,
                  transition: 'opacity 0.5s ease'
                }}>
                  {isVisible ? (
                     <div style={{ width: '12px', height: '12px', borderRadius: '50%', marginTop: '6px', background: color }} />
                  ) : (
                     <div style={{ width: '12px', height: '12px', borderRadius: '50%', marginTop: '6px', border: '2px solid var(--border-light)' }} />
                  )}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: isVisible ? 'bold' : 'normal', fontSize: '1rem' }}>{eventConfig.desc}</span>
                      {isVisible && <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Live</span>}
                    </div>
                    {isVisible && eventConfig.meas && Object.entries(eventConfig.meas).map(([k, v]) => (
                      <div key={k} style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {k}: {v}
                      </div>
                    ))}
                    <div style={{ fontSize: '0.75rem', marginTop: '4px', display: 'inline-block', padding: '2px 8px', borderRadius: '12px', background: 'var(--bg-elevated)', color: 'var(--text-secondary)' }}>
                      {eventConfig.category}
                    </div>
                  </div>
                </div>
              );
            })}
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
