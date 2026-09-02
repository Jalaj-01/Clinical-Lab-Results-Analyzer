import React, { useState } from 'react';
import LabInput from './components/LabInput';
import ResultsDisplay from './components/ResultsDisplay';

const API = 'http://localhost:8000';

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(null);

  const analyze = async (labs) => {
    setLoading(true);
    setApiError(null);
    try {
      const res = await fetch(`${API}/analyze_labs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ labs }),
      });
      if (!res.ok) {
        const e = await res.json().catch(() => ({}));
        throw new Error(e.detail || `Server error ${res.status}`);
      }
      setData(await res.json());
    } catch (err) {
      setApiError(err.message || 'Could not reach the backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Top bar */}
      <header className="topbar">
        <div className="topbar-logo">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
          </svg>
        </div>
        <span className="topbar-name">Lab Results Analyzer</span>
        <span className="topbar-sep" />
        <span className="topbar-sub">Classify · Route · Explain</span>

        {apiError && (
          <span style={{ marginLeft: 'auto', fontSize: 12, color: '#dc2626', fontWeight: 600 }}>
            ⚠ {apiError}
          </span>
        )}
      </header>

      {/* Sidebar */}
      <LabInput onAnalyze={analyze} isLoading={loading} />

      {/* Results panel */}
      <div className="panel">
        <ResultsDisplay data={data} isLoading={loading} />
      </div>
    </div>
  );
}
