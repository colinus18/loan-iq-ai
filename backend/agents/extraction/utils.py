"""
Utility helpers for the AI Extraction Agent (Member 3).
Handles JSON parsing, field sanitization, PAN/IFSC validation,
and merging of multiple extraction results.
"""

from __future__ import annotations

import json
import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("extraction.utils")

# ─────────────────────────────────────────────────────────────────────────────
# Regex patterns (Indian-specific)
# ─────────────────────────────────────────────────────────────────────────────

PAN_REGEX    = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]{1}")
IFSC_REGEX   = re.compile(r"[A-Z]{4}0[A-Z0-9]{6}")
AADHAAR_REGEX = re.compile(r"\d{4}\s?\d{4}\s?\d{4}")
PHONE_REGEX  = re.compile(r"(\+91[\-\s]?)?[6-9]\d{9}")
EMAIL_REGEX  = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
DATE_PATTERNS = [
    re.compile(r"\b(\d{2})[\/\-\.](\d{2})[\/\-\.](\d{4})\b"),  # DD/MM/YYYY
    re.compile(r"\b(\d{4})[\/\-\.](\d{2})[\/\-\.](\d{2})\b"),  # YYYY-MM-DD
]


# ─────────────────────────────────────────────────────────────────────────────
# JSON extraction from Gemini response
# ─────────────────────────────────────────────────────────────────────────────

def extract_json_from_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON from Gemini's raw text response.
    Handles cases where the model wraps output in markdown code blocks.

    Args:
        raw_text: Raw string response from Gemini API.

    Returns:
        Parsed dict or None on failure.
    """
    if not raw_text:
        return None

    # Strip markdown code fences if present
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        # Remove ```json ... ``` wrapping
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    # Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: find first { ... } block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON even after regex extraction.")

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Field sanitizers
# ─────────────────────────────────────────────────────────────────────────────

def sanitize_pan(value: Optional[str]) -> Optional[str]:
    """Validate and uppercase a PAN number. Returns None if invalid."""
    if not value:
        return None
    value = value.upper().replace(" ", "")
    return value if PAN_REGEX.fullmatch(value) else None


def sanitize_ifsc(value: Optional[str]) -> Optional[str]:
    """Validate and uppercase an IFSC code. Returns None if invalid."""
    if not value:
        return None
    value = value.upper().replace(" ", "")
    return value if IFSC_REGEX.fullmatch(value) else None


def mask_aadhaar(value: Optional[str]) -> Optional[str]:
    """Mask Aadhaar to show only last 4 digits."""
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if len(digits) != 12:
        return value  # Return as-is if not 12 digits
    return f"XXXX XXXX {digits[-4:]}"


def sanitize_amount(value: Optional[str]) -> Optional[str]:
    """
    Strip currency symbols and commas from monetary strings.
    e.g. "₹1,20,000.00" → "120000.00"
    """
    if not value:
        return None
    cleaned = re.sub(r"[₹$,\s]", "", str(value))
    # Remove trailing .00 if present for cleanliness
    cleaned = re.sub(r"\.0+$", "", cleaned)
    return cleaned if cleaned else None


def normalize_date(value: Optional[str]) -> Optional[str]:
    """
    Attempt to normalize common date formats to YYYY-MM-DD.
    Returns original string if normalization fails.
    """
    if not value:
        return None
    value = value.strip()

    # DD/MM/YYYY → YYYY-MM-DD
    m = re.fullmatch(r"(\d{2})[\/\-\.](\d{2})[\/\-\.](\d{4})", value)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"

    # Already YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value)
    if m:
        return value

    return value  # Return original if no known pattern


def sanitize_phone(value: Optional[str]) -> Optional[str]:
    """Normalize phone to 10-digit format."""
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    return digits if len(digits) == 10 else None


# ─────────────────────────────────────────────────────────────────────────────
# Deep sanitize: walk parsed dict and clean all fields
# ─────────────────────────────────────────────────────────────────────────────

_SECTION_SANITIZERS: Dict[str, Dict[str, Any]] = {
    "personal": {
        "pan":     sanitize_pan,
        "aadhaar": mask_aadhaar,
        "dob":     normalize_date,
        "phone":   sanitize_phone,
    },
    "employment": {
        "date_of_joining": normalize_date,
    },
    "income": {
        "gross_salary":       sanitize_amount,
        "net_salary":         sanitize_amount,
        "annual_income":      sanitize_amount,
        "basic_salary":       sanitize_amount,
        "hra":                sanitize_amount,
        "other_allowances":   sanitize_amount,
        "pf_deduction":       sanitize_amount,
        "tax_deducted":       sanitize_amount,
        "itr_assessed_income": sanitize_amount,
    },
    "bank": {
        "ifsc":                  sanitize_ifsc,
        "opening_balance":       sanitize_amount,
        "closing_balance":       sanitize_amount,
        "avg_monthly_balance":   sanitize_amount,
        "statement_period_from": normalize_date,
        "statement_period_to":   normalize_date,
    },
    "loan": {
        "loan_amount_requested": sanitize_amount,
        "existing_emi":          sanitize_amount,
    },
    "document_meta": {
        "document_date": normalize_date,
    },
}


def deep_sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Walk the extraction dict and apply field-level sanitizers in place.
    Returns the mutated dict.
    """
    for section, field_map in _SECTION_SANITIZERS.items():
        section_data = data.get(section, {})
        if isinstance(section_data, dict):
            for field, sanitizer in field_map.items():
                if field in section_data:
                    section_data[field] = sanitizer(section_data[field])
    return data


# ─────────────────────────────────────────────────────────────────────────────
# Merge multiple extraction dicts (fallback in-process merge)
# ─────────────────────────────────────────────────────────────────────────────

def merge_extraction_dicts(
    extractions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Merge multiple extraction result dicts into one by preferring non-null
    values from the document with the highest confidence_score.

    This is the in-process fallback; the primary merge path uses Gemini.

    Args:
        extractions: List of dicts (each from ExtractedFields.model_dump()).

    Returns:
        Single merged dict.
    """
    if not extractions:
        return {}
    if len(extractions) == 1:
        return extractions[0]

    # Sort by confidence descending so we pick high-confidence values first
    sorted_exts = sorted(
        extractions,
        key=lambda x: x.get("confidence_score") or 0.0,
        reverse=True,
    )

    merged: Dict[str, Any] = {}

    for ext in sorted_exts:
        _deep_merge(merged, ext)

    # Recalculate confidence as average
    scores = [
        e.get("confidence_score")
        for e in extractions
        if e.get("confidence_score") is not None
    ]
    merged["confidence_score"] = round(sum(scores) / len(scores), 4) if scores else None

    # Combine notes
    notes = [
        e.get("extraction_notes")
        for e in extractions
        if e.get("extraction_notes")
    ]
    merged["extraction_notes"] = " | ".join(notes) if notes else None

    return merged


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    """
    Recursively merge 'override' into 'base'.
    Only fills keys that are None or missing in base (prefer existing non-null).
    """
    for key, value in override.items():
        if key not in base or base[key] is None:
            if isinstance(value, dict):
                base[key] = {}
                _deep_merge(base[key], value)
            else:
                base[key] = value
        elif isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
