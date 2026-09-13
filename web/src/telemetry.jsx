import { createContext, useContext, useEffect, useState } from 'react';
export const API_BASE = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`;
const TelemetryContext = createContext(null);
export const number = (value, digits = 1) => typeof value === 'number' && Number.isFinite(value) ? value.toFixed(digits) : '—';
export function TelemetryProvider({ children }) {
  const [state, setState] = useState({ point: null, connected: false, received: null, trajectory: [] });
  useEffect(() => {
    let socket, reconnect, latest = null, disposed = false;
    const connect = () => {
      socket = new WebSocket(`${API_BASE.replace(/^http/, 'ws')}/telemetry/live`);
      socket.onopen = () => setState(s => ({ ...s, connected: true }));
      socket.onmessage = event => {
        try { const message = JSON.parse(event.data); if (message.type === 'telemetry_batch' && Array.isArray(message.data)) { const sample = message.data.at(-1); if (sample) latest = { ...sample, lat: sample.latitude ?? sample.lat, lon: sample.longitude ?? sample.lon, session_id: message.session_id }; } } catch { /* Keep the last valid sample. */ }
      };
      socket.onclose = () => { if (!disposed) { setState(s => ({ ...s, connected: false })); reconnect = setTimeout(connect, 5000); } };
      socket.onerror = () => socket.close();
    };
    connect();
    const publish = setInterval(() => {
      if (!latest) return;
      const point = latest; latest = null;
      setState(s => {
        let trajectory = point.session_id && point.session_id !== s.point?.session_id ? [] : s.trajectory;
        if (Number.isFinite(point.lat) && Number.isFinite(point.lon) && Math.abs(point.lat) <= 90 && Math.abs(point.lon) <= 180) {
          const last = trajectory.at(-1);
          if (!last || Math.hypot(point.lat - last[0], point.lon - last[1]) > .00005) trajectory = [...trajectory.slice(-1999), [point.lat, point.lon]];
        }
        return { ...s, point, trajectory, received: Date.now() };
      });
    }, 250);
    return () => { disposed = true; clearInterval(publish); clearTimeout(reconnect); socket.close(); };
  }, []);
  const [now, setNow] = useState(Date.now());
  useEffect(() => { const timer = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(timer); }, []);
  return <TelemetryContext.Provider value={{ ...state, stale: !state.received || now - state.received > 5000 }}>{children}</TelemetryContext.Provider>;
}
export const useTelemetry = () => useContext(TelemetryContext);
export function modeLabel(mode) {
  return ({ GNSS_GOOD: 'GNSS + INS', GNSS_DEGRADED: 'GNSS degraded', DEAD_RECKONING: 'Dead reckoning', DEAD_RECKONING_DEGRADED: 'DR degraded' })[mode] || mode?.replaceAll('_', ' ') || 'Waiting for navigation';
}
