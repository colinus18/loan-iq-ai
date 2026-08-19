"""
Pydantic schemas for the AI Extraction Agent (Member 3).
Defines structured output shapes for extracted document fields,
API request models, and response envelopes.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

class DocumentType(str, Enum):
    PAYSLIP        = "payslip"
    BANK_STATEMENT = "bank_statement"
    ITR            = "itr"
    AADHAAR        = "aadhaar"
    PAN_CARD       = "pan_card"
    LOAN_APP       = "loan_application"
    UNKNOWN        = "unknown"


class ExtractionStatus(str, Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    SUCCESS    = "success"
    PARTIAL    = "partial"
    FAILED     = "failed"


# ─────────────────────────────────────────────────────────────────────────────
# Core extracted-field models
# ─────────────────────────────────────────────────────────────────────────────

class PersonalInfo(BaseModel):
    name:         Optional[str] = Field(None, description="Full legal name of the applicant")
    dob:          Optional[str] = Field(None, description="Date of birth (DD/MM/YYYY or YYYY-MM-DD)")
    gender:       Optional[str] = Field(None, description="Gender of the applicant")
    pan:          Optional[str] = Field(None, description="PAN card number (e.g. ABCDE1234F)")
    aadhaar:      Optional[str] = Field(None, description="Aadhaar number (masked or full)")
    address:      Optional[str] = Field(None, description="Residential / permanent address")
    phone:        Optional[str] = Field(None, description="Contact phone number")
    email:        Optional[str] = Field(None, description="Email address")


class EmploymentInfo(BaseModel):
    employer:          Optional[str] = Field(None, description="Name of the employer / company")
    designation:       Optional[str] = Field(None, description="Job title / designation")
    employment_type:   Optional[str] = Field(None, description="Salaried / Self-employed / Business")
    date_of_joining:   Optional[str] = Field(None, description="Date the applicant joined the company")
    department:        Optional[str] = Field(None, description="Department or division")
    employee_id:       Optional[str] = Field(None, description="Employee ID / staff number")
    office_address:    Optional[str] = Field(None, description="Employer's office address")


class IncomeInfo(BaseModel):
    gross_salary:         Optional[str] = Field(None, description="Gross monthly salary (INR)")
    net_salary:           Optional[str] = Field(None, description="Net / take-home monthly salary (INR)")
    annual_income:        Optional[str] = Field(None, description="Total annual income (INR)")
    basic_salary:         Optional[str] = Field(None, description="Basic component of salary (INR)")
    hra:                  Optional[str] = Field(None, description="House rent allowance (INR)")
    other_allowances:     Optional[str] = Field(None, description="Other allowances (INR)")
    pf_deduction:         Optional[str] = Field(None, description="PF / provident fund deduction (INR)")
    tax_deducted:         Optional[str] = Field(None, description="TDS / income-tax deducted (INR)")
    itr_assessed_income:  Optional[str] = Field(None, description="Income as per ITR assessment (INR)")
    assessment_year:      Optional[str] = Field(None, description="ITR assessment year (e.g. 2023-24)")


class BankInfo(BaseModel):
    bank_name:       Optional[str] = Field(None, description="Name of the bank")
    branch:          Optional[str] = Field(None, description="Branch name and city")
    account_number:  Optional[str] = Field(None, description="Bank account number")
    account_type:    Optional[str] = Field(None, description="Savings / Current / OD")
    ifsc:            Optional[str] = Field(None, description="IFSC code of the branch")
    micr:            Optional[str] = Field(None, description="MICR code")
    opening_balance: Optional[str] = Field(None, description="Opening balance of the statement period (INR)")
    closing_balance: Optional[str] = Field(None, description="Closing balance of the statement period (INR)")
    avg_monthly_balance: Optional[str] = Field(None, description="Average monthly balance (INR)")
    statement_period_from: Optional[str] = Field(None, description="Start date of bank statement period")
    statement_period_to:   Optional[str] = Field(None, description="End date of bank statement period")


class LoanInfo(BaseModel):
    loan_amount_requested: Optional[str] = Field(None, description="Loan amount applied for (INR)")
    loan_purpose:          Optional[str] = Field(None, description="Purpose of the loan")
    loan_tenure_months:    Optional[str] = Field(None, description="Requested tenure in months")
    existing_emi:          Optional[str] = Field(None, description="Existing EMI obligations (INR/month)")
    existing_loans:        Optional[str] = Field(None, description="Details of any existing loans")


class DocumentMeta(BaseModel):
    document_type:  DocumentType = Field(DocumentType.UNKNOWN, description="Classified type of this document")
    document_date:  Optional[str] = Field(None, description="Date printed / issued on the document")
    issuing_entity: Optional[str] = Field(None, description="Entity that issued this document")
    page_count:     Optional[int] = Field(None, description="Number of pages in the source PDF")


# ─────────────────────────────────────────────────────────────────────────────
# Top-level extraction result
# ─────────────────────────────────────────────────────────────────────────────

class ExtractedFields(BaseModel):
    """
    Unified structured output produced by Gemini for a single document.
    All sub-models are optional; partial extraction is valid.
    """
    document_meta:  DocumentMeta   = Field(default_factory=DocumentMeta)
    personal:       PersonalInfo   = Field(default_factory=PersonalInfo)
    employment:     EmploymentInfo = Field(default_factory=EmploymentInfo)
    income:         IncomeInfo     = Field(default_factory=IncomeInfo)
    bank:           BankInfo       = Field(default_factory=BankInfo)
    loan:           LoanInfo       = Field(default_factory=LoanInfo)
    raw_text_snippet: Optional[str] = Field(None, description="First 500 chars of OCR text for debugging")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Gemini extraction confidence (0-1)")
    extraction_notes: Optional[str]   = Field(None, description="Any caveats or notes from the extraction model")

    def to_flat_dict(self) -> Dict[str, Any]:
        """Return a flat {key: value} dict for downstream agents."""
        flat: Dict[str, Any] = {}
        for section_name, section_model in self.model_dump().items():
            if isinstance(section_model, dict):
                for k, v in section_model.items():
                    flat[k] = v
            else:
                flat[section_name] = section_model
        return flat


# ─────────────────────────────────────────────────────────────────────────────
# Per-document result (one PDF may contain multiple document types)
# ─────────────────────────────────────────────────────────────────────────────

class SingleDocumentResult(BaseModel):
    filename:   str
    doc_index:  int = Field(0, description="Index of this doc in the upload batch (0-based)")
    fields:     ExtractedFields
    status:     ExtractionStatus = ExtractionStatus.SUCCESS
    error:      Optional[str]    = None


# ─────────────────────────────────────────────────────────────────────────────
# API request / response models
# ─────────────────────────────────────────────────────────────────────────────

class ExtractRequest(BaseModel):
    """POST /extract — body sent by OCR service (Member 2)."""
    application_id: str = Field(..., description="Unique application / session ID")
    documents: List[Dict[str, Any]] = Field(
        ...,
        description="List of docs, each with 'filename' and 'ocr_text' keys"
    )
    hint: Optional[str] = Field(None, description="Optional document-type hint from OCR layer")


class ExtractResponse(BaseModel):
    """Response envelope for POST /extract."""
    application_id:   str
    status:           ExtractionStatus
    documents:        List[SingleDocumentResult]
    merged_fields:    Optional[ExtractedFields] = Field(
        None,
        description="Fields merged across all documents in the application"
    )
    processing_time_ms: Optional[float] = None
    created_at:         datetime = Field(default_factory=datetime.utcnow)


class FieldsResponse(BaseModel):
    """Response envelope for GET /fields/{application_id}."""
    application_id: str
    status:         ExtractionStatus
    fields:         Optional[ExtractedFields]
    documents:      List[SingleDocumentResult] = []
    created_at:     Optional[datetime] = None


class ErrorResponse(BaseModel):
    detail:  str
    code:    Optional[str] = None
    hint:    Optional[str] = None
