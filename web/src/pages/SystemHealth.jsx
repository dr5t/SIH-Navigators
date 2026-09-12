import React, { useState, useEffect } from 'react';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';

export default function SystemHealth() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const runHealthCheck = () => {
    setLoading(true);
    // Simulate health check sweeping through all subsystems
    setTimeout(() => {
      setResults([
        { id: 'sensors', name: 'Internal Sensors (IMU)', status: 'pass', details: 'Acc, Gyro, Mag reporting at 100Hz' },
        { id: 'calibration', name: 'Sensor Calibration', status: 'pass', details: 'Attitude aligned, IMU biases known' },
        { id: 'gnss', name: 'GNSS Receiver', status: 'pass', details: 'Location permissions granted, good SNR' },
        { id: 'ai', name: 'AI Model (Speed Est)', status: 'pass', details: 'v1.0-fusion loaded and checksum verified' },
        { id: 'ins', name: 'Inertial Navigation Sys', status: 'pass', details: 'Strapdown initialized and aligned' },
        { id: 'fusion', name: 'ESKF Fusion Layer', status: 'pass', details: 'Covariance matrix nominal, Gating active' },
        { id: 'map', name: 'Offline Map Engine', status: 'pass', details: 'Graph network loaded (34,000 nodes)' },
        { id: 'imu', name: 'External IMU', status: 'warn', details: 'Not connected (falling back to smartphone IMU)' },
        { id: 'storage', name: 'Local Storage Queue', status: 'pass', details: 'Database OK. 0 pending offline syncs.' },
        { id: 'cloud', name: 'Cloud API Connectivity', status: 'pass', details: 'JWT Authenticated. Ping: 24ms' },
        { id: 'sync', name: 'Background Sync Worker', status: 'pass', details: 'Registered with WorkManager' }
      ]);
      setLoading(false);
    }, 1500);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <header>
        <h2 style={{ marginBottom: 'var(--space-2)' }}>System Health Check</h2>
        <p style={{ color: 'var(--text-muted)' }}>Validate all edge and cloud components before beginning a field test.</p>
      </header>

      <div className="card" style={{ padding: 'var(--space-6)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ margin: 0 }}>Run Diagnostics</h3>
          <p style={{ color: 'var(--text-secondary)', margin: 'var(--space-2) 0 0 0', fontSize: '0.875rem' }}>
            Performs a full hardware and software stack validation.
          </p>
        </div>
        <button 
          className="btn btn-primary" 
          onClick={runHealthCheck} 
          disabled={loading}
          style={{ minWidth: '150px' }}
        >
          {loading ? <><Loader2 size={18} className="spin" style={{marginRight: '8px'}}/> Running...</> : 'Check System'}
        </button>
      </div>

      {results && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: 'var(--space-4) var(--space-6)', borderBottom: '1px solid var(--border-light)', backgroundColor: 'var(--bg-surface)' }}>
            <h3 style={{ margin: 0 }}>Diagnostic Results</h3>
          </div>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {results.map((item, idx) => (
              <li key={item.id} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: 'var(--space-4) var(--space-6)',
                borderBottom: idx < results.length - 1 ? '1px solid var(--border-light)' : 'none'
              }}>
                <div style={{ marginRight: 'var(--space-4)' }}>
                  {item.status === 'pass' ? (
                    <CheckCircle2 color="var(--success)" size={24} />
                  ) : item.status === 'warn' ? (
                    <CheckCircle2 color="var(--status-warning)" size={24} /> // Using warning color for External IMU
                  ) : (
                    <XCircle color="var(--error)" size={24} />
                  )}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: '500' }}>{item.name}</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{item.details}</div>
                </div>
                <div>
                  <span className={`status-badge status-${item.status === 'pass' ? 'success' : 'warning'}`}>
                    {item.status === 'warn' ? 'OPTIONAL' : 'OK'}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
