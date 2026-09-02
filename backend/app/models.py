"""Pydantic Request and Response Models for Clinical Lab Analyzer."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SeverityLevel(str, Enum):
    """Clinical severity classifications."""
    NORMAL = "Normal"
    WARNING = "Warning"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"


class ReferenceRange(BaseModel):
    """Standard physiological reference range for a specific laboratory test."""
    test_name: str
    low: float = Field(..., description="Lower bound of normal physiological range")
    high: float = Field(..., description="Upper bound of normal physiological range")
    unit: str = Field(..., description="Measurement unit (e.g., g/dL, mg/dL, mcL)")
    critical_low: Optional[float] = Field(
        default=None,
        description="Threshold below which the value is considered critically low"
    )
    critical_high: Optional[float] = Field(
        default=None,
        description="Threshold above which the value is considered critically high"
    )
    description: Optional[str] = Field(
        default=None,
        description="Clinical context or notes regarding this test"
    )

    def to_range_string(self) -> str:
        """Format the reference range as a human-readable string."""
        return f"{self.low} - {self.high} {self.unit}"


class LabItem(BaseModel):
    """Individual laboratory test entry provided in the input payload."""
    test_name: str = Field(
        ...,
        min_length=1,
        description="Name of the laboratory test (e.g., Hemoglobin, Glucose, WBC)"
    )
    value: float = Field(
        ...,
        description="Numeric result value obtained from the laboratory"
    )
    unit: str = Field(
        ...,
        min_length=1,
        description="Unit of measurement associated with the test value"
    )

    @field_validator("test_name", "unit", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Field cannot be empty or whitespace only.")
            return v_stripped
        return v

    @field_validator("value", mode="before")
    @classmethod
    def validate_numeric_value(cls, v):
        try:
            val = float(v)
            if val != val:  # Check for NaN
                raise ValueError("Value cannot be NaN")
            return val
        except (TypeError, ValueError) as e:
            raise ValueError(f"Lab test value must be a valid numeric float: {e}")


class LabAnalysisRequest(BaseModel):
    """Payload sent to POST /analyze_labs."""
    labs: List[LabItem] = Field(
        ...,
        min_length=1,
        description="List of lab tests to analyze. Must contain at least one test."
    )


class LabResultItem(BaseModel):
    """Individual analyzed and classified laboratory test result."""
    test_name: str
    value: float
    unit: str
    reference_range: str
    status: str = Field(
        ...,
        description="Severity classification: 'Normal', 'Warning', or 'Critical'"
    )
    explanation: str = Field(
        ...,
        description="LLM-generated explanation of the result's clinical significance"
    )
    next_step: str = Field(
        ...,
        description="Actionable, safe next step recommendation (consultation, retest, etc.)"
    )


class LabAnalysisResponse(BaseModel):
    """Complete response returned by POST /analyze_labs."""
    results: List[LabResultItem]
    total_analyzed: int
    critical_count: int
    warning_count: int
    normal_count: int
    disclaimer: Optional[str] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class HealthResponse(BaseModel):
    """System health check response."""
    status: str = "ok"
    version: str = "1.0.0"
    mcp_server: str = "ready"
    llm_configured: bool = False
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
