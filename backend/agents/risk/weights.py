# Risk scoring weights
# Higher value = higher risk

RISK_WEIGHTS = {
    "salary_mismatch": 30,
    "pan_mismatch": 30,
    "name_mismatch": 20,
    "bank_mismatch": 15,
    "dob_mismatch": 20,
    "missing_document": 10,
    "fraud_detected": 40,
}

# Risk level thresholds

RISK_THRESHOLDS = {
    "low": 20,
    "medium": 50,
    "high": 100,
}
