import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet marker icons not appearing in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Component to dynamically recenter map
function RecenterMap({ position }) {
  const map = useMap();
  useEffect(() => {
    if (position) {
      map.setView(position, map.getZoom());
    }
  }, [position, map]);
  return null;
}

export default function Navigation() {
  const [state, setState] = useState({
    lat: null,
    lon: null,
    speed: 0,
    heading: 0,
    accuracy: 0,
    mode: 'WAITING_FOR_LOCATION'
  });
  
  const [trajectory, setTrajectory] = useState([]);
  const [error, setError] = useState(null);
  const [isTracking, setIsTracking] = useState(false);
  
  const watchId = useRef(null);

  useEffect(() => {
    if (!('geolocation' in navigator)) {
      setError("Geolocation is not supported by this browser.");
      return;
    }

    const startTracking = () => {
      setIsTracking(true);
      watchId.current = navigator.geolocation.watchPosition(
        (position) => {
          const { latitude, longitude, speed, heading, accuracy } = position.coords;
          
          setState({
            lat: latitude,
            lon: longitude,
            speed: speed !== null ? speed : 0, // meters per second
            heading: heading !== null && !isNaN(heading) ? heading : 0,
            accuracy: accuracy,
            mode: accuracy < 10 ? 'GNSS_GOOD' : 'GNSS_DEGRADED'
          });
          
          setTrajectory(prev => {
            const newPoint = [latitude, longitude];
            if (prev.length > 0) {
              const last = prev[prev.length - 1];
              const R = 6371e3; // metres
              const φ1 = last[0] * Math.PI/180;
              const φ2 = latitude * Math.PI/180;
              const Δφ = (latitude-last[0]) * Math.PI/180;
              const Δλ = (longitude-last[1]) * Math.PI/180;

              const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                        Math.cos(φ1) * Math.cos(φ2) *
                        Math.sin(Δλ/2) * Math.sin(Δλ/2);
              const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
              const d = R * c; // in metres
              
              if (d < 10) {
                return prev;
              }
            }
            return [...prev, newPoint];
          });
          setError(null);
        },
        (err) => {
          setError(err.message);
          setState(prev => ({...prev, mode: 'NO_FIX'}));
        },
        {
          enableHighAccuracy: true,
          maximumAge: 0,
          timeout: 5000
        }
      );
    };

    startTracking();

    return () => {
      if (watchId.current !== null) {
        navigator.geolocation.clearWatch(watchId.current);
      }
    };
  }, []);

  const speedKmh = (state.speed * 3.6).toFixed(1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 'var(--space-4)' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>Navigation</h2>
          <p style={{ color: 'var(--text-muted)' }}>Live vehicle telemetry and map view.</p>
        </div>
        <div className={`status-badge ${state.mode.includes('GOOD') ? 'status-dr' : (state.mode === 'WAITING_FOR_LOCATION' ? 'status-dr' : 'status-error')}`}>
          {state.mode.replace('_', ' ')}
        </div>
      </header>

      {error && (
        <div style={{ background: 'var(--error-light)', color: 'var(--error-dark)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)', border: '1px solid var(--error-border)' }}>
          <strong>Location Error: </strong> {error}
        </div>
      )}

      <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', position: 'relative' }}>
        {state.lat === null ? (
           <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
              Waiting for Location Fix...
           </div>
        ) : (
          <MapContainer 
            center={[state.lat, state.lon]} 
            zoom={18} 
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            {trajectory.length > 0 && <Polyline positions={trajectory} color="var(--brand-primary)" weight={6} />}
            
            <Marker position={[state.lat, state.lon]}>
              <Popup>
                Speed: {speedKmh} km/h <br />
                Accuracy: {state.accuracy.toFixed(1)} m
              </Popup>
            </Marker>
            
            <RecenterMap position={[state.lat, state.lon]} />
          </MapContainer>
        )}
        
        {/* Overlay HUD */}
        <div style={{ 
          position: 'absolute', bottom: '20px', left: '20px', zIndex: 1000, 
          background: 'var(--bg-surface-elevated)', padding: 'var(--space-4)',
          borderRadius: 'var(--radius-md)', border: '1px solid var(--border-light)',
          boxShadow: 'var(--shadow-md)',
          display: 'flex', gap: 'var(--space-6)'
        }}>
           <div>
             <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Current Speed</div>
             <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{state.lat === null ? "--" : speedKmh} <span style={{fontSize: '1rem'}}>km/h</span></div>
           </div>
           
           <div style={{ borderLeft: '1px solid var(--border-light)', paddingLeft: 'var(--space-4)' }}>
             <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>GNSS Status</div>
             <div style={{ fontSize: '1rem', fontWeight: 'bold', color: state.mode.includes('GOOD') ? 'var(--success)' : 'var(--warning)', marginTop: 'var(--space-1)' }}>
                {state.mode.replace('_', ' ')}
             </div>
             <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Accuracy: {state.accuracy.toFixed(1)} m</div>
           </div>
        </div>
      </div>
    </div>
  );
}
