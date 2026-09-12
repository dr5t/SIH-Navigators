import React, { useState } from 'react';
import { Activity, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-react';

export default function Diagnostics() {
  const [running, setRunning] = useState(false);
  
  const sensors = [
    { name: 'Accelerometer (INS)', status: 'Optimal', type: 'success' },
    { name: 'Gyroscope (INS)', status: 'Optimal', type: 'success' },
    { name: 'Magnetometer', status: 'Calibrating...', type: 'warning' },
    { name: 'GNSS Receiver', status: 'Optimal (3D Fix)', type: 'success' },
    { name: 'Neural Speed Engine', status: 'Active (v2.1)', type: 'success' },
    { name: 'Local Backend Sync', status: 'Connected', type: 'success' },
  ];

  const runDiagnostics = () => {
    setRunning(true);
    setTimeout(() => setRunning(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>System Diagnostics</h2>
          <p style={{ color: 'var(--text-muted)' }}>Validate sensor hardware and neural engine health.</p>
        </div>
        <button className="btn btn-primary" onClick={runDiagnostics} disabled={running}>
          {running ? <><RefreshCw size={16} style={{ marginRight: '8px', animation: 'spin 1s linear infinite' }} /> Running...</> : 'Run Diagnostics'}
        </button>
      </header>

      <div className="card">
        <h3 style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
          Hardware Status
        </h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {sensors.map((s, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--space-3)', background: 'var(--bg-base)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {s.type === 'success' ? <CheckCircle color="var(--status-success)" size={20} /> : <AlertTriangle color="var(--status-warning)" size={20} />}
                <span style={{ fontWeight: 500 }}>{s.name}</span>
              </div>
              <span className={`status-badge status-${s.type}`}>{s.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
