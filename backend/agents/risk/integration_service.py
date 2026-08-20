import requests

from backend.agents.risk.adapter import adapt_member4_result
from backend.agents.risk.risk_engine import assess_risk
from backend.agents.summary.summary import generate_summary


MEMBER4_BASE_URL = "http://localhost:8000"


def process_application(application_id: str) -> dict:
    """
    Fetch Member 4's validation/fraud result,
    run Member 5 risk assessment,
    and generate the AI summary.
    """

    # 1. Get validation + fraud result from Member 4
    url = f"{MEMBER4_BASE_URL}/validation/{application_id}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    member4_result = response.json()

    # 2. Convert Member 4 schema to Risk Engine schema
    risk_input = adapt_member4_result(member4_result)

    # 3. Run deterministic risk engine
    risk_result = assess_risk(risk_input)

    # 4. Generate AI explanation
    summary = generate_summary(risk_result)

    # 5. Return final result
    return {
        "application_id": application_id,
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "recommendation": risk_result["recommendation"],
        "reasons": risk_result["reasons"],
        "summary": summary
    }