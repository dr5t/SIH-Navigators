import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTelemetry, number } from '../telemetry';
export default function Diagnostics() {
  const { point, connected, stale, received } = useTelemetry();
  const [permission, setPermission] = useState('Unknown');
  useEffect(() => {
    let active = true, result;
    const update = () => { if (active) setPermission(result.state); };
    navigator.permissions?.query({ name: 'geolocation' }).then(value => { result = value; update(); result.addEventListener('change', update); }).catch(() => {});
    return () => { active = false; result?.removeEventListener('change', update); };
  }, []);
  const rows = [
    ['Device telemetry', connected ? stale ? 'Connected · awaiting data' : 'Receiving' : 'Disconnected'],
    ['Last telemetry', received ? new Date(received).toLocaleTimeString() : 'None received'],
    ['Position uncertainty', `${number(point?.pos_uncertainty ?? point?.h_acc)} m`],
    ['AI inference', !stale && point?.ai_status === 'ACTIVE' ? 'Active' : 'Unavailable'],
    ['Map matching', !stale ? point?.map_status || 'Unavailable' : 'Unavailable'],
    ['Browser geolocation API', 'geolocation' in navigator ? 'Available' : 'Unavailable'],
    ['Browser location permission', permission],
    ['Device motion API', typeof DeviceMotionEvent !== 'undefined' ? 'API present · samples not requested' : 'Unavailable'],
    ['Secure context', window.isSecureContext ? 'Yes' : 'No']
  ];
  return <div className="settings-page"><header className="page-heading"><div><span className="eyebrow">ENGINEERING / SYSTEM HEALTH</span><h1>Diagnostics</h1><p>Measured device state and browser capabilities.</p></div></header><dl className="instrument-list">{rows.map(([name, value]) => <div key={name}><dt>{name}</dt><dd>{value}</dd></div>)}</dl><p style={{ margin: '24px 0' }}>Sensor API availability does not establish sensor health. Open Diagnostics on Android for live IMU sample rates and GNSS status.</p><Link className="btn btn-outline" to="/health">Device system health</Link></div>;
}
