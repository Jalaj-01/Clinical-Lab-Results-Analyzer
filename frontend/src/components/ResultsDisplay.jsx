/**
 * ResultsDisplay Component
 * 
 * Renders the prioritized, classified, and LLM-explained lab results
 * including severity badges, reference intervals, and actionable recommendations.
 */

import React from 'react';
import SeverityBadge from './SeverityBadge';
import { Activity, ArrowRight, Info, CheckCircle, AlertTriangle, AlertOctagon, HelpCircle } from 'lucide-react';

export default function ResultsDisplay({ data, isLoading }) {
  if (isLoading) {
    return (
      <div className="card">
        <div className="empty-state">
          <Activity className="empty-icon spinner" style={{ color: '#0284c7' }} />
          <h3 className="empty-title">Analyzing Clinical Findings</h3>
          <p className="empty-desc">Executing Agent orchestration: Validating → Classifying → Priority Routing → AI Explaining...</p>
        </div>
      </div>
    );
  }

  if (!data || !data.results || data.results.length === 0) {
    return (
      <div className="card">
        <div className="empty-state">
          <HelpCircle className="empty-icon" />
          <h3 className="empty-title">No Lab Results Analyzed</h3>
          <p className="empty-desc">Enter laboratory tests on the left panel or upload a CSV dataset to view classified results.</p>
        </div>
      </div>
    );
  }

  const { results, critical_count, warning_count, normal_count, total_analyzed, disclaimer } = data;

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <Activity size={20} color="#0284c7" />
          Clinical Analysis & Explanations
        </h2>
        <span style={{ fontSize: '0.8125rem', color: '#64748b', fontWeight: 600 }}>
          {total_analyzed} Test{total_analyzed !== 1 ? 's' : ''} Processed
        </span>
      </div>

      {/* Summary Stat Counters */}
      <div className="stats-summary">
        <div className="stat-box critical">
          <div className="stat-count">{critical_count}</div>
          <div className="stat-label">Critical</div>
        </div>
        <div className="stat-box warning">
          <div className="stat-count">{warning_count}</div>
          <div className="stat-label">Warning</div>
        </div>
        <div className="stat-box normal">
          <div className="stat-count">{normal_count}</div>
          <div className="stat-label">Normal</div>
        </div>
      </div>

      {/* Prioritized Results List (Critical -> Warning -> Normal) */}
      <div className="results-list">
        {results.map((item, idx) => {
          const cardSeverityClass = (item.status || 'unknown').toLowerCase();

          return (
            <div key={idx} className={`result-card ${cardSeverityClass}`}>
              <div className="result-card-top">
                <div>
                  <h3 className="test-title">{item.test_name}</h3>
                  <div className="test-value-wrap">
                    <span className="test-value">{item.value}</span>
                    <span className="test-unit">{item.unit}</span>
                  </div>
                  <div className="ref-range-badge">
                    Reference Interval: {item.reference_range}
                  </div>
                </div>

                <SeverityBadge status={item.status} />
              </div>

              {/* LLM Clinical Explanation */}
              <div className="result-section">
                <div className="section-label">
                  <Info size={13} />
                  Clinical Context & Explanation
                </div>
                <p className="explanation-text">{item.explanation}</p>
              </div>

              {/* Recommended Next Step */}
              {item.next_step && (
                <div className="next-step-box">
                  <div className="section-label" style={{ color: '#0369a1', marginBottom: '0.2rem' }}>
                    <ArrowRight size={13} />
                    Suggested Next Step
                  </div>
                  <div>{item.next_step}</div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
