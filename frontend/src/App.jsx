import React, { useState, useEffect } from 'react';
import LabInput from './components/LabInput';
import ResultsDisplay from './components/ResultsDisplay';
import { Activity, ShieldAlert, Cpu, HeartPulse } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [resultsData, setResultsData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [backendHealth, setBackendHealth] = useState({ status: 'checking', llm_configured: false });

  // Check backend health on load
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
          const data = await res.json();
          setBackendHealth(data);
        } else {
          setBackendHealth({ status: 'offline', llm_configured: false });
        }
      } catch (e) {
        setBackendHealth({ status: 'offline', llm_configured: false });
      }
    };
    checkHealth();
  }, []);

  const handleAnalyzeLabs = async (labsArray) => {
    setIsLoading(true);
    setApiError(null);

    try {
      const response = await fetch(`${API_BASE}/analyze_labs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ labs: labsArray })
      });

      if (!response.ok) {
        let errorMsg = 'Failed to analyze lab results.';
        try {
          const errData = await response.json();
          errorMsg = errData.detail || errorMsg;
        } catch (_) {}
        throw new Error(errorMsg);
      }

      const data = await response.json();
      setResultsData(data);
    } catch (err) {
      setApiError(err.message || 'Unable to connect to the analysis backend server.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <header className="header">
        <div className="header-content">
          <div className="brand">
            <div className="brand-icon">
              <HeartPulse size={24} />
            </div>
            <div>
              <h1 className="brand-title">Clinical Lab Results Analyzer</h1>
              <p className="brand-subtitle">GenAI & MCP Medical Prioritization & Explanation Engine</p>
            </div>
          </div>

          <div className="system-status">
            <div
              className="status-dot"
              style={{
                backgroundColor:
                  backendHealth.status === 'healthy' ? '#10b981' : '#f59e0b'
              }}
            />
            <span>
              {backendHealth.status === 'healthy'
                ? `Backend Online ${backendHealth.llm_configured ? '(LLM Active)' : '(Fallback Mode)'}`
                : 'Backend Disconnected'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Body */}
      <main className="main-content">
        {/* Medical Safety Disclaimer */}
        <div className="safety-banner">
          <ShieldAlert size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Medical Demonstration Disclaimer:</strong> This application is for educational and clinical workflow demonstration purposes only. It is not intended for diagnostic use. All abnormal findings must be clinically correlated and reviewed by a qualified healthcare professional.
          </div>
        </div>

        {apiError && (
          <div className="error-message">
            <ShieldAlert size={16} />
            <span><strong>Analysis Error:</strong> {apiError}</span>
          </div>
        )}

        {/* Dashboard 2-Column Grid */}
        <div className="dashboard-grid">
          <LabInput onAnalyze={handleAnalyzeLabs} isLoading={isLoading} />
          <ResultsDisplay data={resultsData} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
}
