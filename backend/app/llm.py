"""LLM Provider and Clinical Explanation Engine."""

import os
import json
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# Gemini client initialization
_gemini_client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        from google import genai
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.warning(f"Could not initialize Google GenAI client: {e}")

# Groq client initialization
_groq_client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        logger.warning(f"Could not initialize Groq client: {e}")


def get_clinical_prompt(
    test_name: str,
    value: float,
    unit: str,
    status: str,
    reference_range: str
) -> str:
    """Construct the prompt sent to the LLM for clinical explanation."""
    return f"""You are a clinical laboratory explanation assistant.
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


async def generate_lab_explanation(
    test_name: str,
    value: float,
    unit: str,
    status: str,
    reference_range: str
) -> Dict[str, str]:
    """Generate an explanation for a lab test result using LLM or clinical engine."""
    prompt = get_clinical_prompt(test_name, value, unit, status, reference_range)

    # 1. Try Groq if configured
    if _groq_client:
        try:
            chat_completion = _groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
            content = chat_completion.choices[0].message.content
            if content:
                parsed = json.loads(content)
                if "explanation" in parsed and "next_step" in parsed:
                    return {
                        "explanation": str(parsed["explanation"]),
                        "next_step": str(parsed["next_step"])
                    }
        except Exception as e:
            logger.warning(f"Groq API call failed: {e}")

    # 2. Try Gemini if configured
    if _gemini_client:
        models = [GEMINI_MODEL, "gemini-2.5-flash", "gemini-3.6-flash", "gemini-flash-latest"]
        for model_name in models:
            try:
                response = _gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and hasattr(response, "text") and response.text:
                    text = response.text.strip()
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()

                    parsed = json.loads(text)
                    if "explanation" in parsed and "next_step" in parsed:
                        return {
                            "explanation": str(parsed["explanation"]),
                            "next_step": str(parsed["next_step"])
                        }
            except Exception:
                continue

    # 3. Dynamic Clinical Explanation Engine
    return generate_fallback_explanation(test_name, value, unit, status, reference_range)


CLINICAL_KNOWLEDGE = {
    "hemoglobin": {
        "desc": "Hemoglobin is the primary iron-containing protein in red blood cells that transports oxygen from the lungs to peripheral tissues.",
        "low_warning": "Slightly low hemoglobin indicates mild anemia, which may be related to nutritional deficiency or mild blood loss.",
        "low_critical": "Critically low hemoglobin indicates severe anemia with significantly reduced oxygen delivery capacity.",
        "high_warning": "Mildly elevated hemoglobin can occur with dehydration, smoking, or living at higher altitudes.",
        "high_critical": "Markedly elevated hemoglobin suggests polycythemia or chronic hypoxic stress.",
        "next_step_low": "Consult your physician for complete blood count evaluation, iron studies, and dietary review.",
        "next_step_critical": "Seek urgent medical review with your physician or hematologist for immediate clinical assessment.",
    },
    "glucose": {
        "desc": "Glucose is the main circulating carbohydrate used as a cellular energy source.",
        "low_warning": "Mild hypoglycemia may be related to prolonged fasting, delayed meals, or medication effects.",
        "low_critical": "Severe hypoglycemia poses an immediate risk of neuroglycopenic symptoms and requires rapid carbohydrate intake.",
        "high_warning": "Mildly elevated fasting glucose may indicate impaired fasting glucose or pre-diabetic metabolic stress.",
        "high_critical": "Markedly elevated glucose suggests significant hyperglycemia requiring prompt metabolic evaluation.",
        "next_step_low": "Discuss with your physician; consider repeating fasting glucose with dietary evaluation.",
        "next_step_critical": "Contact your treating physician or urgent care immediately for blood glucose stabilization.",
    },
    "wbc": {
        "desc": "White blood cells (leukocytes) are the primary cellular defense mechanism of the immune system.",
        "low_warning": "Mild leukopenia can occur following viral illnesses or certain medications.",
        "low_critical": "Severe leukopenia (neutropenia) significantly impairs host defense against infections.",
        "high_warning": "Mild leukocytosis is a common physiological response to acute infection, inflammation, or physical stress.",
        "high_critical": "Significantly elevated WBC count requires urgent workup to differentiate acute infection from hematologic disorders.",
        "next_step_low": "Follow up with your clinician for differential count and immune status monitoring.",
        "next_step_critical": "Consult your physician or hematologist promptly for diagnostic blood work.",
    },
    "platelets": {
        "desc": "Platelets (thrombocytes) are essential cellular fragments involved in hemostasis and blood clotting.",
        "low_warning": "Mild thrombocytopenia indicates a slight reduction in platelet count that warrants monitoring.",
        "low_critical": "Critically low platelet count carries a heightened risk of spontaneous bruising and bleeding.",
        "high_warning": "Mild thrombocytosis is often reactive to systemic inflammation, iron deficiency, or recent infection.",
        "high_critical": "Significantly elevated platelet count warrants clinical evaluation for myeloproliferative processes.",
        "next_step_low": "Schedule a follow-up appointment with your physician to monitor platelet trends.",
        "next_step_critical": "Seek prompt medical consultation to prevent bleeding complications.",
    },
    "creatinine": {
        "desc": "Creatinine is a metabolic byproduct of muscle creatine breakdown filtered freely by the kidneys.",
        "low_warning": "Low creatinine is typically benign and often associated with low muscle mass or high fluid intake.",
        "low_critical": "Low serum creatinine is rarely acute but reflects reduced muscle mass or advanced malnutrition.",
        "high_warning": "Mildly elevated creatinine may indicate early renal strain, reduced hydration, or strenuous exercise.",
        "high_critical": "Significantly elevated creatinine indicates acute kidney injury or severe renal impairment.",
        "next_step_low": "Routine clinical follow-up as part of general wellness review.",
        "next_step_critical": "Seek immediate physician evaluation for comprehensive renal function testing and urinalysis.",
    }
}


def generate_fallback_explanation(
    test_name: str,
    value: float,
    unit: str,
    status: str,
    reference_range: str
) -> Dict[str, str]:
    """Generate detailed, accurate clinical explanations based on physiological data."""
    test_key = test_name.strip().lower()
    knowledge = CLINICAL_KNOWLEDGE.get(test_key)

    if status == "Normal":
        desc = knowledge["desc"] if knowledge else ""
        return {
            "explanation": f"{test_name} of {value} {unit} is within the expected standard physiological reference range ({reference_range}). {desc}".strip(),
            "next_step": "Routine monitoring as recommended by your healthcare provider."
        }

    if knowledge:
        if status == "Critical":
            explanation = f"{test_name} of {value} {unit} is critically outside reference bounds ({reference_range}). {knowledge.get('low_critical', knowledge['desc'])}"
            next_step = knowledge.get("next_step_critical", "Contact your physician immediately for urgent clinical evaluation.")
        else:
            explanation = f"{test_name} of {value} {unit} shows a moderate deviation outside the reference range ({reference_range}). {knowledge.get('high_warning', knowledge['desc'])}"
            next_step = knowledge.get("next_step_low", "Discuss with your physician to evaluate contributing factors and determine if re-testing is needed.")
        return {
            "explanation": explanation,
            "next_step": next_step
        }

    if status == "Critical":
        return {
            "explanation": f"{test_name} of {value} {unit} is significantly outside standard reference limits ({reference_range}) and warrants prompt medical evaluation.",
            "next_step": "Contact your physician or seek immediate medical review for urgent clinical evaluation."
        }
    elif status == "Warning":
        return {
            "explanation": f"{test_name} of {value} {unit} shows a moderate deviation outside the reference range ({reference_range}).",
            "next_step": "Discuss with your physician to assess contributing factors and determine if a follow-up test is recommended."
        }
    else:
        return {
            "explanation": f"{test_name} of {value} {unit} could not be matched to a standard reference interval.",
            "next_step": "Consult your clinician or laboratory report for test-specific reference ranges."
        }
