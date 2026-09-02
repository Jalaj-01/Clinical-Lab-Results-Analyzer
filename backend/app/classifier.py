"""Lab Results Classifier Module.

================================================================================
CATEGORY B: HUMAN IMPLEMENTATION REQUIRED
================================================================================
This module defines the core clinical lab result classification logic.
You must personally implement the algorithm to evaluate numeric test values
against reference intervals and assign appropriate clinical severity status.

REQUIRED BEHAVIORS TO IMPLEMENT:
1. Distinguish between:
   - "Normal": Value is strictly within standard reference range (low <= value <= high).
   - "Warning": Value is moderately outside standard reference range (mildly elevated or mildly low).
   - "Critical": Value is severely outside standard reference range (meets or exceeds critical thresholds).
   - "Unknown": When no reference range is provided or found.

2. Edge Cases to Handle:
   - Boundary: Value exactly equal to low limit (should be Normal).
   - Boundary: Value exactly equal to high limit (should be Normal).
   - Borderline Low / High: Slightly below low or slightly above high (Warning).
   - Critical Low / High: Value <= critical_low or Value >= critical_high (Critical).
   - Missing Reference Range: ref_range is None (return "Unknown" or handle gracefully).
   - Invalid Values: NaN, Infinity, negative values where clinically impossible.
================================================================================
"""

from typing import Optional
from .models import ReferenceRange, SeverityLevel


def classify_lab(
    test_name: str,
    value: float,
    unit: str,
    ref_range: Optional[ReferenceRange] = None
) -> str:
    """
    Classify an individual laboratory result into a severity category.

    Args:
        test_name (str): Name of the laboratory test (e.g., 'Hemoglobin', 'Glucose').
        value (float): Numeric measured value from the laboratory.
        unit (str): Unit of measurement (e.g., 'g/dL', 'mg/dL').
        ref_range (Optional[ReferenceRange]): ReferenceRange object containing
            `low`, `high`, `unit`, `critical_low`, and `critical_high` bounds.

    Returns:
        str: One of SeverityLevel values:
             - "Normal"
             - "Warning"
             - "Critical"
             - "Unknown"

    Expected Threshold Logic:
        - If ref_range is None -> return SeverityLevel.UNKNOWN.value
        - If ref_range.critical_low is defined and value <= ref_range.critical_low -> return SeverityLevel.CRITICAL.value
        - If ref_range.critical_high is defined and value >= ref_range.critical_high -> return SeverityLevel.CRITICAL.value
        - If ref_range.low <= value <= ref_range.high -> return SeverityLevel.NORMAL.value
        - If value < ref_range.low or value > ref_range.high -> return SeverityLevel.WARNING.value
    """
    # ==========================================================================
    # TODO: HUMAN IMPLEMENTATION REQUIRED
    # Implement the classification logic below following the guidelines above.
    # Replace this placeholder stub with your validated implementation.
    # ==========================================================================

    # --- SKELETON PLACEHOLDER ---
    if ref_range is None:
        return SeverityLevel.UNKNOWN.value

    # Check for critical bounds
    if ref_range.critical_low is not None and value <= ref_range.critical_low:
        return SeverityLevel.CRITICAL.value
    if ref_range.critical_high is not None and value >= ref_range.critical_high:
        return SeverityLevel.CRITICAL.value

    # Check for normal physiological bounds
    if ref_range.low <= value <= ref_range.high:
        return SeverityLevel.NORMAL.value

    # Borderline/abnormal warning bounds
    if value < ref_range.low or value > ref_range.high:
        return SeverityLevel.WARNING.value

    return SeverityLevel.UNKNOWN.value
