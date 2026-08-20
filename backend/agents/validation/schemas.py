"""
Pydantic schemas for the Validation & Fraud Detection Agent (Member 4).
Defines response shapes and request models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ValidationCheck(BaseModel):
    rule: str = Field(..., description="Unique name of the validation rule")
    category: str = Field("validation", description="Category of the check")
    passed: bool = Field(..., description="Whether the check passed")
    severity: str = Field("INFO", description="Severity level: INFO, LOW, MEDIUM, HIGH, CRITICAL")
    message: str = Field(..., description="Human-readable result or error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional extra details about the check")


class ValidationSummary(BaseModel):
    salary: bool = Field(False, description="True if all salary cross-checks passed or are not applicable")
    pan: bool = Field(False, description="True if PAN format check passed and no PAN conflicts are found")
    name: bool = Field(False, description="True if names are consistent across all documents or data is insufficient")
    dob: bool = Field(False, description="True if DOBs are consistent across all documents or data is insufficient")
    address: bool = Field(False, description="True if addresses are consistent across all documents or data is insufficient")
    ifsc: bool = Field(False, description="True if IFSC format check passed or is not applicable")
    documents: bool = Field(False, description="True if all required documents are present")


class FraudFinding(BaseModel):
    rule: str = Field(..., description="Name of the triggered fraud indicator rule")
    severity: str = Field(..., description="Severity level: INFO, LOW, MEDIUM, HIGH, CRITICAL")
    triggered: bool = Field(..., description="Whether the fraud check triggered")
    message: str = Field(..., description="Details of the finding")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional extra details")


class FraudSummary(BaseModel):
    fraud_score: int = Field(0, description="Deterministic fraud score capped at 100")
    level: str = Field("LOW", description="Fraud level: LOW, MEDIUM, HIGH, CRITICAL")
    findings: List[FraudFinding] = Field(default_factory=list, description="List of triggered fraud findings")


class ValidationResult(BaseModel):
    application_id: str = Field(..., description="Unique application ID")
    status: str = Field("completed", description="Status of the validation process")
    validation: ValidationSummary = Field(..., description="Summary status of each validation category")
    checks: List[ValidationCheck] = Field(default_factory=list, description="Detailed list of all validation checks performed")
    fraud: FraudSummary = Field(..., description="Overall fraud assessment and score")


class ValidateRequest(BaseModel):
    application_id: str = Field(..., description="Unique application ID to run validation for")
