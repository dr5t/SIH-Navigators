import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function Navigation() {
  const [trajectory, setTrajectory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, this would fetch from the FastAPI backend or connect via WebSocket
    fetch('http://localhost:8000/api/v1/sessions/sim_session_001')
      .then(res => res.json())
      .then(data => {
        if(data && data.trajectory) {
           setTrajectory(data.trajectory.map(pt => [pt.lat, pt.lon]));
        }
        setLoading(false);
      })
      .catch(err => {
        console.warn("Backend not running. Using fallback UI.", err);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 'var(--space-4)' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>Navigation</h2>
          <p style={{ color: 'var(--text-muted)' }}>Live vehicle telemetry and map view.</p>
        </div>
        <div className="status-badge status-dr">DR MODE ACTIVE</div>
      </header>

      <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', position: 'relative' }}>
        {loading ? (
          <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
             Loading Map Data...
          </div>
        ) : (
          <MapContainer 
            center={trajectory.length > 0 ? trajectory[0] : [37.7749, -122.4194]} 
            zoom={15} 
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            {trajectory.length > 0 && <Polyline positions={trajectory} color="var(--brand-primary)" weight={4} />}
          </MapContainer>
        )}
        
        {/* Overlay HUD */}
        <div style={{ 
          position: 'absolute', bottom: '20px', left: '20px', zIndex: 1000, 
          background: 'var(--bg-surface-elevated)', padding: 'var(--space-4)',
          borderRadius: 'var(--radius-md)', border: '1px solid var(--border-light)',
          boxShadow: 'var(--shadow-md)'
        }}>
           <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Current Speed</div>
           <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>45 <span style={{fontSize: '1rem'}}>km/h</span></div>
        </div>
      </div>
    </div>
  );
}
