import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Copy, Trash2, CheckCircle, AlertTriangle, Smartphone, Car } from 'lucide-react';

export default function Profiles() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProfile, setEditingProfile] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    vehicle_type: 'CAR',
    phone_mounting: 'DASHBOARD',
    external_imu: false,
    nav_prefs: { avoid_tolls: false, prefer_offline: true }
  });

  const fetchProfiles = async () => {
    setLoading(true);
    try {
      // Use the dummy token expected by the backend
      const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vX2RldmljZSJ9.this_is_a_mock_signature";
      const res = await fetch('http://127.0.0.1:8000/profiles', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setProfiles(data);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchProfiles();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vX2RldmljZSJ9.this_is_a_mock_signature";
    
    const method = editingProfile ? 'PUT' : 'POST';
    const url = editingProfile 
      ? `http://127.0.0.1:8000/profiles/${editingProfile.id}` 
      : 'http://127.0.0.1:8000/profiles';

    try {
      await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      setShowModal(false);
      setEditingProfile(null);
      fetchProfiles();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this profile?')) return;
    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vX2RldmljZSJ9.this_is_a_mock_signature";
    try {
      await fetch(`http://127.0.0.1:8000/profiles/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      fetchProfiles();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDuplicate = async (profile) => {
    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vX2RldmljZSJ9.this_is_a_mock_signature";
    const cloneData = {
      name: `${profile.name} (Copy)`,
      vehicle_type: profile.vehicle_type,
      phone_mounting: profile.phone_mounting,
      external_imu: profile.external_imu,
      nav_prefs: profile.nav_prefs
    };
    try {
      await fetch('http://127.0.0.1:8000/profiles', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(cloneData)
      });
      fetchProfiles();
    } catch (e) {
      console.error(e);
    }
  };

  const openCreate = () => {
    setFormData({
      name: '',
      vehicle_type: 'CAR',
      phone_mounting: 'DASHBOARD',
      external_imu: false,
      nav_prefs: { avoid_tolls: false, prefer_offline: true }
    });
    setEditingProfile(null);
    setShowModal(true);
  };

  const openEdit = (profile) => {
    setFormData({
      name: profile.name,
      vehicle_type: profile.vehicle_type,
      phone_mounting: profile.phone_mounting,
      external_imu: profile.external_imu,
      nav_prefs: profile.nav_prefs || { avoid_tolls: false, prefer_offline: true }
    });
    setEditingProfile(profile);
    setShowModal(true);
  };

  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-6)' }}>
        <div>
          <h2>Vehicle & Sensor Profiles</h2>
          <p style={{ color: 'var(--text-muted)' }}>Manage your vehicle configurations and calibration settings.</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>
          <Plus size={20} style={{ marginRight: '8px' }} />
          New Profile
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 'var(--space-8)' }}>Loading...</div>
      ) : profiles.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 'var(--space-8)' }}>
          <Car size={48} color="var(--text-muted)" style={{ margin: '0 auto var(--space-4)' }} />
          <h3>No profiles found</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-4)' }}>Create a profile to start tracking calibration and preferences for a vehicle.</p>
          <button className="btn btn-primary" onClick={openCreate}>Create Profile</button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 'var(--space-6)' }}>
          {profiles.map(p => (
            <div key={p.id} className="card" style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-4)' }}>
                <div>
                  <h3 style={{ marginBottom: '4px' }}>{p.name}</h3>
                  <div style={{ display: 'flex', gap: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Car size={16} /> {p.vehicle_type}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Smartphone size={16} /> {p.phone_mounting}</span>
                  </div>
                </div>
                
                {p.is_calibrated ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--status-success)', fontSize: '0.8rem', fontWeight: 'bold', background: 'var(--bg-elevated)', padding: '4px 8px', borderRadius: '12px' }}>
                    <CheckCircle size={14} /> Calibrated
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--status-warning)', fontSize: '0.8rem', fontWeight: 'bold', background: 'var(--bg-elevated)', padding: '4px 8px', borderRadius: '12px' }}>
                    <AlertTriangle size={14} /> Uncalibrated
                  </div>
                )}
              </div>

              <div style={{ background: 'var(--bg-main)', padding: 'var(--space-3)', borderRadius: '8px', marginBottom: 'var(--space-4)', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>External IMU:</span> <span>{p.external_imu ? 'Yes' : 'No'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Last Updated:</span> <span>{new Date(p.updated_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', marginTop: 'auto' }}>
                <button className="btn" style={{ flex: 1 }} onClick={() => openEdit(p)}>
                  <Edit2 size={16} style={{ marginRight: '6px' }} /> Edit
                </button>
                <button className="btn" style={{ flex: 1 }} onClick={() => handleDuplicate(p)}>
                  <Copy size={16} style={{ marginRight: '6px' }} /> Clone
                </button>
                <button className="btn" style={{ color: 'var(--status-error)' }} onClick={() => handleDelete(p.id)}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div className="card" style={{ maxWidth: '500px', width: '100%', padding: 'var(--space-6)' }}>
            <h2 style={{ marginBottom: 'var(--space-4)' }}>{editingProfile ? 'Edit Profile' : 'New Profile'}</h2>
            <form onSubmit={handleSave}>
              <div style={{ marginBottom: 'var(--space-4)' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Profile Name</label>
                <input required type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} style={{ width: '100%', padding: '12px', background: 'var(--bg-main)', border: '1px solid var(--border-light)', borderRadius: '8px', color: 'var(--text-primary)' }} />
              </div>
              <div style={{ marginBottom: 'var(--space-4)' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Vehicle Type</label>
                <select value={formData.vehicle_type} onChange={e => setFormData({...formData, vehicle_type: e.target.value})} style={{ width: '100%', padding: '12px', background: 'var(--bg-main)', border: '1px solid var(--border-light)', borderRadius: '8px', color: 'var(--text-primary)' }}>
                  <option value="CAR">Car / SUV</option>
                  <option value="MOTORCYCLE">Motorcycle</option>
                  <option value="BICYCLE">Bicycle</option>
                  <option value="PEDESTRIAN">Pedestrian</option>
                </select>
              </div>
              <div style={{ marginBottom: 'var(--space-4)' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Phone Mounting</label>
                <select value={formData.phone_mounting} onChange={e => setFormData({...formData, phone_mounting: e.target.value})} style={{ width: '100%', padding: '12px', background: 'var(--bg-main)', border: '1px solid var(--border-light)', borderRadius: '8px', color: 'var(--text-primary)' }}>
                  <option value="DASHBOARD">Dashboard Mount</option>
                  <option value="WINDSHIELD">Windshield Mount</option>
                  <option value="CUP_HOLDER">Cup Holder</option>
                  <option value="POCKET">Pocket (Loose)</option>
                </select>
              </div>
              <div style={{ marginBottom: 'var(--space-6)' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={formData.external_imu} onChange={e => setFormData({...formData, external_imu: e.target.checked})} />
                  Use External IMU (via Bluetooth)
                </label>
              </div>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button type="button" className="btn" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Profile</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
