import React from 'react';
import { NavLink } from 'react-router-dom';
import { Activity, ShieldCheck, Map, Smartphone, Server, Cpu } from 'lucide-react';

export default function Landing() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: 'var(--space-8) 0' }}>
        <h1 style={{ fontSize: '3.5rem', marginBottom: 'var(--space-4)', background: 'linear-gradient(45deg, var(--brand-primary), #4facfe)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Navigators
        </h1>
        <p style={{ fontSize: '1.5rem', color: 'var(--text-secondary)', maxWidth: '800px', margin: '0 auto', marginBottom: 'var(--space-6)' }}>
          Intelligent Dead Reckoning & AI Speed Estimation for seamless navigation in GNSS-denied environments.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-4)' }}>
          <NavLink to="/dashboard" className="btn btn-primary" style={{ padding: 'var(--space-3) var(--space-6)', fontSize: '1.1rem' }}>
            Open Dashboard
          </NavLink>
          <NavLink to="/health" className="btn btn-outline" style={{ padding: 'var(--space-3) var(--space-6)', fontSize: '1.1rem' }}>
            System Health Check
          </NavLink>
        </div>
      </section>

      {/* How it Works Section */}
      <section>
        <h2 style={{ textAlign: 'center', marginBottom: 'var(--space-6)' }}>Core Technologies</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-6)' }}>
          
          <div className="card" style={{ padding: 'var(--space-6)' }}>
            <Activity size={32} color="var(--brand-primary)" style={{ marginBottom: 'var(--space-4)' }} />
            <h3 style={{ marginBottom: 'var(--space-2)' }}>AI Speed Estimation</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              Deep learning models process raw IMU data locally on Android to estimate forward vehicle velocity without wheel-speed sensors or GPS.
            </p>
          </div>

          <div className="card" style={{ padding: 'var(--space-6)' }}>
            <Map size={32} color="var(--brand-primary)" style={{ marginBottom: 'var(--space-4)' }} />
            <h3 style={{ marginBottom: 'var(--space-2)' }}>Offline Map Matching</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              Snaps dead-reckoned trajectories to a local graph-based road network to constrain drift during extended outages.
            </p>
          </div>

          <div className="card" style={{ padding: 'var(--space-6)' }}>
            <Cpu size={32} color="var(--brand-primary)" style={{ marginBottom: 'var(--space-4)' }} />
            <h3 style={{ marginBottom: 'var(--space-2)' }}>Error-State Kalman Filter</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              Advanced sensor fusion continuously estimates and corrects inertial drift by blending GNSS (when available) with AI-derived kinematics.
            </p>
          </div>

        </div>
      </section>

      {/* Platform Section */}
      <section>
        <h2 style={{ textAlign: 'center', marginBottom: 'var(--space-6)' }}>Platform Architecture</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-6)', justifyContent: 'center' }}>
          
          <div className="card" style={{ flex: '1 1 300px', maxWidth: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: 'var(--space-6)' }}>
            <Smartphone size={48} color="var(--status-dr)" style={{ marginBottom: 'var(--space-4)' }} />
            <h3>Android Edge App</h3>
            <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-2)' }}>
              Handles sensor acquisition, alignment calibration, external IMU bridging, and on-device PyTorch model inference in the background.
            </p>
          </div>

          <div className="card" style={{ flex: '1 1 300px', maxWidth: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: 'var(--space-6)' }}>
            <Server size={48} color="var(--status-success)" style={{ marginBottom: 'var(--space-4)' }} />
            <h3>Cloud & Telemetry</h3>
            <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-2)' }}>
              Secure WebSocket syncing, session persistence, OTA AI model distribution, and regression validation benchmarking.
            </p>
          </div>

        </div>
      </section>

      {/* Footer / Links */}
      <footer style={{ marginTop: 'var(--space-8)', paddingTop: 'var(--space-6)', borderTop: '1px solid var(--border-light)', textAlign: 'center', color: 'var(--text-muted)' }}>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-6)', marginBottom: 'var(--space-4)' }}>
          <NavLink to="/demo" style={{ color: 'var(--brand-primary)' }}>View Demo Scenario</NavLink>
          <a href="https://github.com/Navigators/Navigators/tree/main/docs" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--brand-primary)' }}>Read Documentation</a>
          <a href="mailto:contact@navigators.com" style={{ color: 'var(--brand-primary)' }}>Contact Support</a>
        </div>
        <p>Developed by Navigators</p>
      </footer>
    </div>
  );
}
