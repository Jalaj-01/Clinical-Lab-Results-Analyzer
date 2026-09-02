/**
 * LabInput Component
 * 
 * Facilitates manual laboratory result entry, quick preset selection,
 * and drag-and-drop CSV file ingestion.
 */

import React, { useState, useRef } from 'react';
import Papa from 'papaparse';
import { Plus, Trash2, Upload, FileText, Sparkles, AlertCircle } from 'lucide-react';

const INITIAL_ROW = { test_name: '', value: '', unit: '' };

const PRESET_DATASETS = {
  normal: [
    { test_name: 'Hemoglobin', value: '14.5', unit: 'g/dL' },
    { test_name: 'Glucose', value: '85.0', unit: 'mg/dL' },
    { test_name: 'WBC', value: '6.8', unit: '10^3/uL' },
    { test_name: 'Platelets', value: '240.0', unit: '10^3/uL' },
    { test_name: 'Creatinine', value: '0.9', unit: 'mg/dL' }
  ],
  warning: [
    { test_name: 'Hemoglobin', value: '11.2', unit: 'g/dL' },
    { test_name: 'Glucose', value: '118.0', unit: 'mg/dL' },
    { test_name: 'WBC', value: '12.4', unit: '10^3/uL' },
    { test_name: 'Platelets', value: '135.0', unit: '10^3/uL' },
    { test_name: 'Creatinine', value: '1.5', unit: 'mg/dL' }
  ],
  critical: [
    { test_name: 'Hemoglobin', value: '6.2', unit: 'g/dL' },
    { test_name: 'Glucose', value: '450.0', unit: 'mg/dL' },
    { test_name: 'WBC', value: '1.4', unit: '10^3/uL' },
    { test_name: 'Platelets', value: '28.0', unit: '10^3/uL' },
    { test_name: 'Creatinine', value: '5.4', unit: 'mg/dL' }
  ],
  kaggle: [
    { test_name: 'Hemoglobin', value: '12.9', unit: 'g/dL' },
    { test_name: 'Ferritin', value: '28.9', unit: 'ug/L' },
    { test_name: 'HbA1c', value: '5.0', unit: '%' },
    { test_name: 'Platelets', value: '267.0', unit: '10^3/uL' },
    { test_name: 'WBC', value: '6.37', unit: '10^3/uL' },
    { test_name: 'Hematocrit', value: '40.0', unit: '%' }
  ]
};

export default function LabInput({ onAnalyze, isLoading }) {
  const [activeTab, setActiveTab] = useState('manual'); // 'manual' | 'csv'
  const [rows, setRows] = useState([
    { test_name: 'Hemoglobin', value: '10.2', unit: 'g/dL' },
    { test_name: 'Glucose', value: '135.0', unit: 'mg/dL' },
    { test_name: 'Platelets', value: '42.0', unit: '10^3/uL' }
  ]);
  const [validationError, setValidationError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleRowChange = (index, field, value) => {
    const updated = [...rows];
    updated[index][field] = value;
    setRows(updated);
    setValidationError(null);
  };

  const handleAddRow = () => {
    setRows([...rows, { ...INITIAL_ROW }]);
  };

  const handleRemoveRow = (index) => {
    if (rows.length <= 1) {
      setRows([{ ...INITIAL_ROW }]);
    } else {
      setRows(rows.filter((_, i) => i !== index));
    }
  };

  const handleLoadPreset = (type) => {
    const preset = PRESET_DATASETS[type];
    if (preset) {
      setRows(preset.map(item => ({ ...item })));
      setValidationError(null);
      setActiveTab('manual');
    }
  };

  const handleCsvFile = (file) => {
    if (!file) return;
    setValidationError(null);

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        try {
          if (!results.data || results.data.length === 0) {
            setValidationError('The uploaded CSV file is empty.');
            return;
          }

          const parsedRows = [];
          for (let idx = 0; idx < results.data.length; idx++) {
            const item = results.data[idx];
            const test_name = item.test_name || item.Test_Name || item.Test || item['Test Name'] || '';
            const rawVal = item.value || item.Value || item.Result || '';
            const unit = item.unit || item.Unit || item.Units || 'units';

            if (!test_name) continue;

            // Check if numeric
            const numericVal = parseFloat(rawVal);
            if (isNaN(numericVal)) {
              // Skip qualitative or non-numeric rows (e.g. "Negatif", "Normal", "1+")
              continue;
            }

            parsedRows.push({
              test_name: String(test_name).trim(),
              value: String(rawVal).trim(),
              unit: String(unit).trim() || 'units'
            });
          }

          if (parsedRows.length === 0) {
            setValidationError('No valid numeric lab test records found in CSV.');
            return;
          }

          setRows(parsedRows);
          setActiveTab('manual');
        } catch (err) {
          setValidationError(`Failed to parse CSV: ${err.message}`);
        }
      },
      error: (error) => {
        setValidationError(`CSV reading error: ${error.message}`);
      }
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setValidationError(null);

    // Validate rows
    const validLabs = [];
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const testName = row.test_name.trim();
      const valStr = String(row.value).trim();
      const unit = row.unit.trim();

      if (!testName && !valStr && !unit) {
        // Skip empty row if there are others
        continue;
      }

      if (!testName) {
        setValidationError(`Test #${i + 1} is missing a test name.`);
        return;
      }

      if (valStr === '' || isNaN(Number(valStr))) {
        setValidationError(`Test #${i + 1} (${testName}) requires a valid numeric value.`);
        return;
      }

      if (!unit) {
        setValidationError(`Test #${i + 1} (${testName}) is missing a unit.`);
        return;
      }

      validLabs.push({
        test_name: testName,
        value: parseFloat(valStr),
        unit: unit
      });
    }

    if (validLabs.length === 0) {
      setValidationError('Please enter at least one complete lab result to analyze.');
      return;
    }

    onAnalyze(validLabs);
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <FileText size={20} color="#0284c7" />
          Lab Test Ingestion
        </h2>
      </div>

      {/* Quick Test Presets */}
      <div className="quick-preloads">
        <span className="quick-title">Quick-Load Synthetic Datasets:</span>
        <div className="preset-buttons">
          <button
            type="button"
            className="btn-preset"
            onClick={() => handleLoadPreset('normal')}
          >
            <span style={{ color: '#10b981' }}>●</span> Normal Dataset
          </button>
          <button
            type="button"
            className="btn-preset"
            onClick={() => handleLoadPreset('warning')}
          >
            <span style={{ color: '#f59e0b' }}>●</span> Warning Dataset
          </button>
          <button
            type="button"
            className="btn-preset"
            onClick={() => handleLoadPreset('critical')}
          >
            <span style={{ color: '#ef4444' }}>●</span> Critical Dataset
          </button>
          <button
            type="button"
            className="btn-preset"
            onClick={() => handleLoadPreset('kaggle')}
          >
            <span style={{ color: '#0284c7' }}>●</span> Kaggle Real Dataset
          </button>
        </div>
      </div>

      {/* Mode Selection Tabs */}
      <div className="tabs-nav">
        <button
          type="button"
          className={`tab-btn ${activeTab === 'manual' ? 'active' : ''}`}
          onClick={() => setActiveTab('manual')}
        >
          Manual Entry ({rows.length})
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'csv' ? 'active' : ''}`}
          onClick={() => setActiveTab('csv')}
        >
          <Upload size={14} />
          Upload CSV
        </button>
      </div>

      {validationError && (
        <div className="error-message">
          <AlertCircle size={16} />
          <span>{validationError}</span>
        </div>
      )}

      {activeTab === 'csv' ? (
        <div>
          <div
            className={`csv-dropzone ${isDragging ? 'dragging' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragging(false);
              if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleCsvFile(e.dataTransfer.files[0]);
              }
            }}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept=".csv,text/csv"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleCsvFile(e.target.files[0]);
                }
              }}
            />
            <Upload className="csv-icon" />
            <div className="csv-title">Drop your laboratory CSV file here</div>
            <div className="csv-desc">Supports columns: test_name, value, unit</div>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="lab-rows-container">
            {rows.map((row, idx) => (
              <div key={idx} className="lab-row">
                <input
                  type="text"
                  placeholder="Test Name (e.g. Hemoglobin)"
                  className="input-field"
                  value={row.test_name}
                  onChange={(e) => handleRowChange(idx, 'test_name', e.target.value)}
                />
                <input
                  type="number"
                  step="any"
                  placeholder="Value (e.g. 14.5)"
                  className="input-field"
                  value={row.value}
                  onChange={(e) => handleRowChange(idx, 'value', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Unit (e.g. g/dL)"
                  className="input-field"
                  value={row.unit}
                  onChange={(e) => handleRowChange(idx, 'unit', e.target.value)}
                />
                <button
                  type="button"
                  className="btn-icon"
                  title="Remove test"
                  onClick={() => handleRemoveRow(idx)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>

          <button
            type="button"
            className="btn-add-row"
            onClick={handleAddRow}
          >
            <Plus size={14} /> Add Test Row
          </button>

          <button
            type="submit"
            className="btn-submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="status-dot spinner" style={{ backgroundColor: 'white' }} />
                Analyzing via MCP & Agent...
              </>
            ) : (
              <>
                <Sparkles size={16} />
                Run Analysis (Classify → Route → Explain)
              </>
            )}
          </button>
        </form>
      )}
    </div>
  );
}
