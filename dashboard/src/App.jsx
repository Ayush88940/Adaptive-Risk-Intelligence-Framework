import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, Cell 
} from 'recharts';
import { Shield, Activity, BarChart3, Clock, ArrowUpRight, ArrowDownRight, RefreshCcw, Search, Loader2, Trash2, CheckCircle2, AlertTriangle } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const App = () => {
  const [builds, setBuilds] = useState([]);
  const [stats, setStats] = useState({ avg_risk: 0, total_builds: 0, avg_sdi: 0 });
  const [loading, setLoading] = useState(true);
  const [repoUrl, setRepoUrl] = useState('');
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [scanError, setScanError] = useState(null);

  const fetchData = async () => {
    try {
      const [buildsRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE}/builds`),
        axios.get(`${API_BASE}/stats`)
      ]);
      setBuilds(buildsRes.data.reverse());
      setStats(statsRes.data);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch data", err);
      // Hard fallback for visually demonstrating UI if backend drops
      const mockBuilds = [
          { build_id: 'v1.0.1', risk_score: 15, drift: 0, sdi: 4, decision: 'ALLOW', timestamp: new Date().toISOString() },
          { build_id: 'v1.0.2', risk_score: 25, drift: 10, sdi: 6, decision: 'ALLOW', timestamp: new Date().toISOString() },
          { build_id: 'v1.0.3', risk_score: 85, drift: 60, sdi: 15, decision: 'BLOCK', timestamp: new Date().toISOString() }
      ];
      setBuilds(mockBuilds);
      setStats({ avg_risk: 41.6, total_builds: 3, avg_sdi: 8.3 });
      setLoading(false);
    }
  };

  const handleScan = async (e) => {
    e.preventDefault();
    if (!repoUrl) return;
    setScanning(true); setScanResult(null); setScanError(null);
    try {
      const res = await axios.post(`${API_BASE}/scan-repo`, { repo_url: repoUrl });
      setScanResult(res.data);
      fetchData();
      setRepoUrl('');
    } catch (err) {
      const msg = err.response?.data?.detail || err.message;
      setScanError(`Scan failed: ${msg}`);
    } finally {
      setScanning(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  // Custom tooltips for premium charts
  const CustomTooltipArea = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ background: 'rgba(20,25,38,0.9)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', padding: '12px', borderRadius: '8px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}>
          <p style={{ margin: '0 0 5px', color: '#8b949e', fontSize: '12px' }}>{label}</p>
          <p style={{ margin: 0, color: '#58a6ff', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={14}/> Score: {payload[0].value.toFixed(1)}
          </p>
        </div>
      );
    }
    return null;
  };

  const CustomTooltipBar = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const isPositive = payload[0].value > 0;
      return (
        <div style={{ background: 'rgba(20,25,38,0.9)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', padding: '12px', borderRadius: '8px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}>
          <p style={{ margin: '0 0 5px', color: '#8b949e', fontSize: '12px' }}>{label}</p>
          <p style={{ margin: 0, color: isPositive ? '#f85149' : '#3fb950', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
            {isPositive ? <ArrowUpRight size={14}/> : <ArrowDownRight size={14}/>} 
            Drift: {Math.abs(payload[0].value).toFixed(1)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="header stagger-1">
        <div>
          <h1>
            <Shield size={36} color="#58a6ff" style={{ filter: 'drop-shadow(0 0 10px rgba(88,166,255,0.4))' }} />
            Risk-Aware CI/CD
          </h1>
          <p>Adaptive Security Gating & Threat Assessment Engine</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={fetchData} className="btn-icon" title="Refresh Data">
            <RefreshCcw size={18} /> Refresh
          </button>
          <button 
            onClick={async () => {
              if (window.confirm('Clear all build history?')) {
                await axios.delete(`${API_BASE}/reset`);
                setBuilds([]);
                setStats({ avg_risk: 0, total_builds: 0, avg_sdi: 0 });
              }
            }}
            className="btn-icon btn-danger"
            title="Clear Data"
          >
            <Trash2 size={18} /> Format
          </button>
        </div>
      </header>

      {/* Top Stats */}
      <div className="grid grid-3 stagger-2" style={{ marginBottom: '2rem' }}>
        <div className="glass-card text-center">
          <div className="stat-card-header"><Activity size={20} color="#58a6ff"/> System Avg Risk</div>
          <div className="stat-value">{stats.avg_risk.toFixed(1)}</div>
        </div>
        <div className="glass-card text-center">
          <div className="stat-card-header"><Clock size={20} color="#bc8cff"/> Pipelines Analyzed</div>
          <div className="stat-value">{stats.total_builds}</div>
        </div>
        <div className="glass-card text-center">
          <div className="stat-card-header"><BarChart3 size={20} color="#3fb950"/> Security Debt Index</div>
          <div className="stat-value">{stats.avg_sdi.toFixed(1)}</div>
        </div>
      </div>

      <div className="grid grid-2 stagger-3" style={{ marginBottom: '2rem' }}>
        {/* Repo Scanner */}
        <div className="glass-card">
          <h3>Analyze External Repository</h3>
          <p className="text-muted" style={{ marginBottom: '1.5rem', fontSize: '0.95rem' }}>
            Enter a public GitHub repository link below to perform a liveContext-Aware risk scan against production configurations.
          </p>
          <form onSubmit={handleScan} className="scanner-form">
            <div className="input-group">
              <Search className="input-icon" size={20} />
              <input 
                type="text" 
                placeholder="https://github.com/username/repo"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                disabled={scanning}
              />
            </div>
            <button type="submit" className="btn-primary" disabled={scanning || !repoUrl}>
              {scanning ? <><Loader2 className="spin" size={18} /> Scanning</> : "Assess Risk"}
            </button>
          </form>

          {scanError && (
            <div className="result-badge bg-danger">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600 }}>
                <AlertTriangle size={20} color="#f85149" /> Error
              </div>
              <p style={{ margin: 0, fontSize: '0.95rem' }}>{scanError}</p>
            </div>
          )}

          {scanResult && !scanning && (
            <div className={`result-badge ${scanResult.decision === 'BLOCK' ? 'bg-danger' : 'bg-success'}`}>
              <div className="result-main">
                <span className="label" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: scanResult.decision === 'BLOCK' ? '#f85149' : '#3fb950' }}>
                  {scanResult.decision === 'BLOCK' ? <AlertTriangle size={24}/> : <CheckCircle2 size={24}/>}
                  {scanResult.decision}
                </span>
                <span className="score">{scanResult.risk_score}</span>
              </div>
              <p className="recommendation">{scanResult.recommendation}</p>
              <p className="details">Uncovered {scanResult.vuln_count} risk artifacts using adaptive weighting.</p>
            </div>
          )}
        </div>

        {/* Drift Chart */}
        <div className="glass-card" style={{ height: '350px' }}>
          <h3>Security Drift Analysis</h3>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={builds}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="build_id" stroke="#8b949e" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
              <YAxis stroke="#8b949e" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
              <Tooltip content={<CustomTooltipBar />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
              <Bar dataKey="drift" radius={[4,4,0,0]}>
                {builds.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.drift > 0 ? '#f85149' : '#3fb950'} fillOpacity={0.8} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Main Trend Line and Table */}
      <div className="glass-card stagger-4" style={{ marginBottom: '2rem', height: '400px' }}>
        <h3>Pipeline Risk Trend</h3>
        <ResponsiveContainer width="100%" height="85%">
          <AreaChart data={builds}>
            <defs>
              <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#58a6ff" stopOpacity={0.5}/>
                <stop offset="95%" stopColor="#58a6ff" stopOpacity={0.0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="build_id" stroke="#8b949e" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
            <YAxis stroke="#8b949e" domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltipArea />} />
            <Area type="monotone" dataKey="risk_score" stroke="#58a6ff" fillOpacity={1} fill="url(#colorRisk)" strokeWidth={3} activeDot={{ r: 6, fill: '#fff', stroke: '#58a6ff', strokeWidth: 2 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="glass-card stagger-5">
        <h3>Deployment Gate Ledger</h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Identifier</th>
                <th>Gate Decision</th>
                <th>Risk Score</th>
                <th>Drift Delta</th>
                <th>Cumulative SDI</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {[...builds].reverse().map((build, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600, fontFamily: 'JetBrains Mono, monospace' }}>{build.build_id}</td>
                  <td>
                    <span className={`status-badge ${build.decision === 'BLOCK' ? 'status-block' : 'status-allow'}`}>
                      {build.decision}
                    </span>
                  </td>
                  <td>
                    <div className="score-flex">
                      <div className="score-bar-bg">
                        <div className="score-bar-fill" style={{ width: `${build.risk_score}%`, background: build.risk_score > 70 ? '#f85149' : '#58a6ff' }}></div>
                      </div>
                      <span style={{ fontWeight: 600 }}>{build.risk_score.toFixed(1)}</span>
                    </div>
                  </td>
                  <td>
                    <span style={{ 
                      color: build.drift > 0 ? '#f85149' : build.drift < 0 ? '#3fb950' : '#8b949e',
                      display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600
                    }}>
                      {build.drift > 0 ? <ArrowUpRight size={16} /> : build.drift < 0 ? <ArrowDownRight size={16} /> : null}
                      {Math.abs(build.drift).toFixed(1)}
                    </span>
                  </td>
                  <td style={{ fontWeight: 500 }}>{build.sdi.toFixed(1)}</td>
                  <td className="text-muted" style={{ fontSize: '0.85rem' }}>{new Date(build.timestamp).toLocaleString()}</td>
                </tr>
              ))}
              {builds.length === 0 && (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '3rem', color: '#8b949e' }}>
                    No security evaluations found. Commit code to trigger an automated scan.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default App;
