"""Clinical Lab Results Agent Orchestrator.

================================================================================
CATEGORY B: HUMAN IMPLEMENTATION REQUIRED
================================================================================
This module implements the core agent orchestration pipeline:
INPUT -> VALIDATE -> CLASSIFY -> ROUTE -> EXPLAIN -> STRUCTURED RESULT

WORKFLOW STEPS TO IMPLEMENT:
- TODO 1: Call reference-range lookup for each lab test (via MCP tool or direct module).
- TODO 2: Classify each lab result into 'Normal', 'Warning', 'Critical', or 'Unknown'.
- TODO 3: Route and sort results by priority:
          1. Critical (Urgent attention)
          2. Warning  (Follow-up)
          3. Normal   (Routine)
          4. Unknown  (Unclassified)
- TODO 4: Invoke the LLM explanation mechanism (via MCP tool or LLM engine).
- TODO 5: Construct and return the final LabAnalysisResponse model with summary statistics.
================================================================================
"""

import logging
from typing import List
from .models import (
    LabItem,
    LabResultItem,
    LabAnalysisResponse,
    SeverityLevel
)
from .reference_ranges import get_reference_range
from .classifier import classify_lab
from .llm import generate_lab_explanation

logger = logging.getLogger(__name__)

# Severity priority ranking for routing/sorting
SEVERITY_ORDER = {
    SeverityLevel.CRITICAL.value: 1,
    SeverityLevel.WARNING.value: 2,
    SeverityLevel.NORMAL.value: 3,
    SeverityLevel.UNKNOWN.value: 4
}


async def run_lab_analysis_agent(labs: List[LabItem]) -> LabAnalysisResponse:
    """
    Orchestrate the complete Classify -> Route -> Explain pipeline.

    Args:
        labs (List[LabItem]): Validated list of input laboratory tests.

    Returns:
        LabAnalysisResponse: Structured response with sorted results and severity statistics.
    """
    analyzed_items: List[dict] = []

    # ==========================================================================
    # STEP 1 & 2: CLASSIFY
    # ==========================================================================
    for item in labs:
        # ----------------------------------------------------------------------
        # TODO 1: HUMAN IMPLEMENTATION REQUIRED - Reference Range Lookup
        # Query the reference range lookup tool/repository for this test.
        # Handle cases where test_name is known vs unknown.
        # ----------------------------------------------------------------------
        ref = get_reference_range(item.test_name)
        ref_str = ref.to_range_string() if ref else "Standard range unavailable"

        # ----------------------------------------------------------------------
        # TODO 2: HUMAN IMPLEMENTATION REQUIRED - Classify Result
        # Evaluate value against bounds using classify_lab or MCP tool.
        # Determine status: 'Normal', 'Warning', 'Critical', or 'Unknown'.
        # ----------------------------------------------------------------------
        status = classify_lab(item.test_name, item.value, item.unit, ref)

        analyzed_items.append({
            "test_name": item.test_name,
            "value": item.value,
            "unit": item.unit,
            "reference_range": ref_str,
            "status": status,
            "ref_obj": ref
        })

    # ==========================================================================
    # STEP 3: ROUTE (Priority Sorting)
    # ==========================================================================
    # --------------------------------------------------------------------------
    # TODO 3: HUMAN IMPLEMENTATION REQUIRED - Route & Sort by Severity
    # Ensure all Critical results appear first, Warning second, Normal last.
    # --------------------------------------------------------------------------
    sorted_items = sorted(
        analyzed_items,
        key=lambda x: SEVERITY_ORDER.get(x["status"], 99)
    )

    # ==========================================================================
    # STEP 4: EXPLAIN
    # ==========================================================================
    results_list: List[LabResultItem] = []
    critical_count = 0
    warning_count = 0
    normal_count = 0

    for item in sorted_items:
        status = item["status"]

        # Track counts
        if status == SeverityLevel.CRITICAL.value:
            critical_count += 1
        elif status == SeverityLevel.WARNING.value:
            warning_count += 1
        elif status == SeverityLevel.NORMAL.value:
            normal_count += 1

        # ----------------------------------------------------------------------
        # TODO 4: HUMAN IMPLEMENTATION REQUIRED - LLM Explanation
        # Call the LLM explanation generator (or explain_lab MCP tool)
        # to generate dynamic explanation and recommended next steps.
        # ----------------------------------------------------------------------
        explanation_data = await generate_lab_explanation(
            test_name=item["test_name"],
            value=item["value"],
            unit=item["unit"],
            status=status,
            reference_range=item["reference_range"]
        )

        # ----------------------------------------------------------------------
        # TODO 5: HUMAN IMPLEMENTATION REQUIRED - Construct Result Item
        # Package the evaluated data into a LabResultItem instance.
        # ----------------------------------------------------------------------
        result_item = LabResultItem(
            test_name=item["test_name"],
            value=item["value"],
            unit=item["unit"],
            reference_range=item["reference_range"],
            status=status,
            explanation=explanation_data.get("explanation", "No explanation available."),
            next_step=explanation_data.get("next_step", "Consult your healthcare provider.")
        )
        results_list.append(result_item)

    # Construct final API response
    return LabAnalysisResponse(
        results=results_list,
        total_analyzed=len(results_list),
        critical_count=critical_count,
        warning_count=warning_count,
        normal_count=normal_count
    )
