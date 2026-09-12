import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, ChevronRight } from 'lucide-react';

export default function SessionsList() {
  const [sessions, setSessions] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:8000/sessions')
      .then(res => res.json())
      .then(data => setSessions(data))
      .catch(err => console.error("Failed to load sessions", err));
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <header>
        <h2>Field Test Sessions</h2>
        <p style={{ color: 'var(--text-muted)' }}>Historical recordings from Android field tests.</p>
      </header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {sessions.map(session => (
          <div 
            key={session.id}
            className="card" 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              cursor: 'pointer'
            }}
            onClick={() => navigate(`/sessions/${session.id}`)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ padding: '12px', background: 'var(--bg-surface-elevated)', borderRadius: '8px' }}>
                <Calendar color="var(--brand-primary)" />
              </div>
              <div>
                <h3 style={{ margin: '0 0 4px 0', fontSize: '1.1rem' }}>{session.id}</h3>
                <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                  Device: {session.device_id}
                </p>
              </div>
            </div>
            <ChevronRight color="var(--text-muted)" />
          </div>
        ))}
        {sessions.length === 0 && (
          <p style={{ color: 'var(--text-muted)' }}>No sessions recorded yet.</p>
        )}
      </div>
    </div>
  );
}
