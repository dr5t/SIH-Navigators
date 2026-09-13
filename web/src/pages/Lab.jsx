import React, { useState, useEffect } from 'react';
import { Database, Play, GitCompare, Activity, Navigation, Crosshair } from 'lucide-react';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Lab() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState("");
  const [config, setConfig] = useState("INS");
  const [isRunning, setIsRunning] = useState(false);
  
  const [experiments, setExperiments] = useState([]);
  const [compareA, setCompareA] = useState("");
  const [compareB, setCompareB] = useState("");
  const [compareData, setCompareData] = useState(null);
  
  const [currentResult, setCurrentResult] = useState(null);

  useEffect(() => {
    fetchSessions();
    fetchExperiments();
  }, []);

  const fetchSessions = async () => {
    try {
      const res = await fetch("http://localhost:8000/sessions");
      const data = await res.json();
      setSessions(data);
      if (data.length > 0) setSelectedSession(data[0].id);
    } catch (e) {
      console.error(e);
    }
  };
  
  const fetchExperiments = async () => {
    try {
      const res = await fetch("http://localhost:8000/experiments");
      const data = await res.json();
      setExperiments(data);
    } catch (e) {
      console.error(e);
    }
  };

  const runReplay = async () => {
    if (!selectedSession) return;
    setIsRunning(true);
    setCurrentResult(null);
    try {
      const res = await fetch(`http://localhost:8000/sessions/${selectedSession}/replay`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ configuration: config })
      });
      const data = await res.json();
      setCurrentResult(data);
      fetchExperiments(); // refresh list
    } catch (e) {
      console.error("Replay failed", e);
    } finally {
      setIsRunning(false);
    }
  };

  const loadComparison = async () => {
    if (!compareA || !compareB) return;
    try {
      const res = await fetch(`http://localhost:8000/experiments/compare?exp_a=${compareA}&exp_b=${compareB}`);
      const data = await res.json();
      setCompareData(data);
    } catch (e) {
      console.error(e);
    }
  };

  const configs = [
    "INS",
    "INS + Vehicle Constraints",
    "INS + AI Speed",
    "INS + AI Speed + Map Matching",
    "Full Navigators"
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', height: '100%', overflowY: 'auto', paddingBottom: 'var(--space-8)' }}>
      <header>
        <h2 style={{ marginBottom: 'var(--space-2)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={28} color="var(--brand-primary)" />
          Navigation Lab
        </h2>
        <p style={{ color: 'var(--text-muted)' }}>Advanced replay-based experimentation. Select a historical session and configuration to evaluate drift and algorithmic improvements.</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 'var(--space-6)' }}>
        
        {/* Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <div className="card">
            <h3 style={{ marginBottom: 'var(--space-4)' }}>Run Experiment</h3>
            
            <label style={{ display: 'block', marginBottom: 'var(--space-2)', fontWeight: '500' }}>Session</label>
            <select 
              value={selectedSession} 
              onChange={e => setSelectedSession(e.target.value)}
              style={{ width: '100%', padding: 'var(--space-2)', marginBottom: 'var(--space-4)', background: 'var(--surface-sunken)', border: '1px solid var(--border-light)', color: 'white', borderRadius: '4px' }}
            >
              {sessions.map(s => <option key={s.id} value={s.id}>{s.id.split('_')[1] || s.id} ({new Date(s.start_time).toLocaleString()})</option>)}
            </select>

            <label style={{ display: 'block', marginBottom: 'var(--space-2)', fontWeight: '500' }}>Configuration</label>
            <select 
              value={config} 
              onChange={e => setConfig(e.target.value)}
              style={{ width: '100%', padding: 'var(--space-2)', marginBottom: 'var(--space-6)', background: 'var(--surface-sunken)', border: '1px solid var(--border-light)', color: 'white', borderRadius: '4px' }}
            >
              {configs.map(c => <option key={c} value={c}>{c}</option>)}
            </select>

            <button 
              className="btn-primary" 
              onClick={runReplay} 
              disabled={isRunning || !selectedSession}
              style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}
            >
              {isRunning ? "Running Simulation..." : <><Play size={18} /> Run Replay</>}
            </button>
          </div>

          {/* Metrics Panel */}
          {currentResult && (
            <div className="card" style={{ borderLeft: '4px solid var(--brand-primary)' }}>
              <h3 style={{ marginBottom: 'var(--space-4)' }}>Results</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Position Error</span>
                  <strong style={{ color: 'var(--error)' }}>{currentResult.results.position_error} m</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Speed RMSE</span>
                  <strong>{currentResult.results.speed_rmse} m/s</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Heading Error</span>
                  <strong>{currentResult.results.heading_error}°</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Drift</span>
                  <strong style={{ color: currentResult.results.drift_percent < 2.0 ? 'var(--success)' : 'var(--warning)' }}>
                    {currentResult.results.drift_percent}%
                  </strong>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Visualizations */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          {currentResult ? (
            <>
              <div className="card" style={{ padding: 0, overflow: 'hidden', height: '400px', display: 'flex', flexDirection: 'column' }}>
                <div style={{ padding: 'var(--space-3)', background: 'var(--surface-sunken)', borderBottom: '1px solid var(--border-light)' }}>
                  <h3 style={{ margin: 0, fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Navigation size={16} /> Trajectory Comparison
                  </h3>
                </div>
                <div style={{ flex: 1 }}>
                  <MapContainer 
                    center={[currentResult.trajectory[0].lat, currentResult.trajectory[0].lon]} 
                    zoom={17} 
                    style={{ height: '100%', width: '100%', background: '#1a1a1a' }}
                    zoomControl={false}
                  >
                    <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                    
                    {/* Ground Truth */}
                    <Polyline 
                      positions={currentResult.trajectory.map(p => [p.gt_lat, p.gt_lon])} 
                      color="#4CAF50" 
                      weight={4} 
                      opacity={0.7}
                    />
                    
                    {/* Estimated */}
                    <Polyline 
                      positions={currentResult.trajectory.map(p => [p.lat, p.lon])} 
                      color="#FF5252" 
                      weight={3}
                      dashArray="5, 10"
                    />
                  </MapContainer>
                </div>
                <div style={{ padding: 'var(--space-2)', display: 'flex', gap: 'var(--space-4)', fontSize: '0.8rem', justifyContent: 'center' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><div style={{ width: '12px', height: '4px', background: '#4CAF50' }}></div> Ground Truth</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><div style={{ width: '12px', height: '4px', background: '#FF5252', borderStyle: 'dashed' }}></div> Engine Estimate</span>
                </div>
              </div>

              <div className="card" style={{ height: '300px' }}>
                <h3 style={{ marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Crosshair size={16} /> Error vs Time
                </h3>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={currentResult.trajectory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis 
                      dataKey="timestamp" 
                      stroke="#888" 
                      tickFormatter={t => new Date(t).toLocaleTimeString()}
                      minTickGap={50}
                    />
                    <YAxis stroke="#888" label={{ value: 'Error (m/s)', angle: -90, position: 'insideLeft', fill: '#888' }} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--surface-raised)', border: '1px solid var(--border-light)' }}
                      labelFormatter={t => new Date(t).toLocaleTimeString()}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey={d => Math.abs(d.speed - d.gt_speed || d.speed)} 
                      name="Speed Error" 
                      stroke="#FF9800" 
                      dot={false} 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
              Select a session and run an experiment to view trajectory and error analysis.
            </div>
          )}
        </div>
      </div>

      <hr style={{ borderColor: 'var(--border-light)', margin: 'var(--space-4) 0' }} />

      {/* Compare Panel */}
      <div>
        <h3 style={{ marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GitCompare size={20} color="var(--brand-primary)" /> Compare Experiments
        </h3>
        
        <div style={{ display: 'flex', gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
          <select 
            value={compareA} 
            onChange={e => setCompareA(e.target.value)}
            style={{ flex: 1, padding: 'var(--space-2)', background: 'var(--surface-sunken)', border: '1px solid var(--border-light)', color: 'white', borderRadius: '4px' }}
          >
            <option value="">Select Experiment A</option>
            {experiments.map(e => <option key={e.id} value={e.id}>{e.configuration} ({new Date(e.timestamp * 1000).toLocaleString()})</option>)}
          </select>
          
          <select 
            value={compareB} 
            onChange={e => setCompareB(e.target.value)}
            style={{ flex: 1, padding: 'var(--space-2)', background: 'var(--surface-sunken)', border: '1px solid var(--border-light)', color: 'white', borderRadius: '4px' }}
          >
            <option value="">Select Experiment B</option>
            {experiments.map(e => <option key={e.id} value={e.id}>{e.configuration} ({new Date(e.timestamp * 1000).toLocaleString()})</option>)}
          </select>
          
          <button className="btn-secondary" onClick={loadComparison} disabled={!compareA || !compareB}>
            Compare
          </button>
        </div>

        {compareData && (
          <div className="card">
            <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
                  <th style={{ padding: 'var(--space-2) 0' }}>Metric</th>
                  <th style={{ padding: 'var(--space-2) 0' }}>{compareData.experiment_a.configuration}</th>
                  <th style={{ padding: 'var(--space-2) 0' }}>{compareData.experiment_b.configuration}</th>
                  <th style={{ padding: 'var(--space-2) 0' }}>Improvement</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
                  <td style={{ padding: 'var(--space-3) 0', color: 'var(--text-muted)' }}>Position Error</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{compareData.experiment_a.results.position_error} m</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{compareData.experiment_b.results.position_error} m</td>
                  <td style={{ padding: 'var(--space-3) 0', color: compareData.experiment_a.results.position_error > compareData.experiment_b.results.position_error ? 'var(--success)' : 'var(--error)' }}>
                    {((compareData.experiment_a.results.position_error - compareData.experiment_b.results.position_error)).toFixed(1)} m
                  </td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
                  <td style={{ padding: 'var(--space-3) 0', color: 'var(--text-muted)' }}>Drift</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{compareData.experiment_a.results.drift_percent}%</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{compareData.experiment_b.results.drift_percent}%</td>
                  <td style={{ padding: 'var(--space-3) 0', color: compareData.experiment_a.results.drift_percent > compareData.experiment_b.results.drift_percent ? 'var(--success)' : 'var(--error)' }}>
                    {((compareData.experiment_a.results.drift_percent - compareData.experiment_b.results.drift_percent)).toFixed(1)}%
                  </td>
                </tr>
                <tr>
                  <td style={{ padding: 'var(--space-3) 0', color: 'var(--text-muted)' }}>Speed RMSE</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{compareData.experiment_a.results.speed_rmse} m/s</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{compareData.experiment_b.results.speed_rmse} m/s</td>
                  <td style={{ padding: 'var(--space-3) 0', color: compareData.experiment_a.results.speed_rmse > compareData.experiment_b.results.speed_rmse ? 'var(--success)' : 'var(--error)' }}>
                    {((compareData.experiment_a.results.speed_rmse - compareData.experiment_b.results.speed_rmse)).toFixed(1)} m/s
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
