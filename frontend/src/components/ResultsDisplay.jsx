import React from 'react';
import SeverityBadge from './SeverityBadge';

function EmptyPanel() {
  return (
    <div className="empty">
      <svg className="empty-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414A1 1 0 0 1 19 9.414V19a2 2 0 0 1-2 2z"/>
      </svg>
      <p className="empty-title">No results to display</p>
      <p className="empty-hint">Load a sample dataset or enter values manually, then click Run Analysis</p>
    </div>
  );
}

function LoadingPanel() {
  return (
    <div className="loading-panel">
      <svg className="spin" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2.2">
        <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
      </svg>
      <p>Classifying results and generating clinical explanations...</p>
    </div>
  );
}

export default function ResultsDisplay({ data, isLoading }) {
  if (isLoading) return <LoadingPanel />;
  if (!data || !data.results || data.results.length === 0) return <EmptyPanel />;

  const { results, critical_count, warning_count, normal_count, total_analyzed } = data;

  return (
    <>
      {/* Summary Stats */}
      <div className="stats-row">
        <div className="stat-card red">
          <span className="stat-indicator red" />
          <div>
            <div className="stat-number">{critical_count}</div>
            <div className="stat-label">Critical</div>
          </div>
        </div>
        <div className="stat-card amber">
          <span className="stat-indicator amber" />
          <div>
            <div className="stat-number">{warning_count}</div>
            <div className="stat-label">Warning</div>
          </div>
        </div>
        <div className="stat-card green">
          <span className="stat-indicator green" />
          <div>
            <div className="stat-number">{normal_count}</div>
            <div className="stat-label">Normal</div>
          </div>
        </div>
      </div>

      {/* Result Cards */}
      {results.map((item, idx) => {
        const s = (item.status || 'unknown').toLowerCase();
        return (
          <div key={idx} className={`result-card is-${s}`}>
            <div className="result-card-header">
              <div>
                <div className="result-name">{item.test_name}</div>
                <div className="result-meta">Ref: {item.reference_range}</div>
              </div>
              <div className="result-right">
                <div className="result-value">
                  {item.value} <span className="result-unit">{item.unit}</span>
                </div>
                <SeverityBadge status={item.status} />
              </div>
            </div>
            <div className="result-body">
              <p className="result-explanation">{item.explanation}</p>
              {item.next_step && (
                <div className="next-step">
                  <span className="next-step-label">Next Step:</span>
                  <span>{item.next_step}</span>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </>
  );
}
