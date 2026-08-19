from backend.agents.risk.risk_engine import assess_risk


test_application = {
    "validation": {
        "salary_match": False,
        "pan_match": False,
        "name_match": True,
        "bank_match": False,
        "dob_match": True,
        "missing_documents": [],
    },
    "fraud": {
        "fraud_detected": True,
        "fraud_score": 80,
    },
}


result = assess_risk(test_application)

print(result)