def generate_summary(risk_result: dict) -> str:
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
