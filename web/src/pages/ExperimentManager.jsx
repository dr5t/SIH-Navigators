import React, { useState, useEffect } from 'react';
import { Database, Download, GitCompare } from 'lucide-react';

export default function ExperimentManager() {
  const [experiments, setExperiments] = useState([]);
  const [comparison, setComparison] = useState([]);
  
  useEffect(() => {
    // In a real app, this would fetch from /experiments and /experiments/compare
    // For this UI scaffolding, we load mock representations of the data.
    setExperiments([
      { id: "EXP_9812", timestamp: "2026-09-12 14:22", device: "Pixel 8 Pro", model: "v1.5-fusion", map: "local-grid-1.0", scenario: "Urban Canyon 60s" },
      { id: "EXP_9813", timestamp: "2026-09-12 15:05", device: "Galaxy S24", model: "v1.4-baseline", map: "local-grid-1.0", scenario: "Highway Tunnel 120s" }
    ]);
    
    setComparison([
        { configuration: "INS", position_error: 12.4, drift: 4.5 },
        { configuration: "INS + AI", position_error: 8.2, drift: 2.1 },
        { configuration: "INS + AI + Map", position_error: 4.1, drift: 0.4 },
        { configuration: "Full system", position_error: 3.2, drift: 0.2 }
    ]);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', height: '100%' }}>
      <header>
        <h2 style={{ marginBottom: 'var(--space-2)' }}>Experiment Manager</h2>
        <p style={{ color: 'var(--text-muted)' }}>Manage, export, and compare reproducible navigation experiments.</p>
      </header>

      {/* Compare Experiments Table */}
      <div className="card">
        <h3 style={{ marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GitCompare size={20} color="var(--brand-primary)" /> Compare Experiments
        </h3>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
              <th style={{ padding: 'var(--space-2) 0' }}>Configuration</th>
              <th style={{ padding: 'var(--space-2) 0' }}>Position Error (m)</th>
              <th style={{ padding: 'var(--space-2) 0' }}>Drift %</th>
            </tr>
          </thead>
          <tbody>
            {comparison.map((c, i) => (
              <tr key={i} style={{ borderBottom: '1px solid var(--border-light)' }}>
                <td style={{ padding: 'var(--space-3) 0', fontWeight: '500' }}>{c.configuration}</td>
                <td style={{ padding: 'var(--space-3) 0' }}>{c.position_error.toFixed(1)}</td>
                <td style={{ padding: 'var(--space-3) 0', color: c.drift < 1 ? 'var(--success)' : 'inherit' }}>
                  {c.drift.toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Experiment History */}
      <div className="card">
        <h3 style={{ marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Database size={20} color="var(--brand-primary)" /> Experiment History
        </h3>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-light)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              <th style={{ padding: 'var(--space-2) 0' }}>ID</th>
              <th style={{ padding: 'var(--space-2) 0' }}>Date</th>
              <th style={{ padding: 'var(--space-2) 0' }}>Device</th>
              <th style={{ padding: 'var(--space-2) 0' }}>Model / Map</th>
              <th style={{ padding: 'var(--space-2) 0' }}>Scenario</th>
              <th style={{ padding: 'var(--space-2) 0' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {experiments.map((e, i) => (
              <tr key={i} style={{ borderBottom: '1px solid var(--border-light)' }}>
                <td style={{ padding: 'var(--space-3) 0', fontWeight: 'bold' }}>{e.id}</td>
                <td style={{ padding: 'var(--space-3) 0' }}>{e.timestamp}</td>
                <td style={{ padding: 'var(--space-3) 0' }}>{e.device}</td>
                <td style={{ padding: 'var(--space-3) 0' }}>{e.model} / {e.map}</td>
                <td style={{ padding: 'var(--space-3) 0' }}>{e.scenario}</td>
                <td style={{ padding: 'var(--space-3) 0' }}>
                  <button className="btn btn-outline" style={{ padding: '4px 8px', fontSize: '0.875rem' }}>
                     <Download size={14} style={{marginRight: '4px'}}/> Export
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}
