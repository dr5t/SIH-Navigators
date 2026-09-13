import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import { API_BASE } from '../telemetry';
export default function SessionsList() {
  const [sessions, setSessions] = useState([]);
  const [status, setStatus] = useState('loading');
  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_BASE}/sessions`, { signal: controller.signal }).then(res => { if (!res.ok) throw Error(); return res.json(); }).then(data => { if (!Array.isArray(data)) throw Error(); setSessions(data); setStatus('ready'); }).catch(e => { if (e.name !== 'AbortError') setStatus('error'); });
    return () => controller.abort();
  }, []);
  return <div><header className="page-heading"><div><span className="eyebrow">NAVIGATION LOG</span><h1>Trips</h1><p>Recorded device sessions and navigation events.</p></div><span className="eyebrow">{sessions.length} SESSIONS</span></header>
  {sessions.map(session => <Link className="session-row" to={`/sessions/${session.id}`} key={session.id}><div><strong>{session.created_at ? new Date(session.created_at).toLocaleString() : session.id}</strong><span>Device {session.device_id} · {session.id}</span></div><ChevronRight size={18}/></Link>)}
  {!sessions.length && <div className="empty-state"><h2>{status === 'loading' ? 'Loading trip log…' : status === 'error' ? 'Trip service unavailable' : 'No recorded trips'}</h2><p>{status === 'error' ? 'Connect to your navigation server to view uploaded sessions. Local trips remain on Android.' : 'Completed sessions will appear here when your device uploads its recordings.'}</p></div>}</div>;
}
