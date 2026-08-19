from .weights import RISK_WEIGHTS, RISK_THRESHOLDS


def calculate_risk_score(validation: dict, fraud: dict) -> dict:
    score = 0
    reasons = []

    if not validation.get("salary_match", True):
        score += RISK_WEIGHTS["salary_mismatch"]
        reasons.append("Salary mismatch detected")

    if not validation.get("pan_match", True):
        score += RISK_WEIGHTS["pan_mismatch"]
        reasons.append("PAN mismatch detected")

    if not validation.get("name_match", True):
        score += RISK_WEIGHTS["name_mismatch"]
        reasons.append("Name mismatch detected")

    if not validation.get("bank_match", True):
        score += RISK_WEIGHTS["bank_mismatch"]
        reasons.append("Bank details mismatch detected")

    if not validation.get("dob_match", True):
        score += RISK_WEIGHTS["dob_mismatch"]
        reasons.append("Date of birth mismatch detected")

    missing_documents = validation.get("missing_documents", [])

    if missing_documents:
        score += (
            len(missing_documents)
            * RISK_WEIGHTS["missing_document"]
        )

        reasons.append(
            f"Missing documents: {', '.join(missing_documents)}"
        )

    if fraud.get("fraud_detected", False):
        score += RISK_WEIGHTS["fraud_detected"]
        reasons.append("Potential fraud detected")

    # Cap score at 100
    score = min(score, 100)

    if score <= RISK_THRESHOLDS["low"]:
        risk_level = "LOW"
        recommendation = "APPROVE"

    elif score <= RISK_THRESHOLDS["medium"]:
        risk_level = "MEDIUM"
        recommendation = "MANUAL_REVIEW"

    else:
        risk_level = "HIGH"
        recommendation = "REJECT"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "reasons": reasons,
    }
