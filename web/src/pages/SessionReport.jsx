import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity, Navigation, MapPin } from 'lucide-react';

export default function SessionReport() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:8000/sessions/${id}/report`)
      .then(res => res.json())
      .then(data => setReport(data))
      .catch(err => console.error(err));
  }, [id]);

  if (!report) return <div style={{ padding: '24px' }}>Loading report...</div>;

  const gnssPoints = report.telemetry.filter(p => p.mode === 'GNSS_GOOD' || p.mode === 'GNSS_DEGRADED');
  const drPoints = report.telemetry.filter(p => p.mode === 'DEAD_RECKONING' || p.mode === 'DEAD_RECKONING_DEGRADED');
  
  // Note: in a real app we would use react-leaflet to plot these arrays on a map
  // and Recharts to plot speed / pos_uncertainty over time.

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
          <h2 style={{ margin: 0 }}>Session Report</h2>
          <p style={{ margin: 0, color: 'var(--text-muted)' }}>{id}</p>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Activity color="var(--brand-primary)" />
            <h4 style={{ margin: 0 }}>Data Points</h4>
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{report.total_points}</div>
        </div>
        
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Navigation color="var(--status-dr)" />
            <h4 style={{ margin: 0 }}>DR Fixes</h4>
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{drPoints.length}</div>
        </div>
        
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <MapPin color="var(--status-success)" />
            <h4 style={{ margin: 0 }}>GNSS Fixes</h4>
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{gnssPoints.length}</div>
        </div>
      </div>

      <div className="card" style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <p>Map Visualization Area</p>
          <p style={{ fontSize: '0.875rem' }}>Trajectory plotter (Leaflet integration) goes here</p>
        </div>
      </div>
      
      <div className="card" style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <p>Time-Series Charts</p>
          <p style={{ fontSize: '0.875rem' }}>Speed & Error metrics (Recharts integration) goes here</p>
        </div>
      </div>
    </div>
  );
}
