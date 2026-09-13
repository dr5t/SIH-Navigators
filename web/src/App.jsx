import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Activity, Map, Radio, List, Settings, HelpCircle, FileText, LayoutDashboard } from 'lucide-react';
import './styles.css';
import { TelemetryProvider } from './telemetry';


import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Navigation from './pages/Navigation';
import Diagnostics from './pages/Diagnostics';
import SessionsList from './pages/SessionsList';
import SessionReport from './pages/SessionReport';
import Benchmark from './pages/Benchmark';
import Demo from './pages/Demo';
import SystemHealth from './pages/SystemHealth';
import ExperimentManager from './pages/ExperimentManager';
import DeviceCompatibility from './pages/DeviceCompatibility';
import Profiles from './pages/Profiles';
import Lab from './pages/Lab';

import Feedback from './pages/Feedback';
import FeedbackDetail from './pages/FeedbackDetail';

const History = () => <div className="card"><h2>History</h2><p>Diagnostic history.</p></div>;
const SettingsPage = () => <div className="settings-page"><header className="page-heading"><div><span className="eyebrow">PREFERENCES & SYSTEM</span><h1>Settings</h1></div></header>{[
  ['Navigation & sensors', 'Manage vehicle profiles and sensor calibration.', '/profiles', 'Vehicle profiles'],
  ['Maps', 'Viewed tiles use the browser cache. Use Android for persistent offline maps.', '/navigation', 'Open map'],
  ['AI & diagnostics', 'Inspect measured runtime and system availability.', '/health', 'System health'],
  ['Data & privacy', 'Review recorded trips and exports.', '/sessions', 'Trip log'],
  ['Appearance', 'Night instruments · high contrast surfaces and restrained navigation accents.', null, null],
  ['Support', 'Report a problem or review product documentation.', '/feedback', 'Feedback & support'],
  ['About', 'NAVIGATORS · Developed by Navigators', '/welcome', 'About Navigators']
].map(([title,description,path,label]) => <section className="setting-row" key={title}><div><h2>{title}</h2><p>{description}</p></div>{path && <NavLink className="btn btn-outline" to={path}>{label}</NavLink>}</section>)}</div>;
const FAQ = () => <div className="card"><h2>FAQ</h2><p>Help and questions.</p></div>;
const Privacy = () => <div className="card"><h2>Privacy Policy</h2><p>Legal terms.</p></div>;
const Terms = () => <div className="card"><h2>Terms & Conditions</h2><p>Legal terms.</p></div>;
const Cookies = () => <div className="card"><h2>Cookie Policy</h2><p>Legal terms.</p></div>;
const DocsHub = () => <div className="card"><h2>Documentation Hub</h2><p>Read the user guide and API docs.</p></div>;
const NotFound = () => <div className="card"><h2>404</h2><p>Page not found.</p><NavLink to="/" className="btn btn-primary">Go to Landing</NavLink></div>;

const primary = [
  ['/dashboard', 'Navigation', Activity], ['/navigation', 'Map', Map],
  ['/sessions', 'Trips', List], ['/diagnostics', 'Diagnostics', Radio], ['/settings', 'Settings', Settings]
];
const AppShell = ({ children }) => <div className="app-shell">
  <aside className="sidebar">
    <NavLink to="/dashboard" className="brand"><img src="/logo192.png" alt=""/><span>NAVIGATORS<small>NAVIGATION SYSTEMS</small></span></NavLink>
    <nav aria-label="Primary navigation" className="primary-nav">{primary.map(([path, label, Icon]) => <NavLink key={path} to={path} className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}><Icon size={19} strokeWidth={1.6}/><span>{label}</span></NavLink>)}</nav>
    <details className="engineering-nav"><summary>Engineering tools</summary><nav aria-label="Engineering tools">{[['/profiles','Vehicle profiles'],['/lab','Navigation lab'],['/experiments','Experiments'],['/health','System health'],['/compatibility','Device compatibility'],['/benchmark','Benchmarks'],['/demo','Replay demo'],['/feedback','Feedback'],['/docs','Documentation'],['/welcome','About Navigators']].map(([path,label]) => <NavLink key={path} to={path}>{label}</NavLink>)}</nav></details>
    <footer className="sidebar-footer"><span>Developed by Navigators</span><div><NavLink to="/privacy">Privacy</NavLink><NavLink to="/terms">Terms</NavLink><NavLink to="/cookies">Cookies</NavLink></div></footer>
  </aside>
  <main className="main-content" id="main-content">{children}</main>
</div>;

export default function App() {
  return (
    <Router>
      <TelemetryProvider><AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/welcome" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/navigation" element={<Navigation />} />
          <Route path="/health" element={<SystemHealth />} />
          <Route path="/compatibility" element={<DeviceCompatibility />} />
          <Route path="/diagnostics" element={<Diagnostics />} />
          <Route path="/experiments" element={<ExperimentManager />} />
          <Route path="/profiles" element={<Profiles />} />
          <Route path="/lab" element={<Lab />} />
          <Route path="/sessions" element={<SessionsList />} />
          <Route path="/sessions/:id" element={<SessionReport />} />
          <Route path="/feedback" element={<Feedback />} />
          <Route path="/feedback/:id" element={<FeedbackDetail />} />
          <Route path="/benchmark" element={<Benchmark />} />
          <Route path="/demo" element={<Demo />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/docs" element={<DocsHub />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/cookies" element={<Cookies />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AppShell></TelemetryProvider>
    </Router>
  );
}
