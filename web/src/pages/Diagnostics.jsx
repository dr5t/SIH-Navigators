import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle, AlertTriangle, RefreshCw, Info } from 'lucide-react';

export default function Diagnostics() {
  const [running, setRunning] = useState(false);
  const [capabilities, setCapabilities] = useState([]);

  const checkCapabilities = () => {
    setRunning(true);
    
    // Simulate slight delay for checking
    setTimeout(() => {
      const caps = [];

      // Check Geolocation (GNSS)
      if ('geolocation' in navigator) {
        caps.push({ name: 'GNSS Receiver (Browser)', status: 'Supported', type: 'success' });
      } else {
        caps.push({ name: 'GNSS Receiver', status: 'Not Supported by Browser', type: 'warning', note: 'Requires Android Native App for full GNSS support.' });
      }

      // Check Accelerometer / Gyroscope (DeviceMotion)
      if (typeof DeviceMotionEvent !== 'undefined') {
        caps.push({ name: 'Accelerometer / Gyroscope', status: 'Supported', type: 'success' });
      } else {
        caps.push({ name: 'Accelerometer / Gyroscope', status: 'Not Supported / Permission Denied', type: 'error', note: 'Browser cannot access IMU. Requires Android Native App for INS integration.' });
      }

      // Check Magnetometer (DeviceOrientation)
      if (typeof DeviceOrientationEvent !== 'undefined') {
        caps.push({ name: 'Magnetometer', status: 'Supported', type: 'success' });
      } else {
        caps.push({ name: 'Magnetometer', status: 'Not Supported', type: 'error', note: 'Requires Android Native App for full heading accuracy.' });
      }

      // Backend Status
      caps.push({ name: 'Local Backend Sync', status: 'Checking...', type: 'warning' }); // Will be updated by actual fetch in real app
      
      setCapabilities(caps);
      setRunning(false);
    }, 600);
  };

  useEffect(() => {
    checkCapabilities();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>System Diagnostics</h2>
          <p style={{ color: 'var(--text-muted)' }}>Validate browser capabilities and hardware access.</p>
        </div>
        <button className="btn btn-primary" onClick={checkCapabilities} disabled={running}>
          {running ? <><RefreshCw size={16} style={{ marginRight: '8px', animation: 'spin 1s linear infinite' }} /> Running...</> : 'Run Diagnostics'}
        </button>
      </header>

      <div className="card">
        <h3 style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
          Web Capability Status
        </h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {capabilities.map((s, i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', padding: 'var(--space-3)', background: 'var(--bg-base)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {s.type === 'success' ? <CheckCircle color="var(--status-success)" size={20} /> : <AlertTriangle color={s.type === 'error' ? 'var(--status-error)' : 'var(--status-warning)'} size={20} />}
                  <span style={{ fontWeight: 500 }}>{s.name}</span>
                </div>
                <span className={`status-badge status-${s.type}`}>{s.status}</span>
              </div>
              {s.note && (
                <div style={{ display: 'flex', gap: '8px', marginTop: 'var(--space-2)', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  <Info size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span>{s.note}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
