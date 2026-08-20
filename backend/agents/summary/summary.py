import os

from dotenv import load_dotenv
from google import genai

from .prompt import build_summary_prompt


load_dotenv()


def generate_summary(risk_result: dict) -> str:
    """
    Generate an AI explanation of an already-determined risk decision.
    Gemini explains the decision; it does not make the decision.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return _fallback_summary(risk_result)

    try:
        client = genai.Client(api_key=api_key)

        prompt = build_summary_prompt(risk_result)

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        if response.text:
            return response.text.strip()

    except Exception as error:
        print(f"Gemini summary error: {error}")

    return _fallback_summary(risk_result)


def _fallback_summary(risk_result: dict) -> str:
    risk_score = risk_result.get("risk_score", 0)
    risk_level = risk_result.get("risk_level", "UNKNOWN")
    recommendation = risk_result.get(
        "recommendation",
        "MANUAL_REVIEW"
    )
    reasons = risk_result.get("reasons", [])

    if recommendation == "APPROVE":
        decision_text = (
            "The application is recommended for approval."
        )
    elif recommendation == "MANUAL_REVIEW":
        decision_text = (
            "The application requires manual review "
            "before a final decision."
        )
    elif recommendation == "REJECT":
        decision_text = (
            "The application is not recommended for approval."
        )
    else:
        decision_text = (
            "The application requires further assessment."
        )

    if reasons:
        reason_text = (
            "Key risk indicators: "
            + "; ".join(reasons)
            + "."
        )
    else:
        reason_text = (
            "No significant risk indicators were detected."
        )

    return (
        f"Risk Assessment: {risk_level} risk "
        f"with a score of {risk_score}/100. "
        f"{decision_text} "
        f"{reason_text}"
    )