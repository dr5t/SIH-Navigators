import React from 'react';
import { Route, Map as MapIcon, Calendar, Clock, Download } from 'lucide-react';

export default function Sessions() {
  const sessions = [
    { id: 'trip_001', date: '2026-09-12 10:15', duration: '45m 12s', distance: '32.5 km', drTime: '12m (26%)' },
    { id: 'trip_002', date: '2026-09-11 14:30', duration: '1h 15m', distance: '85.2 km', drTime: '5m (6%)' },
    { id: 'trip_003', date: '2026-09-10 09:00', duration: '22m 05s', distance: '12.0 km', drTime: '0m (0%)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Navigation Sessions</h2>
          <p style={{ color: 'var(--text-muted)' }}>Historical logs and telemetry exports.</p>
        </div>
      </header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        {sessions.map((session, i) => (
          <div key={session.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
              <div style={{ background: 'var(--bg-base)', padding: '12px', borderRadius: '50%' }}>
                <Route color="var(--brand-primary)" size={24} />
              </div>
              
              <div>
                <h3 style={{ margin: 0, fontSize: '1.125rem' }}>{session.id}</h3>
                <div style={{ display: 'flex', gap: '16px', color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '4px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Calendar size={14}/> {session.date}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Clock size={14}/> {session.duration}</span>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 'var(--space-6)', alignItems: 'center' }}>
               <div style={{ textAlign: 'right' }}>
                 <div style={{ fontWeight: 'bold' }}>{session.distance}</div>
                 <div style={{ fontSize: '0.75rem', color: 'var(--status-dr)' }}>DR: {session.drTime}</div>
               </div>
               
               <div style={{ display: 'flex', gap: '8px' }}>
                 <button className="btn btn-outline" title="View on Map"><MapIcon size={16} /></button>
                 <button className="btn btn-outline" title="Export CSV"><Download size={16} /></button>
               </div>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}
