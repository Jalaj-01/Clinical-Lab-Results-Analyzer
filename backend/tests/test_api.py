"""Comprehensive Automated API and Integration Tests for Clinical Lab Results Analyzer."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.reference_ranges import get_reference_range, normalize_test_name
from app.classifier import classify_lab
from app.models import ReferenceRange

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint returns system metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Clinical Lab Results Analyzer API"
    assert data["status"] == "online"
    assert "endpoints" in data


def test_health_endpoint():
    """Verify health endpoint returns status and capabilities."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "mcp_server" in data


def test_reference_range_lookup():
    """Verify reference range lookups and alias handling."""
    hgb = get_reference_range("Hemoglobin")
    assert hgb is not None
    assert hgb.low == 12.0
    assert hgb.high == 17.5
    assert hgb.unit == "g/dL"

    # Alias check
    hgb_alias = get_reference_range("hgb")
    assert hgb_alias is not None
    assert hgb_alias.test_name == "Hemoglobin"

    # Unknown test
    unknown = get_reference_range("NonExistentTest123")
    assert unknown is None


def test_analyze_labs_normal_result():
    """Verify analysis of a normal lab result."""
    payload = {
        "labs": [
            {
                "test_name": "Hemoglobin",
                "value": 14.5,
                "unit": "g/dL"
            }
        ]
    }
    response = client.post("/analyze_labs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_analyzed"] == 1
    assert data["normal_count"] == 1
    assert data["warning_count"] == 0
    assert data["critical_count"] == 0
    result = data["results"][0]
    assert result["test_name"] == "Hemoglobin"
    assert result["value"] == 14.5
    assert result["status"] == "Normal"
    assert len(result["explanation"]) > 0
    assert len(result["next_step"]) > 0


def test_analyze_labs_warning_result():
    """Verify analysis of a warning/borderline lab result."""
    payload = {
        "labs": [
            {
                "test_name": "Glucose",
                "value": 115.0,
                "unit": "mg/dL"
            }
        ]
    }
    response = client.post("/analyze_labs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_analyzed"] == 1
    assert data["warning_count"] == 1
    result = data["results"][0]
    assert result["status"] == "Warning"


def test_analyze_labs_critical_result():
    """Verify analysis of a critical lab result."""
    payload = {
        "labs": [
            {
                "test_name": "Potassium",
                "value": 6.8,
                "unit": "mEq/L"
            }
        ]
    }
    response = client.post("/analyze_labs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_analyzed"] == 1
    assert data["critical_count"] == 1
    result = data["results"][0]
    assert result["status"] == "Critical"


def test_analyze_labs_severity_routing_order():
    """Verify that results are ordered: Critical first, Warning second, Normal last."""
    payload = {
        "labs": [
            {"test_name": "Hemoglobin", "value": 14.5, "unit": "g/dL"},   # Normal
            {"test_name": "Glucose", "value": 450.0, "unit": "mg/dL"},     # Critical
            {"test_name": "WBC", "value": 12.5, "unit": "10^3/uL"},        # Warning
            {"test_name": "Potassium", "value": 2.2, "unit": "mEq/L"},     # Critical
            {"test_name": "Platelets", "value": 220.0, "unit": "10^3/uL"}  # Normal
        ]
    }
    response = client.post("/analyze_labs", json=payload)
    assert response.status_code == 200
    data = response.json()
    results = data["results"]
    assert len(results) == 5

    # Check status sequence
    statuses = [r["status"] for r in results]
    # First 2 must be Critical
    assert statuses[0] == "Critical"
    assert statuses[1] == "Critical"
    # Middle 1 must be Warning
    assert statuses[2] == "Warning"
    # Last 2 must be Normal
    assert statuses[3] == "Normal"
    assert statuses[4] == "Normal"


def test_boundary_values():
    """Verify boundary handling at exact low and high physiological limits."""
    hgb_ref = get_reference_range("Hemoglobin")
    # Exactly at minimum bound (12.0)
    assert classify_lab("Hemoglobin", 12.0, "g/dL", hgb_ref) == "Normal"
    # Exactly at maximum bound (17.5)
    assert classify_lab("Hemoglobin", 17.5, "g/dL", hgb_ref) == "Normal"
    # Slightly below minimum bound (11.9)
    assert classify_lab("Hemoglobin", 11.9, "g/dL", hgb_ref) == "Warning"
    # Slightly above maximum bound (17.6)
    assert classify_lab("Hemoglobin", 17.6, "g/dL", hgb_ref) == "Warning"


def test_unknown_test_handling():
    """Verify handling when an unknown laboratory test is provided."""
    payload = {
        "labs": [
            {
                "test_name": "ExperimentalBiomarkerX",
                "value": 42.0,
                "unit": "ng/mL"
            }
        ]
    }
    response = client.post("/analyze_labs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_analyzed"] == 1
    assert data["results"][0]["status"] == "Unknown"
    assert data["results"][0]["reference_range"] == "Standard range unavailable"


def test_validation_empty_labs():
    """Verify 422/400 validation error when labs array is empty."""
    response = client.post("/analyze_labs", json={"labs": []})
    assert response.status_code in (400, 422)


def test_validation_missing_fields():
    """Verify 422 validation error when required fields are missing."""
    # Missing value
    response = client.post("/analyze_labs", json={"labs": [{"test_name": "Hemoglobin", "unit": "g/dL"}]})
    assert response.status_code == 422

    # Missing test_name
    response = client.post("/analyze_labs", json={"labs": [{"value": 14.5, "unit": "g/dL"}]})
    assert response.status_code == 422

    # Invalid non-numeric value
    response = client.post("/analyze_labs", json={"labs": [{"test_name": "Hemoglobin", "value": "fourteen", "unit": "g/dL"}]})
    assert response.status_code == 422
