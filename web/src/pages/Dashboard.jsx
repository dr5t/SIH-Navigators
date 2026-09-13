import { Link } from 'react-router-dom';
import { ArrowUpRight, Navigation2 } from 'lucide-react';
import { useTelemetry, number, modeLabel } from '../telemetry';
export default function Dashboard() {
  const { point, connected, stale, received } = useTelemetry();
  return <div className="navigation-page">
    <header className="page-heading"><div><span className="eyebrow">NAVIGATION / LIVE INSTRUMENTS</span><h1>{stale ? 'Ready when you are.' : modeLabel(point?.mode)}</h1><p>{stale ? 'Start navigation on your connected Android device.' : 'Live navigation state from your device.'}</p></div><span className={`status-badge ${connected && !stale ? 'status-success' : ''}`}>{!connected ? 'Disconnected' : stale ? 'Awaiting telemetry' : 'Receiving'}</span></header>
    <section className="instrument-panel" aria-label="Navigation instruments">
      <div className="speed-instrument"><span className="eyebrow">GROUND SPEED</span><div className="speed-value">{number(point?.speed == null ? null : point.speed * 3.6, 0)}<span>km/h</span></div><span className="instrument-caption">{stale && point ? 'LAST RECEIVED POSITION' : 'NAVIGATION TELEMETRY'}</span></div>
      <div className="course-instrument"><Navigation2 size={24} strokeWidth={1.3}/><strong>{number(point?.course ?? point?.heading, 0)}°</strong><span className="eyebrow">TRUE COURSE</span></div>
      <div className="instrument-details"><dl><div><dt>Latitude</dt><dd>{number(point?.lat, 6)}</dd></div><div><dt>Longitude</dt><dd>{number(point?.lon, 6)}</dd></div><div><dt>Position uncertainty</dt><dd>{number(point?.pos_uncertainty ?? point?.h_acc)} m</dd></div><div><dt>Navigation state</dt><dd>{stale ? 'Unavailable' : modeLabel(point?.mode)}</dd></div></dl></div>
    </section>
    <div className="navigation-secondary"><section><span className="eyebrow">SYSTEM STATE</span><dl className="instrument-list"><div><dt>GNSS / inertial fusion</dt><dd>{stale ? 'UNAVAILABLE' : modeLabel(point?.mode)}</dd></div><div><dt>AI speed inference</dt><dd>{!stale && point?.ai_status === 'ACTIVE' ? 'ACTIVE' : 'UNAVAILABLE'}</dd></div><div><dt>Confidence</dt><dd>{!stale ? point?.confidence || 'UNAVAILABLE' : 'UNAVAILABLE'}</dd></div><div><dt>Last received</dt><dd>{received ? new Date(received).toLocaleTimeString() : 'No telemetry yet'}</dd></div></dl></section>
    <section className="map-entry"><span className="eyebrow">POSITION & TRAJECTORY</span><h2>Keep the route in view.</h2><p>Follow the device position, heading and recorded trajectory on the map.</p><Link className="btn btn-primary" to="/navigation">Open map <ArrowUpRight size={18}/></Link><Link className="text-link" to="/sessions">Browse trip log</Link></section></div>
  </div>;
}
