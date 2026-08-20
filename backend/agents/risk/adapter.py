def adapt_member4_result(member4_result: dict) -> dict:
    """
    Convert Member 4's Validation + Fraud response
    into the input format expected by Member 5's Risk Engine.
    """

    validation = member4_result.get("validation", {})
    fraud = member4_result.get("fraud", {})

    # Extract missing documents from validation checks
    missing_documents = []

    for check in member4_result.get("checks", []):
        if check.get("rule") == "required_documents":
            details = check.get("details", {})
            missing_documents.extend(
                details.get("missing", [])
            )

    # Determine whether fraud was actually triggered
    fraud_detected = any(
        finding.get("triggered", False)
        for finding in fraud.get("findings", [])
    )

    return {
        "validation": {
            "salary_match": validation.get("salary", True),
            "pan_match": validation.get("pan", True),
            "name_match": validation.get("name", True),
            "dob_match": validation.get("dob", True),

            # Member 4 currently provides IFSC validation,
            # not a separate bank-details-match check.
            "bank_match": validation.get("ifsc", True),

            "missing_documents": missing_documents
        },

        "fraud": {
            "fraud_detected": fraud_detected,
            "fraud_score": fraud.get("fraud_score", 0)
        }
    }