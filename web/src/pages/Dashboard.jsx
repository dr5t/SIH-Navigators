import React, { useState, useEffect } from 'react';
import { Activity, MapPin, Wifi, Zap } from 'lucide-react';

export default function Dashboard() {
  const [status, setStatus] = useState({
    internet: 'Online',
    gnss: 'GNSS + INS',
    speed: 0,
    heading: 0,
    syncQueue: 0
  });

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/telemetry/live');
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'telemetry_batch' && msg.data && msg.data.length > 0) {
        // Get latest point in batch
        const latest = msg.data[msg.data.length - 1];
        setStatus(prev => ({
          ...prev,
          speed: Math.round(latest.speed * 3.6), // Convert m/s to km/h
          heading: Math.round(latest.heading || 0),
          gnss: latest.mode || prev.gnss
        }));
      }
    };

    ws.onclose = () => {
      setStatus(prev => ({ ...prev, internet: 'Offline (Cloud disconnected)' }));
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <header>
        <h2>Dashboard</h2>
        <p style={{ color: 'var(--text-muted)' }}>Real-time navigation and sensor overview.</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--space-4)' }}>
        
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Activity color="var(--status-dr)" />
            <h3 style={{ margin: 0 }}>Navigation Status</h3>
          </div>
          <div className="status-badge status-success">{status.gnss}</div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <MapPin color="var(--brand-primary)" />
            <h3 style={{ margin: 0 }}>Current Telemetry</h3>
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{status.speed} km/h</div>
          <div style={{ color: 'var(--text-secondary)' }}>Heading: {status.heading}° (W)</div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Zap color="var(--status-warning)" />
            <h3 style={{ margin: 0 }}>Sensor Health</h3>
          </div>
          <div className="status-badge status-warning">Diagnostics Required</div>
          <p style={{ marginTop: '8px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Run full diagnostic scan before next trip.</p>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Wifi color="var(--status-success)" />
            <h3 style={{ margin: 0 }}>Connectivity</h3>
          </div>
          <div className="status-badge status-success">{status.internet}</div>
          <p style={{ marginTop: '8px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>{status.syncQueue} pending records</p>
        </div>

      </div>
    </div>
  );
}
