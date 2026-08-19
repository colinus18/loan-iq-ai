from backend.agents.summary.summary import generate_summary


risk_result = {
    "risk_score": 100,
    "risk_level": "HIGH",
    "recommendation": "REJECT",
    "reasons": [
        "Salary mismatch detected",
        "PAN mismatch detected",
        "Potential fraud detected"
    ]
}


summary = generate_summary(risk_result)

print(summary)