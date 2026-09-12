import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Activity, Map, Radio, List, Settings, HelpCircle, FileText, LayoutDashboard } from 'lucide-react';
import './styles.css';

import Dashboard from './pages/Dashboard';
import Navigation from './pages/Navigation';
import Diagnostics from './pages/Diagnostics';
import SessionsList from './pages/SessionsList';
import SessionReport from './pages/SessionReport';
import Benchmark from './pages/Benchmark';
import Demo from './pages/Demo';

const History = () => <div className="card"><h2>History</h2><p>Diagnostic history.</p></div>;
const SettingsPage = () => <div className="card"><h2>Settings</h2><p>App configuration.</p></div>;
const FAQ = () => <div className="card"><h2>FAQ</h2><p>Help and questions.</p></div>;
const Privacy = () => <div className="card"><h2>Privacy Policy</h2><p>Legal terms.</p></div>;
const Terms = () => <div className="card"><h2>Terms & Conditions</h2><p>Legal terms.</p></div>;
const Cookies = () => <div className="card"><h2>Cookie Policy</h2><p>Legal terms.</p></div>;
const NotFound = () => <div className="card"><h2>404</h2><p>Page not found.</p><NavLink to="/" className="btn btn-primary">Go to Dashboard</NavLink></div>;

const AppShell = ({ children }) => {
  return (
    <div className="app-shell">
      <nav className="sidebar">
        <div style={{ padding: 'var(--space-4)', fontWeight: 'bold', borderBottom: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity color="var(--brand-primary)" /> Navigators
        </div>
        
        <div style={{ padding: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <NavLink to="/" className={({isActive}) => `btn ${isActive ? 'btn-primary' : 'btn-outline'}`} style={{justifyContent: 'flex-start', border: 'none'}}>
            <LayoutDashboard size={18} style={{marginRight: '8px'}}/> Dashboard
          </NavLink>
          <NavLink to="/navigation" className={({isActive}) => `btn ${isActive ? 'btn-primary' : 'btn-outline'}`} style={{justifyContent: 'flex-start', border: 'none'}}>
            <Map size={18} style={{marginRight: '8px'}}/> Navigation
          </NavLink>
          <NavLink to="/diagnostics" className={({isActive}) => `btn ${isActive ? 'btn-primary' : 'btn-outline'}`} style={{justifyContent: 'flex-start', border: 'none'}}>
            <Radio size={18} style={{marginRight: '8px'}}/> Diagnostics
          </NavLink>
          <NavLink to="/sessions" className={({isActive}) => `btn ${isActive ? 'btn-primary' : 'btn-outline'}`} style={{justifyContent: 'flex-start', border: 'none'}}>
            <List size={18} style={{marginRight: '8px'}}/> Sessions
          </NavLink>
          <NavLink to="/benchmark" className={({isActive}) => `btn ${isActive ? 'btn-primary' : 'btn-outline'}`} style={{justifyContent: 'flex-start', border: 'none'}}>
            <Activity size={18} style={{marginRight: '8px'}}/> Benchmarks
          </NavLink>
          <NavLink to="/demo" className={({isActive}) => `btn ${isActive ? 'btn-primary' : 'btn-outline'}`} style={{justifyContent: 'flex-start', border: 'none'}}>
            <FileText size={18} style={{marginRight: '8px'}}/> Demo View
          </NavLink>
          <NavLink to="/settings" className={({isActive}) => `btn ${isActive ? 'btn-primary' : 'btn-outline'}`} style={{justifyContent: 'flex-start', border: 'none'}}>
            <Settings size={18} style={{marginRight: '8px'}}/> Settings
          </NavLink>
          <NavLink to="/faq" className={({isActive}) => `btn ${isActive ? 'btn-primary' : 'btn-outline'}`} style={{justifyContent: 'flex-start', border: 'none'}}>
            <HelpCircle size={18} style={{marginRight: '8px'}}/> FAQ
          </NavLink>
        </div>
        
        <div style={{ marginTop: 'auto', padding: 'var(--space-4)', borderTop: '1px solid var(--border-light)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <div><NavLink to="/privacy" style={{color: 'inherit'}}>Privacy</NavLink> | <NavLink to="/terms" style={{color: 'inherit'}}>Terms</NavLink> | <NavLink to="/cookies" style={{color: 'inherit'}}>Cookies</NavLink></div>
          <div style={{marginTop: 'var(--space-2)'}}>Developed by Navigators</div>
        </div>
      </nav>
      
      <main className="main-content" style={{ padding: 'var(--space-6)' }}>
        {children}
      </main>
    </div>
  );
};

export default function App() {
  return (
    <Router>
      <AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/navigation" element={<Navigation />} />
          <Route path="/diagnostics" element={<Diagnostics />} />
          <Route path="/sessions" element={<SessionsList />} />
          <Route path="/sessions/:id" element={<SessionReport />} />
          <Route path="/benchmark" element={<Benchmark />} />
          <Route path="/demo" element={<Demo />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/cookies" element={<Cookies />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AppShell>
    </Router>
  );
}
