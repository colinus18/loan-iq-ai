"""
Evaluator to map validation check failures to fraud findings.
"""

from __future__ import annotations

from typing import List
from backend.agents.validation.schemas import ValidationCheck, FraudFinding


def evaluate_fraud_checks(checks: List[ValidationCheck]) -> List[FraudFinding]:
    """
    Examine the list of completed validation checks and identify
    any triggered fraud findings.
    """
    findings: List[FraudFinding] = []
    for check in checks:
        # A check failure (passed=False) with a severity above INFO triggers a fraud finding
        if not check.passed and check.severity != "INFO":
            findings.append(
                FraudFinding(
                    rule=check.rule,
                    severity=check.severity,
                    triggered=True,
                    message=check.message,
                    details=check.details
                )
            )
    return findings
