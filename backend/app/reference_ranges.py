"""Standard Clinical Laboratory Reference Ranges Configuration.

Maintains reference ranges, units, normal physiological intervals,
and critical thresholds for common clinical laboratory tests.
"""

from typing import Dict, Optional
from .models import ReferenceRange

# Centralized reference ranges for standard laboratory tests.
# Values represent standard adult clinical laboratory reference intervals.
REFERENCE_RANGES: Dict[str, ReferenceRange] = {
    "hemoglobin": ReferenceRange(
        test_name="Hemoglobin",
        low=12.0,
        high=17.5,
        unit="g/dL",
        critical_low=7.0,
        critical_high=20.0,
        description="Oxygen-carrying protein in red blood cells. Evaluates anemia and polycythemia."
    ),
    "glucose": ReferenceRange(
        test_name="Glucose",
        low=70.0,
        high=99.0,
        unit="mg/dL",
        critical_low=50.0,
        critical_high=400.0,
        description="Fasting blood sugar level. Evaluates diabetes, hypoglycemia, and metabolic health."
    ),
    "wbc": ReferenceRange(
        test_name="WBC",
        low=4.0,
        high=11.0,
        unit="10^3/uL",
        critical_low=2.0,
        critical_high=30.0,
        description="White blood cell count. Evaluates immune response, infection, and leukemia."
    ),
    "platelets": ReferenceRange(
        test_name="Platelets",
        low=150.0,
        high=450.0,
        unit="10^3/uL",
        critical_low=50.0,
        critical_high=1000.0,
        description="Thrombocyte count. Evaluates blood clotting ability and bleeding disorders."
    ),
    "creatinine": ReferenceRange(
        test_name="Creatinine",
        low=0.6,
        high=1.2,
        unit="mg/dL",
        critical_low=0.3,
        critical_high=4.0,
        description="Waste product filtered by kidneys. Key marker for renal function and kidney health."
    ),
    "potassium": ReferenceRange(
        test_name="Potassium",
        low=3.5,
        high=5.0,
        unit="mEq/L",
        critical_low=2.8,
        critical_high=6.5,
        description="Major intracellular electrolyte. Crucial for cardiac rhythm and muscle function."
    ),
    "sodium": ReferenceRange(
        test_name="Sodium",
        low=135.0,
        high=145.0,
        unit="mEq/L",
        critical_low=120.0,
        critical_high=160.0,
        description="Primary extracellular electrolyte. Regulates osmotic pressure and fluid balance."
    ),
    "ferritin": ReferenceRange(
        test_name="Ferritin",
        low=15.0,
        high=150.0,
        unit="ug/L",
        critical_low=5.0,
        critical_high=1000.0,
        description="Iron storage protein. Used to evaluate iron deficiency or iron overload disorders."
    ),
    "hba1c": ReferenceRange(
        test_name="HbA1c",
        low=4.0,
        high=5.6,
        unit="%",
        critical_low=3.5,
        critical_high=10.0,
        description="Glycated hemoglobin. Assesses average 3-month blood glucose control."
    ),
    "hematocrit": ReferenceRange(
        test_name="Hematocrit",
        low=36.0,
        high=50.0,
        unit="%",
        critical_low=20.0,
        critical_high=60.0,
        description="Proportion of red blood cells in blood volume. Key indicator for anemia or polycythemia."
    )
}

# Alias mappings for flexible test name lookup
TEST_ALIASES: Dict[str, str] = {
    "hgb": "hemoglobin",
    "hb": "hemoglobin",
    "blood sugar": "glucose",
    "fasting glucose": "glucose",
    "fbs": "glucose",
    "glu": "glucose",
    "white blood cells": "wbc",
    "white blood count": "wbc",
    "leukocytes": "wbc",
    "lökosit": "wbc",
    "lokosit": "wbc",
    "plt": "platelets",
    "thrombocytes": "platelets",
    "trombosit": "platelets",
    "creat": "creatinine",
    "serum creatinine": "creatinine",
    "k": "potassium",
    "na": "sodium",
    "glikozile hemoglobin (hba1c)": "hba1c",
    "glikozile hemoglobin": "hba1c",
    "glycated hemoglobin": "hba1c",
    "a1c": "hba1c",
    "hct": "hematocrit",
    "hematokrit": "hematocrit"
}


def normalize_test_name(test_name: str) -> str:
    """Normalize test name string for case-insensitive and alias matching."""
    cleaned = test_name.strip().lower()
    return TEST_ALIASES.get(cleaned, cleaned)


def get_reference_range(test_name: str) -> Optional[ReferenceRange]:
    """
    Look up standard physiological reference range for a given laboratory test.
    
    Args:
        test_name: Name or alias of the test (e.g. 'Hemoglobin', 'Hgb', 'Glucose')
        
    Returns:
        ReferenceRange model if found, or None if unknown.
    """
    normalized_key = normalize_test_name(test_name)
    return REFERENCE_RANGES.get(normalized_key)


def get_all_supported_tests() -> Dict[str, ReferenceRange]:
    """Return dictionary of all configured standard reference ranges."""
    return dict(REFERENCE_RANGES)
