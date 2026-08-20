"""
Fraud detector class that evaluates validation checks, computes the fraud score,
and assigns the fraud risk level.
"""

from __future__ import annotations

import logging
from typing import List

from backend.agents.validation.schemas import ValidationCheck, FraudSummary
from backend.agents.fraud.checks import evaluate_fraud_checks
from backend.agents.fraud.rules import SEVERITY_WEIGHTS, get_fraud_level

logger = logging.getLogger("fraud.detector")


class FraudDetector:
    """Combines validation findings into a deterministic fraud score and level."""

    def detect_fraud(self, checks: List[ValidationCheck]) -> FraudSummary:
        """
        Analyze validation checks, filter for triggered fraud conditions,
        calculate a weighted score, and classify the risk level.
        """
        findings = evaluate_fraud_checks(checks)
        
        # Calculate raw score by summing weights
        raw_score = 0
        for finding in findings:
            weight = SEVERITY_WEIGHTS.get(finding.severity, 0)
            raw_score += weight
            logger.debug("Triggered fraud rule: %s, severity: %s, weight: %d", 
                         finding.rule, finding.severity, weight)

        # Cap score at 100
        fraud_score = min(raw_score, 100)
        level = get_fraud_level(fraud_score)

        logger.info("Fraud assessment complete: score=%d, level=%s, findings=%d", 
                    fraud_score, level, len(findings))

        return FraudSummary(
            fraud_score=fraud_score,
            level=level,
            findings=findings
        )
