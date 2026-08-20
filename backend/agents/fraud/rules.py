"""
Severity and threshold configurations for Fraud Detection (Member 4).
"""

from __future__ import annotations

# Score weights for each severity level
SEVERITY_WEIGHTS = {
    "INFO": 0,
    "LOW": 5,
    "MEDIUM": 15,
    "HIGH": 30,
    "CRITICAL": 50,
}

# Fraud level classification thresholds
# LOW: score < 15
# MEDIUM: 15 <= score < 40
# HIGH: 40 <= score < 75
# CRITICAL: score >= 75
def get_fraud_level(score: int) -> str:
    """Determine the fraud risk level based on the cumulative fraud score."""
    if score < 15:
        return "LOW"
    elif score < 40:
        return "MEDIUM"
    elif score < 75:
        return "HIGH"
    else:
        return "CRITICAL"
