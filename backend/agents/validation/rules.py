"""
Deterministic validation rules for Member 4.
No LLM calls. Fully typed, robust, and handles missing/null values safely.
"""

from __future__ import annotations

import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.agents.validation.schemas import ValidationCheck

logger = logging.getLogger("validation.rules")

# Regex patterns
PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
IFSC_REGEX = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")


def parse_float(val: Any) -> Optional[float]:
    """Safely convert any currency/monetary string or number to float."""
    if val is None:
        return None
    val_str = str(val).strip()
    if not val_str:
        return None
    try:
        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r"[₹$,\s]", "", val_str)
        if not cleaned:
            return None
        return float(cleaned)
    except ValueError:
        logger.warning("Failed to parse numeric value from: %r", val)
        return None


def normalize_date_string(val: Optional[str]) -> Optional[str]:
    """
    Standardize common date formats to YYYY-MM-DD.
    Supports DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD.
    """
    if not val:
        return None
    val = val.strip()

    # DD/MM/YYYY or DD-MM-YYYY
    m = re.fullmatch(r"(\d{2})[\/\-\.](\d{2})[\/\-\.](\d{4})", val)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"

    # YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", val)
    if m:
        return val

    return val


def validate_pan_format(pan: Optional[str]) -> ValidationCheck:
    """Validate standard Indian PAN format: AAAAA9999A."""
    if not pan:
        return ValidationCheck(
            rule="pan_format",
            category="validation",
            passed=False,
            severity="LOW",
            message="PAN number is missing or not extracted.",
            details={"pan": None}
        )

    pan_clean = pan.strip().upper()
    if PAN_REGEX.match(pan_clean):
        return ValidationCheck(
            rule="pan_format",
            category="validation",
            passed=True,
            severity="INFO",
            message="PAN format is valid.",
            details={"pan": pan_clean}
        )
    else:
        return ValidationCheck(
            rule="pan_format",
            category="validation",
            passed=False,
            severity="HIGH",
            message=f"Invalid PAN format: '{pan}'",
            details={"pan": pan}
        )


def validate_ifsc_format(ifsc: Optional[str]) -> ValidationCheck:
    """Validate standard Indian IFSC format: 4 letters + 0 + 6 alphanumeric characters."""
    if not ifsc:
        return ValidationCheck(
            rule="ifsc_format",
            category="validation",
            passed=True,  # Mark as true but not_applicable since it's optional
            severity="INFO",
            message="IFSC code not provided / not applicable.",
            details={"ifsc": None, "status": "not_applicable"}
        )

    ifsc_clean = ifsc.strip().upper()
    if IFSC_REGEX.match(ifsc_clean):
        return ValidationCheck(
            rule="ifsc_format",
            category="validation",
            passed=True,
            severity="INFO",
            message="IFSC format is valid.",
            details={"ifsc": ifsc_clean}
        )
    else:
        return ValidationCheck(
            rule="ifsc_format",
            category="validation",
            passed=False,
            severity="HIGH",
            message=f"Invalid IFSC format: '{ifsc}'",
            details={"ifsc": ifsc}
        )


def compare_names(names_by_source: Dict[str, Optional[str]]) -> ValidationCheck:
    """
    Compare names across multiple sources.
    Uses token matching & subset logic to handle spacing and punctuation.
    """
    # Filter out empty/None entries
    valid_names = {src: val for src, val in names_by_source.items() if val and val.strip()}

    if len(valid_names) <= 1:
        return ValidationCheck(
            rule="name_match",
            category="validation",
            passed=True,
            severity="INFO",
            message="Name matching skipped: insufficient data (0 or 1 source available).",
            details={"sources": list(valid_names.keys()), "status": "insufficient_data"}
        )

    def tokenize_name(name_str: str) -> set[str]:
        cleaned = re.sub(r"[^\w\s]", "", name_str.lower()).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return set(cleaned.split())

    sources = list(valid_names.keys())
    mismatches = []

    # Pairwise comparison
    for i in range(len(sources)):
        for j in range(i + 1, len(sources)):
            src1, src2 = sources[i], sources[j]
            w1 = tokenize_name(valid_names[src1])
            w2 = tokenize_name(valid_names[src2])

            if not w1 or not w2:
                mismatches.append(f"{src1} vs {src2} (empty name)")
                continue

            # Check Jaccard similarity and subset matching
            intersection = w1.intersection(w2)
            union = w1.union(w2)
            jaccard = len(intersection) / len(union) if union else 0.0

            is_subset = w1.issubset(w2) or w2.issubset(w1)

            # Name match criteria: Jaccard similarity >= 0.6 or one is subset of other
            if jaccard < 0.6 and not is_subset:
                mismatches.append(f"'{valid_names[src1]}' ({src1}) vs '{valid_names[src2]}' ({src2})")

    if mismatches:
        return ValidationCheck(
            rule="name_match",
            category="validation",
            passed=False,
            severity="HIGH",
            message=f"Name consistency mismatch found in sources: {'; '.join(mismatches)}",
            details={"names": valid_names, "mismatches": mismatches}
        )

    return ValidationCheck(
        rule="name_match",
        category="validation",
        passed=True,
        severity="INFO",
        message="Names match and are consistent across all documents.",
        details={"names": valid_names}
    )


def compare_dob(dobs_by_source: Dict[str, Optional[str]]) -> ValidationCheck:
    """Compare DOB across all available documents."""
    valid_dobs = {}
    for src, dob in dobs_by_source.items():
        if dob:
            normalized = normalize_date_string(dob)
            if normalized:
                valid_dobs[src] = normalized

    if len(valid_dobs) <= 1:
        return ValidationCheck(
            rule="dob_match",
            category="validation",
            passed=True,
            severity="INFO",
            message="DOB matching skipped: insufficient data (0 or 1 source available).",
            details={"sources": list(valid_dobs.keys()), "status": "insufficient_data"}
        )

    dob_values = list(valid_dobs.values())
    first_dob = dob_values[0]

    # Check if all DOB values are identical
    mismatch = False
    for src, dob in valid_dobs.items():
        if dob != first_dob:
            mismatch = True
            break

    if mismatch:
        details_msg = ", ".join([f"{src}: {dob}" for src, dob in valid_dobs.items()])
        return ValidationCheck(
            rule="dob_match",
            category="validation",
            passed=False,
            severity="HIGH",
            message=f"DOB mismatch found between documents: {details_msg}",
            details={"dobs": valid_dobs}
        )

    return ValidationCheck(
        rule="dob_match",
        category="validation",
        passed=True,
        severity="INFO",
        message=f"DOBs are consistent across all documents ({first_dob}).",
        details={"dobs": valid_dobs}
    )


def compare_addresses(addresses_by_source: Dict[str, Optional[str]]) -> ValidationCheck:
    """Compare addresses using Jaccard token similarity."""
    valid_addresses = {src: val for src, val in addresses_by_source.items() if val and val.strip()}

    if len(valid_addresses) <= 1:
        return ValidationCheck(
            rule="address_match",
            category="validation",
            passed=True,
            severity="INFO",
            message="Address matching skipped: insufficient data (0 or 1 source available).",
            details={"sources": list(valid_addresses.keys()), "status": "insufficient_data"}
        )

    def tokenize_address(addr_str: str) -> set[str]:
        cleaned = re.sub(r"[^\w\s]", "", addr_str.lower()).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        # Filter out common filler words
        fillers = {"street", "road", "st", "rd", "ave", "lane", "ln", "near", "opposite", "opp"}
        words = set(cleaned.split())
        return words - fillers

    sources = list(valid_addresses.keys())
    mismatches = []

    for i in range(len(sources)):
        for j in range(i + 1, len(sources)):
            src1, src2 = sources[i], sources[j]
            w1 = tokenize_address(valid_addresses[src1])
            w2 = tokenize_address(valid_addresses[src2])

            if not w1 or not w2:
                mismatches.append(f"{src1} vs {src2} (empty address)")
                continue

            intersection = w1.intersection(w2)
            union = w1.union(w2)
            jaccard = len(intersection) / len(union) if union else 0.0

            # Reasonable threshold for address matching is 0.35 because of varied address formats
            if jaccard < 0.35:
                mismatches.append(f"{src1} vs {src2} (similarity: {jaccard:.2f})")

    if mismatches:
        return ValidationCheck(
            rule="address_match",
            category="validation",
            passed=False,
            severity="MEDIUM",
            message=f"Address mismatch or low similarity detected: {'; '.join(mismatches)}",
            details={"addresses": valid_addresses, "mismatches": mismatches}
        )

    return ValidationCheck(
        rule="address_match",
        category="validation",
        passed=True,
        severity="INFO",
        message="Addresses are consistent across all documents.",
        details={"addresses": valid_addresses}
    )


def compare_salary(
    payslip_net: Optional[str],
    payslip_gross: Optional[str],
    bank_credits: Optional[str],
    itr_annual: Optional[str]
) -> ValidationCheck:
    """
    Cross-checks salary credit from Bank Statement against Payslip net salary (10% tolerance),
    and Annual income from ITR against Monthly salary * 12 (20% tolerance).
    """
    net_val = parse_float(payslip_net)
    gross_val = parse_float(payslip_gross)
    bank_val = parse_float(bank_credits)
    itr_val = parse_float(itr_annual)

    details: Dict[str, Any] = {
        "payslip_net": net_val,
        "payslip_gross": gross_val,
        "bank_credits": bank_val,
        "itr_annual": itr_val
    }

    checks_run = []
    failures = []

    # 1. Compare Payslip Net against Bank Credits (10% tolerance)
    if net_val is not None and bank_val is not None:
        checks_run.append("payslip_net_vs_bank")
        diff_pct = abs(net_val - bank_val) / max(net_val, bank_val) if max(net_val, bank_val) > 0 else 0
        if diff_pct > 0.10:
            failures.append(f"Payslip Net (INR {net_val:.2f}) differs from Bank credit (INR {bank_val:.2f}) by {diff_pct*100:.1f}% (exceeds 10% tolerance)")
    # Fallback to Gross if net is not available
    elif gross_val is not None and bank_val is not None:
        checks_run.append("payslip_gross_vs_bank")
        # Gross salary should be larger than bank credit (which is net), so we check if credit is significantly larger than gross
        if bank_val > gross_val * 1.10:
            failures.append(f"Bank credit (INR {bank_val:.2f}) is significantly higher than Payslip Gross (INR {gross_val:.2f})")

    # 2. Compare ITR Annual against Monthly * 12 (20% tolerance)
    monthly_ref = net_val if net_val is not None else gross_val
    if monthly_ref is not None and itr_val is not None:
        checks_run.append("monthly_vs_itr_annual")
        calculated_annual = monthly_ref * 12
        diff_pct = abs(calculated_annual - itr_val) / max(calculated_annual, itr_val) if max(calculated_annual, itr_val) > 0 else 0
        if diff_pct > 0.20:
            failures.append(f"Estimated annual income from monthly (INR {calculated_annual:.2f}) differs from ITR annual income (INR {itr_val:.2f}) by {diff_pct*100:.1f}% (exceeds 20% tolerance)")

    details["checks_run"] = checks_run

    if not checks_run:
        return ValidationCheck(
            rule="salary_cross_check",
            category="validation",
            passed=True,
            severity="INFO",
            message="Salary cross-check skipped: insufficient data from payslip, bank statement, or ITR.",
            details={"status": "insufficient_data", **details}
        )

    if failures:
        return ValidationCheck(
            rule="salary_cross_check",
            category="validation",
            passed=False,
            severity="HIGH",
            message=f"Salary cross-check failed: {'; '.join(failures)}",
            details={"failures": failures, **details}
        )

    return ValidationCheck(
        rule="salary_cross_check",
        category="validation",
        passed=True,
        severity="INFO",
        message="Salary cross-check passed. Values are consistent within acceptable tolerances.",
        details=details
    )


def check_required_documents(present_docs: List[str], required_docs: List[str]) -> ValidationCheck:
    """Verifies that all required documents are present in the upload batch."""
    missing = [d for d in required_docs if d not in present_docs]

    if missing:
        return ValidationCheck(
            rule="required_documents",
            category="validation",
            passed=False,
            severity="HIGH",
            message=f"Required documents are missing: {', '.join(missing)}.",
            details={"present": present_docs, "required": required_docs, "missing": missing}
        )

    return ValidationCheck(
        rule="required_documents",
        category="validation",
        passed=True,
        severity="INFO",
        message="All required documents are present.",
        details={"present": present_docs, "required": required_docs}
    )


def check_expiry(expiry_dates_by_doc: Dict[str, Optional[str]]) -> ValidationCheck:
    """Check if any document has an expiry date in the past."""
    valid_exp_dates = {src: val for src, val in expiry_dates_by_doc.items() if val}

    if not valid_exp_dates:
        return ValidationCheck(
            rule="expiry_check",
            category="validation",
            passed=True,
            severity="INFO",
            message="No expiry dates found or applicable on uploaded documents.",
            details={"status": "not_applicable"}
        )

    today = datetime.utcnow().date()
    expired_docs = []
    parse_errors = []

    for doc, date_str in valid_exp_dates.items():
        normalized = normalize_date_string(date_str)
        if not normalized:
            parse_errors.append(f"Could not parse expiry date '{date_str}' for {doc}")
            continue

        try:
            exp_date = datetime.strptime(normalized, "%Y-%m-%d").date()
            if exp_date < today:
                expired_docs.append(f"{doc} (expired on {normalized})")
        except ValueError:
            parse_errors.append(f"Invalid date format '{normalized}' for {doc}")

    details = {"expiry_dates": valid_exp_dates}
    if expired_docs:
        details["expired_docs"] = expired_docs
        return ValidationCheck(
            rule="expiry_check",
            category="validation",
            passed=False,
            severity="HIGH",
            message=f"Expired documents detected: {', '.join(expired_docs)}",
            details=details
        )

    if parse_errors:
        details["parse_errors"] = parse_errors
        # We don't fail validation just for parsing issues, but we warn
        return ValidationCheck(
            rule="expiry_check",
            category="validation",
            passed=True,
            severity="LOW",
            message="Expiry checks passed, but some dates could not be parsed.",
            details=details
        )

    return ValidationCheck(
        rule="expiry_check",
        category="validation",
        passed=True,
        severity="INFO",
        message="All document expiry dates are in the future.",
        details=details
    )


def detect_pan_conflict(pans_by_source: Dict[str, Optional[str]]) -> ValidationCheck:
    """Detect if different PAN values are found across different documents."""
    valid_pans = {src: val.strip().upper() for src, val in pans_by_source.items() if val and val.strip()}

    if len(valid_pans) <= 1:
        return ValidationCheck(
            rule="pan_conflict",
            category="validation",
            passed=True,
            severity="INFO",
            message="No conflicting PAN values found: insufficient sources (0 or 1 source available).",
            details={"sources": list(valid_pans.keys()), "status": "insufficient_data"}
        )

    pan_values = list(valid_pans.values())
    first_pan = pan_values[0]

    conflicting_pans = {}
    for src, pan in valid_pans.items():
        if pan != first_pan:
            conflicting_pans[src] = pan

    if conflicting_pans:
        conflicting_pans[list(valid_pans.keys())[0]] = first_pan
        details_msg = ", ".join([f"{src}: {pan}" for src, pan in conflicting_pans.items()])
        return ValidationCheck(
            rule="pan_conflict",
            category="validation",
            passed=False,
            severity="CRITICAL",
            message=f"Conflicting PAN card numbers extracted from documents: {details_msg}",
            details={"pans": valid_pans}
        )

    return ValidationCheck(
        rule="pan_conflict",
        category="validation",
        passed=True,
        severity="INFO",
        message=f"PAN numbers match and are consistent across all documents ({first_pan}).",
        details={"pans": valid_pans}
    )
