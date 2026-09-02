"""Model Context Protocol (MCP) Server for Clinical Lab Analyzer.

================================================================================
CATEGORY B: HUMAN IMPLEMENTATION REQUIRED
================================================================================
This module defines the MCP server and tool interfaces used by the Clinical
Lab Analysis Agent.

REQUIRED TOOLS TO IMPLEMENT:
1. `reference_range_lookup`:
   - Input: `test_name: str`
   - Output: JSON dict with `low`, `high`, `unit`, `critical_low`, `critical_high`, `description`
   - Purpose: Retrieve physiological reference bounds for a given test.

2. `classify_lab_tool`:
   - Input: `test_name: str`, `value: float`, `unit: str`, `ref_range_json: Optional[dict]`
   - Output: JSON dict with `status` ("Normal" | "Warning" | "Critical" | "Unknown")
   - Purpose: Classify the numeric value against reference intervals.

3. `explain_lab_tool`:
   - Input: `test_name: str`, `value: float`, `unit: str`, `status: str`, `reference_range: str`
   - Output: JSON dict with `explanation: str`, `next_step: str`
   - Purpose: Generate clinical explanation and non-diagnostic safe next steps via LLM.
================================================================================
"""

import json
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP
from .reference_ranges import get_reference_range
from .classifier import classify_lab
from .models import ReferenceRange

# Initialize FastMCP Server
mcp = FastMCP("clinical-lab-server")


@mcp.tool()
async def reference_range_lookup(test_name: str) -> str:
    """
    Look up standard physiological reference range for a clinical laboratory test.

    Args:
        test_name (str): Name or abbreviation of the lab test (e.g., 'Hemoglobin', 'WBC', 'Glucose').

    Returns:
        str: JSON string containing reference bounds:
             {
                 "found": bool,
                 "test_name": str,
                 "low": float,
                 "high": float,
                 "unit": str,
                 "critical_low": Optional[float],
                 "critical_high": Optional[float],
                 "description": Optional[str]
             }
    """
    # ==========================================================================
    # TODO: HUMAN IMPLEMENTATION REQUIRED
    # Implement the MCP lookup logic:
    # 1. Normalize test name and query the reference range repository.
    # 2. Handle unknown tests by returning a structured 'not found' payload or fallback.
    # 3. Return a serialized JSON string.
    # ==========================================================================

    # --- SKELETON PLACEHOLDER ---
    ref = get_reference_range(test_name)
    if not ref:
        return json.dumps({
            "found": False,
            "test_name": test_name,
            "error": f"No standard reference range found for test '{test_name}'"
        })

    return json.dumps({
        "found": True,
        "test_name": ref.test_name,
        "low": ref.low,
        "high": ref.high,
        "unit": ref.unit,
        "critical_low": ref.critical_low,
        "critical_high": ref.critical_high,
        "description": ref.description,
        "range_string": ref.to_range_string()
    })


@mcp.tool()
async def classify_lab_tool(
    test_name: str,
    value: float,
    unit: str,
    ref_range_json: Optional[str] = None
) -> str:
    """
    Classify a laboratory result into Normal, Warning, or Critical severity.

    Args:
        test_name (str): The name of the lab test.
        value (float): The numeric measured lab value.
        unit (str): The unit of measurement.
        ref_range_json (Optional[str]): Optional JSON string with reference bounds.

    Returns:
        str: JSON string containing:
             {
                 "test_name": str,
                 "value": float,
                 "unit": str,
                 "status": "Normal" | "Warning" | "Critical" | "Unknown"
             }
    """
    # ==========================================================================
    # TODO: HUMAN IMPLEMENTATION REQUIRED
    # Implement the MCP tool classification logic:
    # 1. Deserialize ref_range_json into a ReferenceRange model (or fetch via lookup).
    # 2. Invoke the classifier algorithm (classify_lab).
    # 3. Return the classification status in JSON format.
    # ==========================================================================

    # --- SKELETON PLACEHOLDER ---
    ref_obj = None
    if ref_range_json:
        try:
            data = json.loads(ref_range_json)
            if data.get("found", True) and "low" in data and "high" in data:
                ref_obj = ReferenceRange(
                    test_name=data.get("test_name", test_name),
                    low=data["low"],
                    high=data["high"],
                    unit=data.get("unit", unit),
                    critical_low=data.get("critical_low"),
                    critical_high=data.get("critical_high"),
                    description=data.get("description")
                )
        except Exception:
            ref_obj = get_reference_range(test_name)
    else:
        ref_obj = get_reference_range(test_name)

    status = classify_lab(test_name, value, unit, ref_obj)
    return json.dumps({
        "test_name": test_name,
        "value": value,
        "unit": unit,
        "status": status
    })


@mcp.tool()
async def explain_lab_tool(
    test_name: str,
    value: float,
    unit: str,
    status: str,
    reference_range: str
) -> str:
    """
    Generate an LLM-powered clinical explanation and suggested next step.

    Args:
        test_name (str): Name of the test.
        value (float): Measured value.
        unit (str): Measurement unit.
        status (str): Severity classification ('Normal', 'Warning', 'Critical').
        reference_range (str): Reference range string (e.g., '12.0 - 17.5 g/dL').

    Returns:
        str: JSON string containing:
             {
                 "explanation": str,
                 "next_step": str
             }
    """
    # ==========================================================================
    # TODO: HUMAN IMPLEMENTATION REQUIRED
    # Implement the MCP tool explanation logic:
    # 1. Connect to the LLM explanation generator in llm.py.
    # 2. Ensure prompt constraints and non-diagnostic disclaimers are respected.
    # 3. Handle LLM rate limits and fallback gracefully.
    # ==========================================================================

    # --- SKELETON PLACEHOLDER (Imports deferred to avoid circular dependencies) ---
    from .llm import generate_lab_explanation
    result = await generate_lab_explanation(test_name, value, unit, status, reference_range)
    return json.dumps(result)


def get_mcp_server() -> FastMCP:
    """Return the configured FastMCP server instance."""
    return mcp
