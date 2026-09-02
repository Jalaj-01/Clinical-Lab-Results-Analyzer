# Clinical Lab Results Analyzer

A full-stack clinical decision-support application that ingests laboratory test results, validates numeric inputs, classifies severity against reference intervals, prioritizes critical findings first, and generates non-diagnostic clinical explanations and recommended next steps using LLMs and the Model Context Protocol (MCP).

---

## Architecture

The system implements the **Classify -> Route -> Explain** pipeline:

```
[React Frontend] ──(POST /analyze_labs)──> [FastAPI Backend]
                                                  │
                                                  ▼
                                      [Agent Orchestrator]
                                                  │
                 ┌────────────────────────────────┼────────────────────────────────┐
                 ▼                                ▼                                ▼
    [1. Reference Lookup & Classify]     [2. Priority Router]              [3. LLM Explain]
     (mcp_server / classifier.py)       (Critical > Warning > Normal)      (mcp_server / llm.py)
                 │                                │                                │
                 ▼                                ▼                                ▼
         Assign Severity                  Sort Urgently                   Generate Context
                 └────────────────────────────────┼────────────────────────────────┘
                                                  │
                                                  ▼
                                    [Structured JSON Response]
```

### Flow Breakdown:
1. **Classify**: Compares numeric results against physiological reference intervals (Normal, Warning, Critical) using `classifier.py` and the MCP lookup tools.
2. **Route**: Prioritizes findings so urgent **Critical** alerts are positioned first, followed by **Warning**, and **Normal** baselines last.
3. **Explain**: Generates clinical context explaining why a result was flagged and suggests safe, actionable next steps.

---

## AI Provider Chosen

- **Primary Provider**: **Google Gemini API** (`gemini-2.5-flash` / `gemini-3.6-flash`) using the official SDK.
- **Alternative Providers Supported**: **Groq API** (`llama-3.3-70b-versatile`) and **OpenAI API**.
- **Resilient Clinical Fallback Engine**: If no API key is supplied or if network/quota errors occur, the system utilizes an intelligent built-in physiological clinical engine so the application remains fully functional and never crashes during offline testing or evaluation.

---

## Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Environment Setup
Create your local `.env` from the template:
```bash
cp .env.example .env
```

Configure your `.env`:
```env
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 3. Backend Setup
```bash
pip install -r backend/requirements.txt
python backend/run.py
```
- Server URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Dashboard URL: `http://localhost:5173`

---

## How to Test

### 1. Testing with Synthetic Datasets (Web UI)
Open `http://localhost:5173` in your browser:
- Click **Normal Dataset** to test baseline physiological values.
- Click **Warning Dataset** to test borderline/mildly elevated values.
- Click **Critical Dataset** to test urgent critical values and verify priority routing.
- Click **Kaggle Real Dataset** to test records from the anonymized Kaggle laboratory dataset.
- Click **Run Analysis** to execute the pipeline.

### 2. Testing with CSV Upload
1. Switch to the **Upload CSV** tab in the sidebar.
2. Drag and drop any file from the `test_data/` folder:
   - `test_data/normal.csv`
   - `test_data/warning.csv`
   - `test_data/critical.csv`
   - `test_data/kaggle_dataset.csv`
3. Click **Run Analysis**.

### 3. Running Automated Test Suite
Run the automated pytest test suite covering validation, routing priority, boundaries, and error handling:
```bash
python -m pytest backend/tests -v
```

---

## API Reference

### `POST /analyze_labs`
Main analysis endpoint. Ingests raw laboratory results, performs validation, reference interval classification, priority routing, and clinical explanation generation.

**Request Example:**
```json
{
  "labs": [
    { "test_name": "Hemoglobin", "value": 6.2, "unit": "g/dL" },
    { "test_name": "Glucose", "value": 118.0, "unit": "mg/dL" },
    { "test_name": "Platelets", "value": 240.0, "unit": "10^3/uL" }
  ]
}
```

**Response Example:**
```json
{
  "results": [
    {
      "test_name": "Hemoglobin",
      "value": 6.2,
      "unit": "g/dL",
      "reference_range": "12.0 - 17.5 g/dL",
      "status": "Critical",
      "explanation": "Hemoglobin of 6.2 g/dL is critically outside reference bounds (12.0 - 17.5 g/dL). Critically low hemoglobin indicates severe anemia with significantly reduced oxygen delivery capacity.",
      "next_step": "Seek urgent medical review with your physician or hematologist for immediate clinical assessment."
    },
    {
      "test_name": "Glucose",
      "value": 118.0,
      "unit": "mg/dL",
      "reference_range": "70.0 - 99.0 mg/dL",
      "status": "Warning",
      "explanation": "Glucose of 118.0 mg/dL shows a moderate deviation outside the reference range (70.0 - 99.0 mg/dL).",
      "next_step": "Discuss with your physician to evaluate contributing factors and determine if a follow-up test is recommended."
    },
    {
      "test_name": "Platelets",
      "value": 240.0,
      "unit": "10^3/uL",
      "reference_range": "150.0 - 450.0 10^3/uL",
      "status": "Normal",
      "explanation": "Platelets of 240.0 10^3/uL is within the expected standard physiological reference range (150.0 - 450.0 10^3/uL).",
      "next_step": "Routine monitoring as recommended by your healthcare provider."
    }
  ],
  "total_analyzed": 3,
  "critical_count": 1,
  "warning_count": 1,
  "normal_count": 1
}
```

### `GET /health`
Returns backend health status, MCP readiness, and LLM configuration state.

---

## MCP (Model Context Protocol) Tools

The backend implements standard MCP tools in `backend/app/mcp_server.py`:
- `reference_range_lookup`: Queries physiological minimums, maximums, and critical cutoffs for lab tests.
- `classify_lab_tool`: Evaluates numeric lab values against reference intervals.
- `explain_lab_tool`: Generates non-diagnostic clinical explanations and actionable next steps.
