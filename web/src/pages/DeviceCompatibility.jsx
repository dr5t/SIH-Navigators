import React from 'react';
import { Smartphone, CheckCircle2, XCircle } from 'lucide-react';

export default function DeviceCompatibility() {
  const devices = [
    { name: "Pixel 8 Pro", acc: true, gyro: true, mag: true, gnss: true, rate: true, ai: true, imu: true, offline: true },
    { name: "Galaxy S24", acc: true, gyro: true, mag: true, gnss: true, rate: true, ai: true, imu: true, offline: true },
    { name: "Galaxy A54", acc: true, gyro: true, mag: false, gnss: true, rate: false, ai: true, imu: false, offline: true },
    { name: "OnePlus 12", acc: true, gyro: true, mag: true, gnss: true, rate: true, ai: true, imu: true, offline: true },
  ];

  const renderIcon = (val) => {
    return val ? <CheckCircle2 color="var(--success)" size={20} /> : <XCircle color="var(--error)" size={20} />;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', height: '100%' }}>
      <header>
        <h2 style={{ marginBottom: 'var(--space-2)' }}>Device Compatibility Center</h2>
        <p style={{ color: 'var(--text-muted)' }}>Validate whether specific Android hardware supports the Navigators edge stack.</p>
      </header>

      <div className="card">
        <h3 style={{ marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Smartphone size={20} color="var(--brand-primary)" /> Hardware Matrix
        </h3>
        
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', textAlign: 'center', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-light)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                <th style={{ padding: 'var(--space-2) 0', textAlign: 'left' }}>Device Model</th>
                <th style={{ padding: 'var(--space-2) 0' }}>Accelerometer</th>
                <th style={{ padding: 'var(--space-2) 0' }}>Gyroscope</th>
                <th style={{ padding: 'var(--space-2) 0' }}>Magnetometer</th>
                <th style={{ padding: 'var(--space-2) 0' }}>GNSS (Raw)</th>
                <th style={{ padding: 'var(--space-2) 0' }}>Rate (100Hz+)</th>
                <th style={{ padding: 'var(--space-2) 0' }}>AI Inference</th>
                <th style={{ padding: 'var(--space-2) 0' }}>Ext IMU Support</th>
                <th style={{ padding: 'var(--space-2) 0' }}>Offline Maps</th>
              </tr>
            </thead>
            <tbody>
              {devices.map((d, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border-light)' }}>
                  <td style={{ padding: 'var(--space-3) 0', fontWeight: 'bold', textAlign: 'left' }}>{d.name}</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{renderIcon(d.acc)}</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{renderIcon(d.gyro)}</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{renderIcon(d.mag)}</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{renderIcon(d.gnss)}</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{renderIcon(d.rate)}</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{renderIcon(d.ai)}</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{renderIcon(d.imu)}</td>
                  <td style={{ padding: 'var(--space-3) 0' }}>{renderIcon(d.offline)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="card">
        <h3>Minimum Requirements</h3>
        <ul style={{ marginTop: 'var(--space-4)', lineHeight: '1.6', color: 'var(--text-secondary)' }}>
          <li><strong>Sensors:</strong> Accelerometer and Gyroscope must support uncalibrated output at 100Hz or higher.</li>
          <li><strong>GNSS:</strong> Device must support Android Location Manager with Fine Location permissions. Raw GNSS measurements (Carrier Phase) are recommended but not required.</li>
          <li><strong>AI Inference:</strong> Device must support PyTorch Mobile (Android 7.0+).</li>
          <li><strong>Storage:</strong> Minimum 500MB free for offline map graph caching.</li>
        </ul>
      </div>

    </div>
  );
}
