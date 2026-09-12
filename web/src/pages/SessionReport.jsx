import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity, Navigation, MapPin, AlertTriangle, CheckCircle, Clock, Star } from 'lucide-react';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function SessionReport() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    // Fetch raw telemetry
    fetch(`http://localhost:8000/sessions/${id}/report`)
      .then(res => res.json())
      .then(data => setReport(data))
      .catch(err => console.error(err));

    // Fetch computed summary
    fetch(`http://localhost:8000/sessions/${id}/summary`)
      .then(res => res.json())
      .then(data => setSummary(data))
      .catch(err => console.error(err));
  }, [id]);

  if (!report || !summary) return <div style={{ padding: '24px' }}>Loading report...</div>;

  const getPolylineColor = (mode) => {
    if (mode.includes('DEAD_RECKONING')) return 'var(--status-dr)';
    if (mode.includes('MAP_MATCH')) return '#a855f7';
    return 'var(--status-success)';
  };

  const segments = [];
  let currentSegment = [];
  let currentMode = null;

  report.telemetry.forEach((p, idx) => {
    if (p.mode !== currentMode && currentSegment.length > 0) {
      currentSegment.push([p.lat, p.lon]); // Connect to next
      segments.push({ mode: currentMode, positions: currentSegment });
      currentSegment = [[p.lat, p.lon]];
      currentMode = p.mode;
    } else {
      currentMode = p.mode;
      currentSegment.push([p.lat, p.lon]);
    }
  });
  if (currentSegment.length > 0) {
    segments.push({ mode: currentMode, positions: currentSegment });
  }

  const mapCenter = report.telemetry.length > 0 
    ? [report.telemetry[0].lat, report.telemetry[0].lon]
    : [0, 0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button 
          onClick={() => navigate('/sessions')}
          style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-primary)' }}
        >
          <ArrowLeft />
        </button>
        <div>
          <h2 style={{ margin: 0 }}>Smart Trip Summary</h2>
          <p style={{ margin: 0, color: 'var(--text-muted)' }}>Session: {id}</p>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--space-4)' }}>
        {summary.quality?.unavailable ? (
          <div className="card" style={{ gridColumn: '1 / -1' }}>
            <h4 style={{ margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Star color="var(--text-muted)" size={20} /> Navigation Quality
            </h4>
            <div style={{ color: 'var(--text-muted)' }}>
              Quality score unavailable — insufficient session data.
            </div>
          </div>
        ) : (
          <div className="card" style={{ gridColumn: '1 / -1', display: 'flex', gap: 'var(--space-6)', flexWrap: 'wrap' }}>
            <div style={{ flex: '1', minWidth: '200px' }}>
              <h4 style={{ margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Star color={summary.quality?.overall_score >= 90 ? 'var(--status-success)' : summary.quality?.overall_score >= 60 ? 'var(--status-warning)' : 'var(--status-error)'} size={20} /> 
                Navigation Quality
              </h4>
              <div style={{ 
                fontSize: '2.5rem', 
                fontWeight: 'bold', 
                color: summary.quality?.overall_score >= 90 ? 'var(--status-success)' : summary.quality?.overall_score >= 60 ? 'var(--status-warning)' : 'var(--status-error)' 
              }}>
                {summary.quality?.overall_score} <span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>/ 100</span>
              </div>
            </div>
            
            <div style={{ flex: '2', minWidth: '250px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>GNSS Quality</span>
                <span style={{ fontWeight: 'bold' }}>{summary.quality?.gnss_score}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>DR Stability</span>
                <span style={{ fontWeight: 'bold' }}>{summary.quality?.dr_score}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Data Completeness</span>
                <span style={{ fontWeight: 'bold' }}>{summary.quality?.completeness_score}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>System Interruptions</span>
                <span style={{ fontWeight: 'bold' }}>{summary.quality?.interruptions_score}</span>
              </div>
            </div>

            <div style={{ flex: '1', minWidth: '200px', borderLeft: '1px solid var(--border-light)', paddingLeft: 'var(--space-4)' }}>
              <h5 style={{ margin: '0 0 8px 0', color: 'var(--text-muted)' }}>Explanation</h5>
              {summary.quality?.explanation?.map((msg, idx) => (
                <div key={idx} style={{ fontSize: '0.85rem', marginBottom: '4px' }}>• {msg}</div>
              ))}
            </div>
          </div>
        )}

        <div className="card">
          <h4 style={{ margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity color="var(--brand-primary)" size={20} /> Overview
          </h4>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Distance</span>
            <span style={{ fontWeight: 'bold' }}>{(summary.overview?.total_distance / 1000).toFixed(2)} km</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Duration</span>
            <span style={{ fontWeight: 'bold' }}>{Math.round(summary.overview?.duration / 60)} min</span>
          </div>
        </div>
        
        <div className="card">
          <h4 style={{ margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Navigation color="var(--status-dr)" size={20} /> Navigation
          </h4>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>GNSS Outages</span>
            <span style={{ fontWeight: 'bold' }}>{summary.navigation?.outages}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>GNSS Time</span>
            <span style={{ fontWeight: 'bold' }}>{Math.round(summary.navigation?.gnss_time / 60)} min</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>DR Distance</span>
            <span style={{ fontWeight: 'bold' }}>{(summary.navigation?.dr_distance / 1000).toFixed(2)} km</span>
          </div>
        </div>
        
        <div className="card">
          <h4 style={{ margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity color="var(--status-success)" size={20} /> Performance
          </h4>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Avg Speed</span>
            <span style={{ fontWeight: 'bold' }}>{(summary.performance?.avg_speed * 3.6).toFixed(1)} km/h</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Max Speed</span>
            <span style={{ fontWeight: 'bold' }}>{(summary.performance?.max_speed * 3.6).toFixed(1)} km/h</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Max Uncertainty</span>
            <span style={{ fontWeight: 'bold' }}>{summary.performance?.max_uncertainty.toFixed(1)} m</span>
          </div>
        </div>

        <div className="card">
          <h4 style={{ margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle color="var(--brand-primary)" size={20} /> System
          </h4>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Sensors</span>
            <span style={{ fontWeight: 'bold', color: 'var(--status-success)' }}>{summary.system?.sensor_status}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Sync Status</span>
            <span style={{ fontWeight: 'bold' }}>{summary.system?.sync_status}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Model</span>
            <span style={{ fontWeight: 'bold' }}>{summary.system?.model_version}</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-6)' }}>
        <div className="card" style={{ height: '400px', display: 'flex', flexDirection: 'column' }}>
          <h4 style={{ margin: '0 0 16px 0' }}>Trajectory</h4>
          <div style={{ flex: 1, borderRadius: '8px', overflow: 'hidden' }}>
            <MapContainer center={mapCenter} zoom={14} style={{ height: '100%', width: '100%' }}>
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; OpenStreetMap contributors'
              />
              {segments.map((seg, i) => (
                <Polyline 
                  key={i} 
                  positions={seg.positions} 
                  color={getPolylineColor(seg.mode)}
                  weight={5}
                />
              ))}
            </MapContainer>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h4 style={{ margin: '0 0 16px 0' }}>Key Events</h4>
          <div style={{ overflowY: 'auto', flex: 1 }}>
            {summary.events?.map((e, idx) => (
              <div key={idx} style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <div style={{ 
                  width: '10px', height: '10px', borderRadius: '50%', marginTop: '6px',
                  background: e.type.includes('LOST') ? 'var(--status-dr)' : 
                              e.type.includes('RECOVERED') ? 'var(--status-success)' : 'var(--brand-primary)'
                }} />
                <div>
                  <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{e.message}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {new Date(e.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            {(!summary.events || summary.events.length === 0) && (
              <div style={{ color: 'var(--text-muted)' }}>No notable events recorded.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
