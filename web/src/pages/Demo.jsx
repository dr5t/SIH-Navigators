import React, { useState, useEffect } from 'react';
import { Activity, ShieldCheck, Map as MapIcon, Database } from 'lucide-react';

export default function Demo() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // In a real scenario, this fetches from the last stored benchmark result.
    // For this UI scaffolding, we load a mock representation of the final state.
    setData({
      drDistance: 1005,
      outageDuration: 60,
      positionError: 4.1,
      driftPercent: 0.4,
      speedError: 0.8,
      headingError: 1.2,
      modelVersion: "v1.0-fusion",
      mapVersion: "local-grid-1.0"
    });
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', height: '100%' }}>
      <header style={{ textAlign: 'center', marginBottom: 'var(--space-4)' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: 'var(--space-2)' }}>Navigators Performance</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.25rem' }}>GNSS-Denied Reliability Metrics</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--space-6)' }}>
        
        {/* Metric 1 */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: 'var(--space-6)' }}>
          <Activity size={48} color="var(--brand-primary)" style={{ marginBottom: 'var(--space-4)' }}/>
          <div style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Drift Percentage</div>
          <div style={{ fontSize: '3rem', fontWeight: '900', color: 'var(--success)', margin: 'var(--space-2) 0' }}>
            {data.driftPercent !== null ? `${data.driftPercent}%` : 'Not measured'}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>over {data.drDistance}m outage</div>
        </div>

        {/* Metric 2 */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: 'var(--space-6)' }}>
          <ShieldCheck size={48} color="var(--brand-primary)" style={{ marginBottom: 'var(--space-4)' }}/>
          <div style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Position Error (RMSE)</div>
          <div style={{ fontSize: '3rem', fontWeight: '900', margin: 'var(--space-2) 0' }}>
            {data.positionError !== null ? `${data.positionError}m` : 'Not measured'}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>After {data.outageDuration}s total GNSS loss</div>
        </div>

        {/* Metric 3 */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: 'var(--space-6)' }}>
          <MapIcon size={48} color="var(--brand-primary)" style={{ marginBottom: 'var(--space-4)' }}/>
          <div style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Speed Error</div>
          <div style={{ fontSize: '3rem', fontWeight: '900', margin: 'var(--space-2) 0' }}>
            {data.speedError !== null ? `${data.speedError} m/s` : 'Not measured'}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>AI-Estimated Accuracy</div>
        </div>

      </div>

      <div className="card" style={{ marginTop: 'auto', display: 'flex', justifyContent: 'space-around', padding: 'var(--space-4)' }}>
         <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
            <Database size={16} /> <span>Model: {data.modelVersion}</span>
         </div>
         <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
            <Database size={16} /> <span>Map Engine: {data.mapVersion}</span>
         </div>
      </div>
    </div>
  );
}
