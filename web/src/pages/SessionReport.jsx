import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity, Navigation, MapPin, AlertTriangle, CheckCircle, Clock, Star, Download, ShieldAlert, X } from 'lucide-react';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function SessionReport() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [summary, setSummary] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  
  const categories = ['All', 'GNSS', 'DR', 'AI', 'Sensors', 'Map', 'Fusion', 'Errors'];

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

  const triggerExport = () => {
    window.location.href = `http://localhost:8000/sessions/${id}/export`;
    setIsExportModalOpen(false);
  };

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
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', position: 'relative' }}>
      
      {/* Export Modal */}
      {isExportModalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 9999,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div className="card" style={{ maxWidth: '500px', width: '100%', position: 'relative' }}>
            <button onClick={() => setIsExportModalOpen(false)} style={{ position: 'absolute', top: '16px', right: '16px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: 'var(--brand-primary)' }}>
              <ShieldAlert size={24} /> Export Session Data
            </h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>
              You are about to export raw telemetry and logs for this session.
            </p>
            <ul style={{ marginBottom: '24px', paddingLeft: '20px', color: 'var(--text-primary)', lineHeight: '1.6' }}>
              <li><strong>Included:</strong> Trajectory, raw GNSS, AI Speed limits, events, diagnostics, and configurations.</li>
              <li><strong>Privacy:</strong> This export contains exact location coordinates and timestamps. Be careful when sharing this file publicly.</li>
              <li><strong>Format:</strong> A ZIP archive containing structured CSVs and JSONs.</li>
            </ul>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button className="btn-secondary" onClick={() => setIsExportModalOpen(false)}>Cancel</button>
              <button className="btn-primary" onClick={triggerExport} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Download size={16} /> Accept & Download
              </button>
            </div>
          </div>
        </div>
      )}

      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
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
        </div>
        
        <button className="btn-secondary" onClick={() => setIsExportModalOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Download size={16} /> Export Data
        </button>
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
          <h4 style={{ margin: '0 0 16px 0' }}>Navigation Event Timeline</h4>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
            {categories.map(c => (
              <button 
                key={c}
                onClick={() => setSelectedCategory(c)}
                style={{
                  padding: '4px 12px',
                  borderRadius: '16px',
                  border: '1px solid var(--border-light)',
                  background: selectedCategory === c ? 'var(--brand-primary)' : 'transparent',
                  color: selectedCategory === c ? 'white' : 'var(--text-primary)',
                  cursor: 'pointer',
                  fontSize: '0.8rem'
                }}
              >
                {c}
              </button>
            ))}
          </div>
          <div style={{ overflowY: 'auto', flex: 1 }}>
            {summary.events?.filter(e => selectedCategory === 'All' || e.category === selectedCategory).map((e, idx) => {
              let color = 'var(--brand-primary)';
              if (e.severity === 'ERROR') color = 'var(--status-error)';
              if (e.severity === 'WARNING') color = 'var(--status-warning)';
              if (e.severity === 'SUCCESS') color = 'var(--status-success)';
              
              return (
                <div key={idx} style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ 
                    width: '10px', height: '10px', borderRadius: '50%', marginTop: '6px',
                    background: color
                  }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{e.description}</span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {new Date(e.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    {e.measurements && Object.entries(e.measurements).map(([k, v]) => (
                      <div key={k} style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {k}: {v}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
            {(!summary.events || summary.events.filter(e => selectedCategory === 'All' || e.category === selectedCategory).length === 0) && (
              <div style={{ color: 'var(--text-muted)' }}>No events to display.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
