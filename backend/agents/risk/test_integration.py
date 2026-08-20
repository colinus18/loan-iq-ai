from backend.agents.risk.adapter import adapt_member4_result
from backend.agents.risk.risk_engine import assess_risk
from backend.agents.summary.summary import generate_summary

member4_result = {
    "application_id": "M4-INTEGRATION-TEST-003",
    "status": "completed",

    "validation": {
        "salary": True,
        "pan": True,
        "name": True,
        "dob": True,
        "address": True,
        "ifsc": True,
        "documents": False
    },

    "checks": [
        {
            "rule": "required_documents",
            "category": "validation",
            "passed": False,
            "severity": "HIGH",
            "message": "Required documents are missing: pan_card.",
            "details": {
                "present": ["payslip", "bank_statement"],
                "required": [
                    "pan_card",
                    "payslip",
                    "bank_statement"
                ],
                "missing": ["pan_card"]
            }
        }
    ],

    "fraud": {
        "fraud_score": 30,
        "level": "MEDIUM",
        "findings": [
            {
                "rule": "required_documents",
                "severity": "HIGH",
                "triggered": True,
                "message": "Required documents are missing: pan_card."
            }
        ]
    }
}


# Step 1: Convert Member 4 output
risk_input = adapt_member4_result(member4_result)

print("\n=== ADAPTED MEMBER 4 RESULT ===")
print(risk_input)


# Step 2: Run your Risk Engine
risk_result = assess_risk(risk_input)

print("\n=== MEMBER 5 RISK RESULT ===")
print(risk_result)
summary = generate_summary(risk_result)

print("\n=== GEMINI SUMMARY ===")
print(summary)