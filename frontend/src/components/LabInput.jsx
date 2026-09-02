import React, { useState, useRef } from 'react';
import Papa from 'papaparse';

const INITIAL_ROW = { test_name: '', value: '', unit: '' };

const PRESETS = {
  normal: [
    { test_name: 'Hemoglobin', value: '14.5', unit: 'g/dL' },
    { test_name: 'Glucose', value: '85.0', unit: 'mg/dL' },
    { test_name: 'WBC', value: '6.8', unit: '10^3/uL' },
    { test_name: 'Platelets', value: '240.0', unit: '10^3/uL' },
    { test_name: 'Creatinine', value: '0.9', unit: 'mg/dL' },
  ],
  warning: [
    { test_name: 'Hemoglobin', value: '11.2', unit: 'g/dL' },
    { test_name: 'Glucose', value: '118.0', unit: 'mg/dL' },
    { test_name: 'WBC', value: '12.4', unit: '10^3/uL' },
    { test_name: 'Platelets', value: '135.0', unit: '10^3/uL' },
    { test_name: 'Creatinine', value: '1.5', unit: 'mg/dL' },
  ],
  critical: [
    { test_name: 'Hemoglobin', value: '6.2', unit: 'g/dL' },
    { test_name: 'Glucose', value: '450.0', unit: 'mg/dL' },
    { test_name: 'WBC', value: '1.4', unit: '10^3/uL' },
    { test_name: 'Platelets', value: '28.0', unit: '10^3/uL' },
    { test_name: 'Creatinine', value: '5.4', unit: 'mg/dL' },
  ],
  kaggle: [
    { test_name: 'Hemoglobin', value: '12.9', unit: 'g/dL' },
    { test_name: 'Ferritin', value: '28.9', unit: 'ug/L' },
    { test_name: 'HbA1c', value: '5.0', unit: '%' },
    { test_name: 'Platelets', value: '267.0', unit: '10^3/uL' },
    { test_name: 'WBC', value: '6.37', unit: '10^3/uL' },
    { test_name: 'Hematocrit', value: '40.0', unit: '%' },
  ],
};

export default function LabInput({ onAnalyze, isLoading }) {
  const [tab, setTab] = useState('manual');
  const [rows, setRows] = useState([
    { test_name: 'Hemoglobin', value: '10.2', unit: 'g/dL' },
    { test_name: 'Glucose', value: '135.0', unit: 'mg/dL' },
    { test_name: 'Platelets', value: '42.0', unit: '10^3/uL' },
  ]);
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef(null);

  const change = (i, field, val) => {
    const next = [...rows];
    next[i][field] = val;
    setRows(next);
    setError(null);
  };

  const loadPreset = (key) => {
    setRows(PRESETS[key].map(r => ({ ...r })));
    setError(null);
    setTab('manual');
  };

  const parseCSV = (file) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: ({ data }) => {
        const parsed = [];
        for (const item of data) {
          const name = item.test_name || item.Test_Name || item.Test || '';
          const raw = item.value || item.Value || item.Result || '';
          const unit = item.unit || item.Unit || item.Units || 'units';
          if (!name) continue;
          if (isNaN(parseFloat(raw))) continue;
          parsed.push({ test_name: name.trim(), value: raw.trim(), unit: unit.trim() });
        }
        if (parsed.length === 0) { setError('No valid numeric rows found in CSV.'); return; }
        setRows(parsed);
        setTab('manual');
        setError(null);
      },
      error: (e) => setError(`CSV error: ${e.message}`),
    });
  };

  const submit = (e) => {
    e.preventDefault();
    setError(null);
    const valid = [];
    for (let i = 0; i < rows.length; i++) {
      const { test_name, value, unit } = rows[i];
      if (!test_name && !value && !unit) continue;
      if (!test_name.trim()) { setError(`Row ${i + 1}: test name is empty.`); return; }
      if (isNaN(parseFloat(value))) { setError(`Row ${i + 1} (${test_name}): value must be numeric.`); return; }
      if (!unit.trim()) { setError(`Row ${i + 1} (${test_name}): unit is missing.`); return; }
      valid.push({ test_name: test_name.trim(), value: parseFloat(value), unit: unit.trim() });
    }
    if (valid.length === 0) { setError('Add at least one lab test to analyze.'); return; }
    onAnalyze(valid);
  };

  return (
    <div className="sidebar">
      {/* Presets */}
      <div className="sidebar-section">
        <div className="section-label">Sample datasets</div>
        <div className="presets-row">
          {['normal', 'warning', 'critical', 'kaggle'].map(k => (
            <button key={k} className={`preset-chip ${k}`} onClick={() => loadPreset(k)}>
              <span className="dot" />
              {k.charAt(0).toUpperCase() + k.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Tab switch */}
      <div className="sidebar-section" style={{ flex: 1 }}>
        <div className="tabs">
          <button className={`tab-btn ${tab === 'manual' ? 'active' : ''}`} onClick={() => setTab('manual')}>
            Manual ({rows.length})
          </button>
          <button className={`tab-btn ${tab === 'csv' ? 'active' : ''}`} onClick={() => setTab('csv')}>
            Upload CSV
          </button>
        </div>

        {error && (
          <div className="err-bar">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{flexShrink:0,marginTop:1}}>
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {error}
          </div>
        )}

        {tab === 'csv' ? (
          <div
            className={`csv-zone ${dragging ? 'dragging' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={e => { e.preventDefault(); setDragging(false); if (e.dataTransfer.files[0]) parseCSV(e.dataTransfer.files[0]); }}
            onClick={() => fileRef.current?.click()}
          >
            <input type="file" accept=".csv" ref={fileRef} style={{ display: 'none' }}
              onChange={e => { if (e.target.files[0]) parseCSV(e.target.files[0]); }} />
            <div className="csv-zone-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/>
              </svg>
            </div>
            <div className="csv-zone-text">Drop CSV here or click to browse</div>
            <div className="csv-zone-hint">Columns: test_name, value, unit</div>
          </div>
        ) : (
          <form onSubmit={submit}>
            <table className="lab-table">
              <thead>
                <tr>
                  <th style={{ width: '45%' }}>Test</th>
                  <th style={{ width: '22%' }}>Value</th>
                  <th style={{ width: '22%' }}>Unit</th>
                  <th style={{ width: '11%' }}></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr key={i}>
                    <td>
                      <input className="cell-input" placeholder="e.g. Glucose" value={row.test_name}
                        onChange={e => change(i, 'test_name', e.target.value)} />
                    </td>
                    <td>
                      <input className="cell-input mono" placeholder="85.0" type="number" step="any" value={row.value}
                        onChange={e => change(i, 'value', e.target.value)} />
                    </td>
                    <td>
                      <input className="cell-input" placeholder="mg/dL" value={row.unit}
                        onChange={e => change(i, 'unit', e.target.value)} />
                    </td>
                    <td>
                      <button type="button" className="remove-btn" onClick={() =>
                        setRows(rows.length === 1 ? [{ ...INITIAL_ROW }] : rows.filter((_, j) => j !== i))
                      }>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <button type="button" className="add-row-btn" onClick={() => setRows([...rows, { ...INITIAL_ROW }])}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              Add row
            </button>

            <div style={{ marginTop: 14 }}>
              <button type="submit" className="submit-btn" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <svg className="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                    </svg>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <polygon points="5 3 19 12 5 21 5 3"/>
                    </svg>
                    Run Analysis
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
