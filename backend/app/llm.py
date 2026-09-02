"""LLM Provider and Clinical Explanation Engine.

================================================================================
CATEGORY B: HUMAN IMPLEMENTATION REQUIRED
================================================================================
This module interfaces with the Google Gemini LLM API (or accessible provider)
to generate clinical explanations and recommended next steps for lab results.

PROMPT DESIGN CONSTRAINTS & REQUIREMENTS TO IMPLEMENT:
1. Explain WHY the lab test result was flagged (comparing value vs reference range).
2. Explain the general physiological/clinical significance of this finding.
3. Recommend a safe, actionable, non-diagnostic next step (e.g. repeat test, discuss with physician).
4. STRICT MEDICAL SAFETY:
   - AVOID diagnosing the patient with specific diseases.
   - AVOID inventing hypothetical patient history or symptoms.
   - Explicitly frame statements as general clinical knowledge, not medical advice.
5. Return clean structured JSON:
   {
       "explanation": "<clinical interpretation>",
       "next_step": "<safe actionable recommendation>"
   }
================================================================================
"""

import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Attempt to configure Gemini client safely
_gemini_client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        from google import genai
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Google GenAI client initialized successfully.")
    except Exception as e:
        logger.warning(f"Failed to initialize google-genai client: {e}. Fallback mode active.")
else:
    logger.info("No valid GEMINI_API_KEY found. Operating in fallback explanation mode.")


def get_clinical_prompt(test_name: str, value: float, unit: str, status: str, reference_range: str) -> str:
    """
    Construct the clinical explanation prompt sent to the LLM.

    Args:
        test_name (str): Name of the test.
        value (float): Measured numeric value.
        unit (str): Measurement unit.
        status (str): Severity flag ('Normal', 'Warning', 'Critical', 'Unknown').
        reference_range (str): Normal reference interval.

    Returns:
        str: Formatted LLM prompt string.
    """
    # ==========================================================================
    # TODO: HUMAN IMPLEMENTATION REQUIRED
    # Design and implement your clinical prompt here.
    # Ensure instructions adhere to medical safety guidelines and structured output.
    # ==========================================================================

    prompt = f"""You are a clinical laboratory explanation assistant.
Analyze the following laboratory test result and provide a concise, non-diagnostic clinical explanation.

TEST DETAILS:
- Test Name: {test_name}
- Value: {value} {unit}
- Reference Range: {reference_range}
- Severity Classification: {status}

CONSTRAINTS:
1. Explain why this result falls into the '{status}' classification.
2. Provide general physiological context (what this test measures and what abnormal levels might indicate).
3. Suggest a safe, non-diagnostic next step for the patient or provider.
4. DO NOT provide a definitive medical diagnosis.
5. DO NOT invent patient symptoms or medical history.
6. Return your response ONLY as valid JSON in this format:
{{
  "explanation": "Your concise clinical explanation here.",
  "next_step": "Your safe recommended next step here."
}}
"""
    return prompt


async def generate_lab_explanation(
    test_name: str,
    value: float,
    unit: str,
    status: str,
    reference_range: str
) -> Dict[str, str]:
    """
    Generate an explanation for an individual lab test result using the LLM.

    Args:
        test_name: Name of the test
        value: Numeric value
        unit: Unit string
        status: 'Normal', 'Warning', 'Critical', 'Unknown'
        reference_range: Human-readable reference range

    Returns:
        Dict with keys 'explanation' and 'next_step'
    """
    # ==========================================================================
    # TODO: HUMAN IMPLEMENTATION REQUIRED
    # Implement the complete LLM query and JSON response parsing workflow:
    # 1. Generate the prompt via get_clinical_prompt(...).
    # 2. Call the LLM API using the client.
    # 3. Parse and validate the response JSON.
    # 4. Handle API timeouts, rate limits, or invalid JSON with safe fallbacks.
    # ==========================================================================

    # --- SKELETON EXECUTION & FALLBACK IMPLEMENTATION ---
    if _gemini_client:
        try:
            prompt = get_clinical_prompt(test_name, value, unit, status, reference_range)
            response = _gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            response_text = response.text.strip()
            
            # Extract JSON block if wrapped in markdown code fence
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            parsed = json.loads(response_text)
            if "explanation" in parsed and "next_step" in parsed:
                return {
                    "explanation": str(parsed["explanation"]),
                    "next_step": str(parsed["next_step"])
                }
        except Exception as e:
            logger.error(f"LLM generation failed for {test_name}: {e}. Utilizing structured clinical fallback.")

    # Safe Structured Clinical Fallback (used when API key is unset or API call fails)
    return generate_fallback_explanation(test_name, value, unit, status, reference_range)


def generate_fallback_explanation(
    test_name: str,
    value: float,
    unit: str,
    status: str,
    reference_range: str
) -> Dict[str, str]:
    """Safe, deterministic clinical fallback explanation when LLM is offline or unconfigured."""
    if status == "Normal":
        return {
            "explanation": f"{test_name} result of {value} {unit} is within the expected standard physiological reference range ({reference_range}).",
            "next_step": "Routine monitoring as indicated by your primary care provider during regular wellness visits."
        }
    elif status == "Warning":
        return {
            "explanation": f"{test_name} result of {value} {unit} shows a moderate deviation outside the standard reference range ({reference_range}).",
            "next_step": "Discuss this result with your healthcare provider to assess potential contributing lifestyle or dietary factors and determine if retesting is warranted."
        }
    elif status == "Critical":
        return {
            "explanation": f"CRITICAL FINDING: {test_name} result of {value} {unit} is significantly outside safe physiological limits ({reference_range}) and requires urgent medical attention.",
            "next_step": "Contact your treating physician or seek immediate medical evaluation at an urgent care or emergency facility."
        }
    else:
        return {
            "explanation": f"{test_name} result of {value} {unit} could not be automatically evaluated against a known reference range.",
            "next_step": "Review with your ordering physician or lab provider for laboratory-specific reference ranges."
        }
