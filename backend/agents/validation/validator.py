"""
Validation engine class that orchestrates individual validation checks,
extracts and cleans data from multiple documents, and coordinates with the FraudDetector.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from backend.agents.extraction import store as extraction_store
from backend.agents.extraction.schemas import ExtractResponse
from backend.agents.validation.schemas import ValidationResult, ValidationCheck, ValidationSummary
from backend.agents.validation.rules import (
    validate_pan_format,
    validate_ifsc_format,
    compare_names,
    compare_dob,
    compare_addresses,
    compare_salary,
    check_required_documents,
    check_expiry,
    detect_pan_conflict,
)
from backend.agents.fraud.fraud_detector import FraudDetector
from backend.agents.validation import store as validation_store

logger = logging.getLogger("validation.engine")


class ValidationEngine:
    """Orchestrates validation rules and triggers fraud detection on extracted data."""

    def __init__(self, fraud_detector: Optional[FraudDetector] = None):
        self.fraud_detector = fraud_detector or FraudDetector()

    def validate(
        self, application_id: str, extracted_data: Optional[ExtractResponse] = None
    ) -> ValidationResult:
        """
        Runs validation and fraud checks for the given application_id.
        Obtains extracted data from Member 3's store if not provided.
        """
        logger.info("Starting validation for application_id: %s", application_id)

        # 1. Retrieve extracted data
        stored_extraction = extracted_data or extraction_store.get(application_id)
        if not stored_extraction:
            raise ValueError(f"No extraction data found for application_id: {application_id}")

        # 2. Extract values from documents
        names_by_source: Dict[str, Optional[str]] = {}
        dobs_by_source: Dict[str, Optional[str]] = {}
        addresses_by_source: Dict[str, Optional[str]] = {}
        pans_by_source: Dict[str, Optional[str]] = {}
        expiry_dates_by_doc: Dict[str, Optional[str]] = {}

        present_docs: List[str] = []

        # Salary variables
        payslip_net: Optional[str] = None
        payslip_gross: Optional[str] = None
        bank_credits: Optional[str] = None
        itr_annual: Optional[str] = None

        # IFSC
        ifsc_code: Optional[str] = None

        # Gather data from each document
        for doc in stored_extraction.documents:
            doc_type = doc.fields.document_meta.document_type
            doc_type_val = doc_type.value if hasattr(doc_type, "value") else str(doc_type)

            # Fallback document type detection from filename
            if doc_type_val == "unknown":
                filename_lower = doc.filename.lower()
                if "payslip" in filename_lower or "salary" in filename_lower:
                    doc_type_val = "payslip"
                elif "bank" in filename_lower or "statement" in filename_lower:
                    doc_type_val = "bank_statement"
                elif "itr" in filename_lower or "tax" in filename_lower:
                    doc_type_val = "itr"
                elif "aadhaar" in filename_lower or "aadhar" in filename_lower:
                    doc_type_val = "aadhaar"
                elif "pan" in filename_lower:
                    doc_type_val = "pan_card"
                elif "loan" in filename_lower:
                    doc_type_val = "loan_application"

            present_docs.append(doc_type_val)
            source_id = f"{doc_type_val} ({doc.filename})"
            fields = doc.fields

            # Collect personal info
            if fields.personal:
                if fields.personal.name:
                    names_by_source[source_id] = fields.personal.name
                if fields.personal.dob:
                    dobs_by_source[source_id] = fields.personal.dob
                if fields.personal.address:
                    addresses_by_source[source_id] = fields.personal.address
                if fields.personal.pan:
                    pans_by_source[source_id] = fields.personal.pan

            # Collect salary/income info
            if fields.income:
                if doc_type_val == "payslip":
                    if fields.income.net_salary:
                        payslip_net = fields.income.net_salary
                    if fields.income.gross_salary:
                        payslip_gross = fields.income.gross_salary
                elif doc_type_val == "bank_statement":
                    if fields.income.net_salary:
                        bank_credits = fields.income.net_salary
                    elif fields.income.gross_salary:
                        bank_credits = fields.income.gross_salary
                elif doc_type_val == "itr":
                    if fields.income.annual_income:
                        itr_annual = fields.income.annual_income
                    elif fields.income.itr_assessed_income:
                        itr_annual = fields.income.itr_assessed_income

            # Collect bank statement info
            if fields.bank:
                if fields.bank.ifsc:
                    ifsc_code = fields.bank.ifsc
                if doc_type_val == "bank_statement" and bank_credits is None:
                    # Fallback to bank balance as credit estimation
                    if fields.bank.avg_monthly_balance:
                        bank_credits = fields.bank.avg_monthly_balance

            # Parse expiry date from notes or metadata
            if fields.extraction_notes:
                notes_lower = fields.extraction_notes.lower()
                # Find patterns like "expiry: 2025-12-31" or "expires on 25/12/2026"
                match = re.search(r"expir\w*\s*(?:date)?\s*[:\-]?\s*([\d\-\/]+)", notes_lower)
                if match:
                    expiry_dates_by_doc[source_id] = match.group(1)

        # Supplement with merged fields if document-specific data is sparse
        merged = stored_extraction.merged_fields
        if merged:
            if merged.personal:
                if merged.personal.pan and not pans_by_source:
                    pans_by_source["merged"] = merged.personal.pan
                if merged.personal.name and not names_by_source:
                    names_by_source["merged"] = merged.personal.name
                if merged.personal.dob and not dobs_by_source:
                    dobs_by_source["merged"] = merged.personal.dob
                if merged.personal.address and not addresses_by_source:
                    addresses_by_source["merged"] = merged.personal.address
            if merged.bank and merged.bank.ifsc and not ifsc_code:
                ifsc_code = merged.bank.ifsc
            if merged.income:
                if merged.income.net_salary and payslip_net is None:
                    payslip_net = merged.income.net_salary
                if merged.income.gross_salary and payslip_gross is None:
                    payslip_gross = merged.income.gross_salary
                if merged.income.annual_income and itr_annual is None:
                    itr_annual = merged.income.annual_income

        # 3. Execute validation rules
        checks: List[ValidationCheck] = []

        # PAN format
        ref_pan = None
        for src, p in pans_by_source.items():
            if "pan_card" in src:
                ref_pan = p
                break
        if not ref_pan and pans_by_source:
            ref_pan = list(pans_by_source.values())[0]
        pan_check = validate_pan_format(ref_pan)
        checks.append(pan_check)

        # IFSC format
        ifsc_check = validate_ifsc_format(ifsc_code)
        checks.append(ifsc_check)

        # Name matching
        name_check = compare_names(names_by_source)
        checks.append(name_check)

        # DOB matching
        dob_check = compare_dob(dobs_by_source)
        checks.append(dob_check)

        # Address matching
        address_check = compare_addresses(addresses_by_source)
        checks.append(address_check)

        # Salary cross-check
        salary_check = compare_salary(payslip_net, payslip_gross, bank_credits, itr_annual)
        checks.append(salary_check)

        # Required documents
        required_docs = ["pan_card", "payslip", "bank_statement"]
        docs_check = check_required_documents(present_docs, required_docs)
        checks.append(docs_check)

        # Expiry check
        expiry_check_obj = check_expiry(expiry_dates_by_doc)
        checks.append(expiry_check_obj)

        # Conflicting PAN
        pan_conflict_check = detect_pan_conflict(pans_by_source)
        checks.append(pan_conflict_check)

        # 4. Generate validation category summary
        salary_summary = salary_check.passed
        pan_summary = pan_check.passed and pan_conflict_check.passed
        name_summary = name_check.passed
        dob_summary = dob_check.passed
        address_summary = address_check.passed
        ifsc_summary = ifsc_check.passed
        docs_summary = docs_check.passed

        val_summary = ValidationSummary(
            salary=salary_summary,
            pan=pan_summary,
            name=name_summary,
            dob=dob_summary,
            address=address_summary,
            ifsc=ifsc_summary,
            documents=docs_summary,
        )

        # 5. Run Fraud Detector
        fraud_summary = self.fraud_detector.detect_fraud(checks)

        # 6. Build the final result
        result = ValidationResult(
            application_id=application_id,
            status="completed",
            validation=val_summary,
            checks=checks,
            fraud=fraud_summary,
        )

        # 7. Persist result in validation store
        validation_store.save(result)

        logger.info(
            "Validation complete for application_id: %s. Status: %s, Fraud Score: %d",
            application_id,
            result.status,
            fraud_summary.fraud_score,
        )

        return result
