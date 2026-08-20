from backend.agents.risk.adapter import adapt_member4_result


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


adapted = adapt_member4_result(member4_result)

print(adapted)