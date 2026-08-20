"""
Gemini prompt templates for the AI Extraction Agent (Member 3).
Centralises all prompts so they're easy to tune without touching business logic.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# System / role prompt (sent once per session)
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a highly accurate financial document data-extraction AI for an Indian \
loan-processing platform called LoanIQ.

Your job is to read OCR text extracted from loan application documents \
(payslips, bank statements, ITR, Aadhaar, PAN cards, loan application forms) \
and extract every relevant structured field.

Rules:
1. Return ONLY a valid JSON object matching the schema provided — no markdown, \
   no explanations, no extra keys.
2. For every field you cannot confidently determine, output null.
3. Monetary values should be returned as plain strings without currency symbols \
   (e.g. "82000" not "₹82,000").
4. Dates should be in ISO 8601 (YYYY-MM-DD) wherever possible.
5. PAN must match the regex [A-Z]{5}[0-9]{4}[A-Z]{1}. Return null if ambiguous.
6. IFSC must match [A-Z]{4}0[A-Z0-9]{6}. Return null if ambiguous.
7. Aadhaar: mask all but last 4 digits (e.g. "XXXX XXXX 3456").
8. If the document contains data spanning multiple months/years (bank statement), \
   summarise aggregate values where instructed.
9. Add a "confidence_score" (0.0–1.0) reflecting overall extraction quality.
10. Add "extraction_notes" for any caveats or ambiguities you noticed.
"""


# ─────────────────────────────────────────────────────────────────────────────
# JSON schema (injected into user prompt so Gemini knows the target shape)
# ─────────────────────────────────────────────────────────────────────────────

EXTRACTION_SCHEMA = """\
{
  "document_meta": {
    "document_type": "<payslip|bank_statement|itr|aadhaar|pan_card|loan_application|unknown>",
    "document_date": "<YYYY-MM-DD or null>",
    "issuing_entity": "<string or null>",
    "page_count": "<int or null>"
  },
  "personal": {
    "name":    "<string or null>",
    "dob":     "<YYYY-MM-DD or null>",
    "gender":  "<string or null>",
    "pan":     "<string or null>",
    "aadhaar": "<masked string or null>",
    "address": "<string or null>",
    "phone":   "<string or null>",
    "email":   "<string or null>"
  },
  "employment": {
    "employer":        "<string or null>",
    "designation":     "<string or null>",
    "employment_type": "<Salaried|Self-employed|Business|null>",
    "date_of_joining": "<YYYY-MM-DD or null>",
    "department":      "<string or null>",
    "employee_id":     "<string or null>",
    "office_address":  "<string or null>"
  },
  "income": {
    "gross_salary":        "<string or null>",
    "net_salary":          "<string or null>",
    "annual_income":       "<string or null>",
    "basic_salary":        "<string or null>",
    "hra":                 "<string or null>",
    "other_allowances":    "<string or null>",
    "pf_deduction":        "<string or null>",
    "tax_deducted":        "<string or null>",
    "itr_assessed_income": "<string or null>",
    "assessment_year":     "<string or null>"
  },
  "bank": {
    "bank_name":             "<string or null>",
    "branch":                "<string or null>",
    "account_number":        "<string or null>",
    "account_type":          "<Savings|Current|OD|null>",
    "ifsc":                  "<string or null>",
    "micr":                  "<string or null>",
    "opening_balance":       "<string or null>",
    "closing_balance":       "<string or null>",
    "avg_monthly_balance":   "<string or null>",
    "statement_period_from": "<YYYY-MM-DD or null>",
    "statement_period_to":   "<YYYY-MM-DD or null>"
  },
  "loan": {
    "loan_amount_requested": "<string or null>",
    "loan_purpose":          "<string or null>",
    "loan_tenure_months":    "<string or null>",
    "existing_emi":          "<string or null>",
    "existing_loans":        "<string or null>"
  },
  "raw_text_snippet":  "<first 500 chars of OCR text>",
  "confidence_score":  "<float 0.0–1.0>",
  "extraction_notes":  "<string or null>"
}
"""


# ─────────────────────────────────────────────────────────────────────────────
# User message template
# ─────────────────────────────────────────────────────────────────────────────

def build_extraction_prompt(ocr_text: str, filename: str = "", hint: str = "") -> str:
    """
    Build the user-turn prompt fed to Gemini for a single document.

    Args:
        ocr_text: Raw text output from the OCR service (Member 2).
        filename: Original filename (helps Gemini guess document type).
        hint:     Optional document-type hint from upstream.

    Returns:
        Formatted prompt string.
    """
    hint_section = f"\nDocument type hint from OCR layer: {hint}" if hint else ""
    filename_section = f"\nSource filename: {filename}" if filename else ""

    return f"""\
Extract all financial and personal fields from the following OCR text of an \
Indian loan-application document.{filename_section}{hint_section}

Return ONLY a valid JSON object that exactly matches this schema:
{EXTRACTION_SCHEMA}

--- BEGIN OCR TEXT ---
{ocr_text}
--- END OCR TEXT ---
"""


# ─────────────────────────────────────────────────────────────────────────────
# Merge prompt — combines fields from multiple documents of one application
# ─────────────────────────────────────────────────────────────────────────────

MERGE_SYSTEM_PROMPT = """\
You are a data-merging AI for a loan-processing platform.
You will receive multiple JSON extraction results (one per document in a single \
loan application). Merge them into ONE unified JSON object using the same schema.

Rules:
1. Prefer more specific/confident values over null or vague ones.
2. If two documents disagree on the same field, pick the value from the document \
   with higher confidence_score.
3. Return ONLY the merged JSON — no markdown, no commentary.
4. Set confidence_score to the average of all input confidence scores.
5. Combine extraction_notes from all documents (pipe-separated).
"""

def build_merge_prompt(extractions_json: str) -> str:
    """
    Build the merge prompt for combining multiple document extractions.

    Args:
        extractions_json: JSON array string of ExtractedFields dicts.

    Returns:
        Formatted prompt string.
    """
    return f"""\
Here are the extraction results for each document in this loan application:

{extractions_json}

Merge them into ONE unified JSON object matching the schema below:
{EXTRACTION_SCHEMA}
"""
