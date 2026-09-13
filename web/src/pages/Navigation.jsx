import { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { LocateFixed, Plus, Minus } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import { useTelemetry, number, modeLabel } from '../telemetry';
function Controls({ position, follow, setFollow }) {
  const map = useMapEvents({ dragstart: () => setFollow(false) });
  useEffect(() => { if (position && follow) map.setView(position, Math.max(map.getZoom(), 16), { animate: false }); }, [position, follow, map]);
  useEffect(() => { map.invalidateSize(); }, [map]);
  return <div className="map-controls"><button aria-label="Zoom in" onClick={() => map.zoomIn()}><Plus/></button><button aria-label="Zoom out" onClick={() => map.zoomOut()}><Minus/></button><button aria-label="Follow / re-center" disabled={!position} className={follow ? 'selected' : ''} onClick={() => { setFollow(true); if (position) map.setView(position, Math.max(map.getZoom(), 16)); }}><LocateFixed/></button></div>;
}
export default function Navigation() {
  const { point, trajectory, stale } = useTelemetry();
  const [follow, setFollow] = useState(true);
  const [online, setOnline] = useState(navigator.onLine);
  const [tileError, setTileError] = useState(false);
  const position = useMemo(() => Number.isFinite(point?.lat) && Number.isFinite(point?.lon) && Math.abs(point.lat) <= 90 && Math.abs(point.lon) <= 180 ? [point.lat, point.lon] : null, [point?.lat, point?.lon]);
  const heading = point?.course ?? point?.heading;
  const marker = useMemo(() => L.divIcon({ className: 'navigation-marker', html: Number.isFinite(heading) ? `<svg viewBox="0 0 40 40" style="transform:rotate(${heading}deg)"><path d="M20 3 34 35 20 28 6 35Z" fill="#2884b4" stroke="white" stroke-width="3"/></svg>` : '<span class="position-dot"></span>', iconSize: [40, 40], iconAnchor: [20, 20] }), [heading]);
  useEffect(() => { const update = () => setOnline(navigator.onLine); window.addEventListener('online', update); window.addEventListener('offline', update); return () => { window.removeEventListener('online', update); window.removeEventListener('offline', update); }; }, []);
  return <div className="map-page"><header className="page-heading"><div><span className="eyebrow">POSITION & TRAJECTORY</span><h1>Map</h1></div><span className="status-badge">{online ? 'Online tiles' : 'Offline · cached coverage only'}</span></header>
    <div className="map-canvas"><MapContainer bounds={[[-85, -180], [85, 180]]} zoomControl={false}>
      <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>' eventHandlers={{ tileerror: () => setTileError(true), load: () => setTileError(false) }}/>
      {trajectory.length > 1 && <Polyline positions={trajectory} color="#2884b4" weight={4}/>}
      {position && <Marker position={position} icon={marker}/>}
      <Controls position={position} follow={follow} setFollow={setFollow}/>
    </MapContainer>
    <div className="map-hud"><span className="eyebrow">{stale ? position ? 'LAST RECEIVED POSITION' : 'NO POSITION YET' : modeLabel(point?.mode)}</span><strong>{number(point?.speed == null ? null : point.speed * 3.6, 0)} <small>km/h</small></strong><span>Course {number(heading, 0)}° · ±{number(point?.pos_uncertainty ?? point?.h_acc)} m</span></div>
    {(!position || tileError || !online) && <div className="map-notice" role="status"><strong>{!position ? 'Waiting for device position' : 'Offline map coverage'}</strong><p>{!position ? 'Start navigation on Android. You can browse the map while waiting.' : 'Previously viewed tiles may be available in your browser cache. Android keeps a dedicated offline tile store.'}</p></div>}
    </div></div>;
}
