from .calculator import calculate_risk_score


def assess_risk(application_data: dict) -> dict:
    validation = application_data.get("validation", {})
    fraud = application_data.get("fraud", {})

    result = calculate_risk_score(
        validation=validation,
        fraud=fraud,
    )

    return result