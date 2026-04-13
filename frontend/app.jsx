import React, { useState, useEffect } from 'react';
import * as api from './api.js';

function App() {
  const [platform, setPlatform] = useState('instagram');
  const [workflows, setWorkflows] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('home');

  useEffect(() => {
    // Stub: don't fetch yet in Phase 1
    // Phase 2+: call api.getWorkflows(platform).then(data => setWorkflows(data))
  }, [platform]);

  return (
    <div className="container">
      <header className="header">
        <h1>The Bot</h1>
        <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
          <option value="instagram">Instagram</option>
          <option value="twitter">Twitter</option>
          <option value="telegram">Telegram</option>
        </select>
      </header>

      <nav className="tabs">
        <button
          className={activeTab === 'home' ? 'active' : ''}
          onClick={() => setActiveTab('home')}
        >
          Home
        </button>
        <button
          className={activeTab === 'workflows' ? 'active' : ''}
          onClick={() => setActiveTab('workflows')}
        >
          Workflows
        </button>
        <button
          className={activeTab === 'sessions' ? 'active' : ''}
          onClick={() => setActiveTab('sessions')}
        >
          Sessions
        </button>
        <button
          className={activeTab === 'platforms' ? 'active' : ''}
          onClick={() => setActiveTab('platforms')}
        >
          Platforms
        </button>
      </nav>

      <main className="main">
        {activeTab === 'home' && (
          <section className="tab-content">
            <h2>Overview</h2>
            <div className="status-pills">
              <div className="pill running">Instagram: RUNNING</div>
              <div className="pill paused">Twitter: PAUSED</div>
              <div className="pill paused">Telegram: PAUSED</div>
            </div>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Triggers Matched</h3>
                <p className="stat-value">0</p>
              </div>
              <div className="stat-card">
                <h3>Messages Sent</h3>
                <p className="stat-value">0</p>
              </div>
              <div className="stat-card">
                <h3>Active Sessions</h3>
                <p className="stat-value">0</p>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'workflows' && (
          <section className="tab-content">
            <h2>Workflows</h2>
            <button className="btn-primary">New Workflow</button>
            <div className="workflows-grid">
              <p>Loading workflows...</p>
            </div>
          </section>
        )}

        {activeTab === 'sessions' && (
          <section className="tab-content">
            <h2>Message Sessions</h2>
            <select>
              <option value="">All States</option>
              <option value="RUNNING">Running</option>
              <option value="COMPLETED">Completed</option>
            </select>
            <div className="sessions-list">
              <p>No sessions yet.</p>
            </div>
          </section>
        )}

        {activeTab === 'platforms' && (
          <section className="tab-content">
            <h2>Platforms</h2>
            <div className="platform-cards">
              <div className="platform-card">
                <h3>Instagram</h3>
                <p>Status: <strong>Enabled</strong></p>
                <button className="btn-secondary">Pause</button>
              </div>
              <div className="platform-card">
                <h3>Twitter</h3>
                <p>Status: <strong>Disabled</strong></p>
                <button className="btn-secondary">Enable</button>
              </div>
              <div className="platform-card">
                <h3>Telegram</h3>
                <p>Status: <strong>Disabled</strong></p>
                <button className="btn-secondary">Enable</button>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
