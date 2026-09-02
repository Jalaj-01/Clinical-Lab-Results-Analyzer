# Clinical Lab Results Analyzer

A full-stack clinical decision-support demonstration that takes laboratory test results, validates them, classifies their severity against standard reference intervals, prioritizes critical findings first, and generates clear, non-diagnostic clinical explanations and next steps using LLMs and the Model Context Protocol (MCP).

---

## What It Does

Clinical laboratories produce high volumes of test data every day. This application streamlines how these results are interpreted and prioritized:

1. **Classify**: Compares numeric results against clinical reference ranges and categorizes them into `Normal`, `Warning`, or `Critical`.
2. **Route**: Sorts findings by clinical urgency so critical alerts appear at the very top, followed by warnings, and normal baselines last.
3. **Explain**: Generates concise, understandable explanations of why a result was flagged along with safe, recommended follow-up actions using an LLM.

---

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Agent / Tooling**: Model Context Protocol (MCP) SDK
- **AI / LLM**: Google Gemini API (`gemini-2.5-flash`) with structured fallback handling
- **Frontend**: React 18, Vite, Lucide Icons, PapaParse, Vanilla CSS
- **Testing**: Pytest, FastAPI TestClient

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app and API routes
│   │   ├── models.py            # Pydantic request and response schemas
│   │   ├── reference_ranges.py  # Standard reference intervals & test aliases
│   │   ├── classifier.py        # Lab result classification logic
│   │   ├── mcp_server.py        # FastMCP server and tool definitions
│   │   ├── agent.py             # Classify -> Route -> Explain orchestration
│   │   └── llm.py               # Gemini client & prompt generation
│   ├── tests/
│   │   └── test_api.py          # Pytest automated test suite
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variable template
│   └── run.py                   # Server startup script
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LabInput.jsx         # Form entry & CSV upload
│   │   │   ├── ResultsDisplay.jsx   # Results card layout & counters
│   │   │   └── SeverityBadge.jsx    # Severity status badges
│   │   ├── App.jsx                  # Main dashboard layout
│   │   ├── App.css                  # Custom styling and design system
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── test_data/
│   ├── normal.csv               # Normal test results sample
│   ├── warning.csv              # Borderline/warning test results sample
│   ├── critical.csv             # Critical/urgent test results sample
│   └── kaggle_dataset.csv       # Anonymized laboratory dataset from Kaggle
├── README.md
└── .gitignore
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Environment Setup
Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```

Set your Google Gemini API key in `.env`:
```env
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

> **Note**: If you do not have a Gemini API key yet, the application will automatically run in fallback mode with structured clinical explanations so you can test all features offline.

### 3. Running the Backend
Install Python dependencies and start the server:
```bash
pip install -r backend/requirements.txt
python backend/run.py
```
The FastAPI backend will start at `http://localhost:8000`. You can explore the interactive OpenAPI documentation at `http://localhost:8000/docs`.

### 4. Running the Frontend
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
The React frontend will be accessible at `http://localhost:5173`.

---

## How to Test

### Using the Web UI
1. Open `http://localhost:5173` in your browser.
2. Use the **Quick-Load Synthetic Datasets** buttons (`Normal`, `Warning`, `Critical`, or `Kaggle Real Dataset`) to populate sample data with a single click.
3. Or manually add custom lab test rows (e.g., `Hemoglobin`, `Glucose`, `Platelets`, `WBC`, `Creatinine`).
4. Or switch to the **Upload CSV** tab and drag-and-drop any CSV file from `test_data/`.
5. Click **Run Analysis** to execute the pipeline.

### Running Automated Backend Tests
Run the pytest test suite to verify endpoint routing, validation, reference intervals, and severity sorting:
```bash
python -m pytest backend/tests -v
```

---

## API Reference

### `POST /analyze_labs`
Accepts a list of lab results and returns categorized, sorted, and explained findings.

**Request Payload:**
```json
{
  "labs": [
    { "test_name": "Hemoglobin", "value": 6.2, "unit": "g/dL" },
    { "test_name": "Glucose", "value": 118.0, "unit": "mg/dL" },
    { "test_name": "Platelets", "value": 240.0, "unit": "10^3/uL" }
  ]
}
```

**Response Payload:**
```json
{
  "results": [
    {
      "test_name": "Hemoglobin",
      "value": 6.2,
      "unit": "g/dL",
      "reference_range": "12.0 - 17.5 g/dL",
      "status": "Critical",
      "explanation": "CRITICAL FINDING: Hemoglobin of 6.2 g/dL is severely low and indicates acute anemia requiring urgent clinical review.",
      "next_step": "Seek immediate medical evaluation or contact treating physician for urgent hematology assessment."
    },
    {
      "test_name": "Glucose",
      "value": 118.0,
      "unit": "mg/dL",
      "reference_range": "70.0 - 99.0 mg/dL",
      "status": "Warning",
      "explanation": "Glucose level of 118.0 mg/dL is mildly elevated above the fasting reference interval.",
      "next_step": "Discuss with your physician to evaluate fasting status or consider follow-up testing."
    },
    {
      "test_name": "Platelets",
      "value": 240.0,
      "unit": "10^3/uL",
      "reference_range": "150.0 - 450.0 10^3/uL",
      "status": "Normal",
      "explanation": "Platelet count of 240.0 10^3/uL is within the standard physiological reference range.",
      "next_step": "Routine monitoring as recommended during regular wellness visits."
    }
  ],
  "total_analyzed": 3,
  "critical_count": 1,
  "warning_count": 1,
  "normal_count": 1,
  "disclaimer": "INFORMATIONAL ONLY: This analysis is an educational demonstration and does NOT constitute a medical diagnosis."
}
```

### `GET /health`
Returns backend service health, MCP readiness, and LLM configuration status.

---

## Model Context Protocol (MCP) Tools

The backend implements MCP tool interfaces inside `backend/app/mcp_server.py`:
- `reference_range_lookup`: Queries physiological minimums, maximums, and critical cutoffs for lab tests.
- `classify_lab_tool`: Evaluates numeric lab values against reference intervals.
- `explain_lab_tool`: Invokes the LLM to generate non-diagnostic clinical explanations and next steps.

---

## Medical Safety & Disclaimer

This application is created strictly for educational demonstration and software engineering evaluation purposes. It does not provide medical advice or diagnosis. All laboratory results should be reviewed in consultation with qualified healthcare professionals.
