import React, { useState } from 'react';
import { Play, Download, BarChart2 } from 'lucide-react';

export default function Benchmark() {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState(null);

  const runBenchmark = () => {
    setRunning(true);
    // Simulate backend call
    setTimeout(() => {
      setResults({
        configs: [
          { name: 'B. Pure INS', drift: 124.5, percent: 12.4, rmse: 85.2 },
          { name: 'C. INS + NHC', drift: 45.2, percent: 4.5, rmse: 28.1 },
          { name: 'D. INS + NHC + AI', drift: 18.4, percent: 1.8, rmse: 12.3 },
          { name: 'E. Full Navigators', drift: 4.1, percent: 0.4, rmse: 3.2 }
        ],
        outageDuration: 60,
        totalDistance: 1005
      });
      setRunning(false);
    }, 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <header>
        <h2>Benchmarking & Evaluation</h2>
        <p style={{ color: 'var(--text-muted)' }}>Rigorous GNSS-denied performance analysis.</p>
      </header>

      <div className="card" style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <label style={{ display: 'block', marginBottom: 'var(--space-2)', fontSize: '0.875rem' }}>Dataset Session</label>
          <select style={{ width: '100%', padding: 'var(--space-2)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-light)' }}>
            <option>Urban Canyon Route 1</option>
            <option>Highway Tunnel</option>
            <option>Suburban Mix</option>
          </select>
        </div>
        
        <div style={{ flex: 1, minWidth: '200px' }}>
          <label style={{ display: 'block', marginBottom: 'var(--space-2)', fontSize: '0.875rem' }}>GNSS Outage Duration</label>
          <select style={{ width: '100%', padding: 'var(--space-2)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-light)' }}>
            <option>60 Seconds</option>
            <option>30 Seconds</option>
            <option>120 Seconds</option>
            <option>500 Meters</option>
          </select>
        </div>
        
        <div style={{ marginTop: 'auto' }}>
          <button className="btn btn-primary" onClick={runBenchmark} disabled={running}>
            {running ? 'Running...' : <><Play size={16} style={{marginRight: '8px'}}/> Run Benchmark</>}
          </button>
        </div>
      </div>

      {results && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
            <div className="card">
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Outage Duration</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{results.outageDuration}s</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Distance Traveled</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{results.totalDistance}m</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Best Drift %</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)' }}>
                {results.configs[3].percent}%
              </div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: 'var(--space-4)' }}>Ablation Results</h3>
            <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
                  <th style={{ padding: 'var(--space-2) 0' }}>Configuration</th>
                  <th style={{ padding: 'var(--space-2) 0' }}>Absolute Drift (m)</th>
                  <th style={{ padding: 'var(--space-2) 0' }}>Drift %</th>
                  <th style={{ padding: 'var(--space-2) 0' }}>Position RMSE (m)</th>
                </tr>
              </thead>
              <tbody>
                {results.configs.map((c, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid var(--border-light)' }}>
                    <td style={{ padding: 'var(--space-3) 0', fontWeight: '500' }}>{c.name}</td>
                    <td style={{ padding: 'var(--space-3) 0' }}>{c.drift.toFixed(1)}</td>
                    <td style={{ padding: 'var(--space-3) 0' }}>{c.percent.toFixed(2)}%</td>
                    <td style={{ padding: 'var(--space-3) 0' }}>{c.rmse.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
             <button className="btn btn-outline"><Download size={16} style={{marginRight: '8px'}} /> Download Report (PDF)</button>
             <button className="btn btn-outline"><BarChart2 size={16} style={{marginRight: '8px'}} /> View Trajectory Plots</button>
          </div>
        </>
      )}
    </div>
  );
}
