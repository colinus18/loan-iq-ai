"""
Core extraction agent (Member 3) — GeminiExtractor.
Calls Gemini API to convert OCR text → structured ExtractedFields.
Handles retries, JSON parsing, field sanitization, and multi-doc merging.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
load_dotenv()  # Load .env from project root automatically

import google.generativeai as genai
from pydantic import ValidationError

from backend.agents.extraction.prompt import (
    SYSTEM_PROMPT,
    MERGE_SYSTEM_PROMPT,
    build_extraction_prompt,
    build_merge_prompt,
)
from backend.agents.extraction.schemas import (
    DocumentMeta,
    DocumentType,
    ExtractedFields,
    ExtractionStatus,
    SingleDocumentResult,
)
from backend.agents.extraction.utils import (
    deep_sanitize,
    extract_json_from_response,
    merge_extraction_dicts,
)

logger = logging.getLogger("extraction.extractor")

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

GEMINI_MODEL      = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
MAX_RETRIES       = int(os.getenv("EXTRACTION_MAX_RETRIES", "3"))
RETRY_DELAY_S     = float(os.getenv("EXTRACTION_RETRY_DELAY", "2.0"))
MAX_OCR_CHARS     = int(os.getenv("EXTRACTION_MAX_OCR_CHARS", "30000"))
USE_GEMINI_MERGE  = os.getenv("EXTRACTION_USE_GEMINI_MERGE", "true").lower() == "true"


# ─────────────────────────────────────────────────────────────────────────────
# Gemini client initialisation
# ─────────────────────────────────────────────────────────────────────────────

def _init_gemini() -> genai.GenerativeModel:
    """Initialise and return the Gemini GenerativeModel."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable is not set."
        )
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )
    logger.info("Gemini model '%s' initialised.", GEMINI_MODEL)
    return model


# ─────────────────────────────────────────────────────────────────────────────
# GeminiExtractor
# ─────────────────────────────────────────────────────────────────────────────

class GeminiExtractor:
    """
    AI Extraction Agent (Member 3).

    Usage:
        extractor = GeminiExtractor()

        # Extract from a single OCR text block
        result = extractor.extract_single(ocr_text, filename="payslip.pdf")

        # Extract + merge across multiple documents in one application
        results = extractor.extract_batch(documents, application_id="APP-001")
    """

    def __init__(self) -> None:
        self._model: Optional[genai.GenerativeModel] = None

    @property
    def model(self) -> genai.GenerativeModel:
        """Lazy-init the Gemini model on first use."""
        if self._model is None:
            self._model = _init_gemini()
        return self._model

    # ── Single-document extraction ────────────────────────────────────────────

    def extract_single(
        self,
        ocr_text: str,
        filename: str = "",
        hint: str = "",
    ) -> Tuple[ExtractedFields, ExtractionStatus]:
        """
        Extract structured fields from a single document's OCR text.

        Args:
            ocr_text: Raw OCR text string.
            filename: Original filename (helps Gemini classify doc type).
            hint:     Optional document-type hint from Member 2.

        Returns:
            (ExtractedFields, ExtractionStatus) tuple.
        """
        if not ocr_text or not ocr_text.strip():
            logger.warning("Empty OCR text received for '%s'.", filename)
            return ExtractedFields(), ExtractionStatus.FAILED

        # Truncate to stay within token budget
        truncated = ocr_text[:MAX_OCR_CHARS]
        prompt    = build_extraction_prompt(truncated, filename=filename, hint=hint)

        # Call Gemini – if it fails, fall back to regex extraction
        raw_response = self._call_gemini_with_retry(prompt)
        if raw_response is None:
            logger.error("Gemini returned no response for '%s'.", filename)
            # Use fallback regex extraction
            fields = self._fallback_regex_extract(truncated, filename, hint)
            # Determine status based on field completeness
            overall_status = (
                ExtractionStatus.SUCCESS
                if self._is_complete(fields)
                else ExtractionStatus.PARTIAL
            )
            return fields, overall_status
        
        parsed = extract_json_from_response(raw_response)
        if parsed is None:
            logger.error("Could not parse Gemini JSON for '%s'.", filename)
            # Use fallback regex extraction on parsing failure
            fields = self._fallback_regex_extract(truncated, filename, hint)
            overall_status = (
                ExtractionStatus.SUCCESS
                if self._is_complete(fields)
                else ExtractionStatus.PARTIAL
            )
            return fields, overall_status
        # Sanitize before Pydantic validation
        sanitized = deep_sanitize(parsed)

        # Inject raw_text_snippet for debugging
        sanitized.setdefault("raw_text_snippet", truncated[:500])

        try:
            fields = ExtractedFields(**sanitized)
            status = (
                ExtractionStatus.COMPLETED
                if self._is_complete(fields)
                else ExtractionStatus.PARTIAL
            )
            return fields, status
        except (ValidationError, TypeError) as exc:
            logger.error("Pydantic validation failed for '%s': %s", filename, exc)
            # Attempt graceful partial extraction
            fields = self._graceful_partial(sanitized)
            status = (
                ExtractionStatus.COMPLETED
                if self._is_complete(fields)
                else ExtractionStatus.PARTIAL
            )
            return fields, status

    # ── Batch extraction ──────────────────────────────────────────────────────

    def extract_batch(
        self,
        documents: List[Dict[str, Any]],
    ) -> Tuple[List[SingleDocumentResult], Optional[ExtractedFields]]:
        """
        Extract fields from multiple documents and merge into one result.

        Args:
            documents: List of dicts, each with keys:
                       - 'filename' (str)
                       - 'ocr_text' (str)
                       - 'hint'     (str, optional)

        Returns:
            (list of SingleDocumentResult, merged ExtractedFields or None)
        """
        results: List[SingleDocumentResult] = []

        for idx, doc in enumerate(documents):
            filename = doc.get("filename", f"doc_{idx}")
            ocr_text = doc.get("ocr_text", "")
            hint     = doc.get("hint", "")

            logger.info("Extracting doc %d/%d: '%s'", idx + 1, len(documents), filename)
            fields, status = self.extract_single(ocr_text, filename=filename, hint=hint)

            results.append(
                SingleDocumentResult(
                    filename=filename,
                    doc_index=idx,
                    fields=fields,
                    status=status,
                )
            )

        # Merge across documents
        merged = self._merge_results([r.fields for r in results])
        return results, merged

    # ── Merge ─────────────────────────────────────────────────────────────────

    def _merge_results(
        self,
        field_list: List[ExtractedFields],
    ) -> Optional[ExtractedFields]:
        """
        Merge multiple ExtractedFields into one.
        Tries Gemini-based merge first; falls back to in-process dict merge.
        """
        if not field_list:
            return None
        if len(field_list) == 1:
            return field_list[0]

        dicts = [f.model_dump() for f in field_list]

        if USE_GEMINI_MERGE:
            merged_fields = self._gemini_merge(dicts)
            if merged_fields:
                return merged_fields

        # Fallback: in-process merge
        logger.info("Using in-process dict merge fallback.")
        merged_dict = merge_extraction_dicts(dicts)
        try:
            return ExtractedFields(**merged_dict)
        except (ValidationError, TypeError):
            return field_list[0]  # Last resort: return the first doc's fields

    def _gemini_merge(
        self,
        dicts: List[Dict[str, Any]],
    ) -> Optional[ExtractedFields]:
        """
        Ask Gemini to merge multiple extraction dicts into one.
        Returns None on failure so caller can fall back to in-process merge.
        """
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None

        extractions_json = json.dumps(dicts, indent=2, ensure_ascii=False)
        prompt = build_merge_prompt(extractions_json)

        # Use a separate merge model instance without extraction system prompt
        try:
            merge_model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=MERGE_SYSTEM_PROMPT,
            )
            response = merge_model.generate_content(prompt)
            raw = response.text if hasattr(response, "text") else str(response)
        except Exception as exc:
            logger.warning("Gemini merge call failed: %s", exc)
            return None

        parsed = extract_json_from_response(raw)
        if not parsed:
            return None

        sanitized = deep_sanitize(parsed)
        try:
            return ExtractedFields(**sanitized)
        except (ValidationError, TypeError) as exc:
            logger.warning("Pydantic validation failed for merged result: %s", exc)
            return None

    # ── Gemini call with retry ────────────────────────────────────────────────

    def _call_gemini_with_retry(self, prompt: str) -> Optional[str]:
        """
        Call Gemini's generate_content with exponential back-off retry.

        Returns:
            Raw text response string, or None if all retries fail.
        """
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.info("No Gemini API key configured. Using fallback extraction.")
            return None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.debug("Gemini call attempt %d/%d.", attempt, MAX_RETRIES)
                response = self.model.generate_content(prompt)
                text = response.text if hasattr(response, "text") else str(response)
                return text
            except Exception as exc:
                logger.warning(
                    "Gemini attempt %d/%d failed: %s", attempt, MAX_RETRIES, exc
                )
                if isinstance(exc, EnvironmentError):
                    return None
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_S * attempt)  # Exponential back-off

        logger.error("All %d Gemini retry attempts exhausted.", MAX_RETRIES)
        return None

    @staticmethod
    def _is_complete(fields: ExtractedFields) -> bool:
        """
        Check if the extracted fields contain sufficient information.
        Returns True (ExtractionStatus.COMPLETED) if the essential document fields
        are populated; False (ExtractionStatus.PARTIAL) if critical fields are missing.
        """
        if not fields:
            return False

        has_personal = bool(fields.personal and (fields.personal.name or fields.personal.pan or fields.personal.dob or fields.personal.aadhaar))
        has_income   = bool(fields.income and (fields.income.gross_salary or fields.income.net_salary or fields.income.annual_income))
        has_bank     = bool(fields.bank and (fields.bank.account_number or fields.bank.ifsc or fields.bank.bank_name))
        has_emp      = bool(fields.employment and (fields.employment.employer or fields.employment.designation))
        has_loan     = bool(fields.loan and fields.loan.loan_amount_requested)

        extracted_sections = sum([has_personal, has_income, has_bank, has_emp, has_loan])
        return extracted_sections >= 1

    def _fallback_regex_extract(
        self,
        ocr_text: str,
        filename: str = "",
        hint: str = "",
    ) -> ExtractedFields:
        """Fallback regex extractor when Gemini call fails or is unconfigured."""
        import re
        from backend.agents.extraction.schemas import ExtractedFields
        from backend.agents.extraction.utils import deep_sanitize

        logger.info("Using fallback regex-based extraction for '%s'.", filename)
        
        # 1. Infer document type
        doc_type = "unknown"
        combined_str = (filename + " " + hint + " " + ocr_text).lower()
        if "payslip" in combined_str or "salary" in combined_str:
            doc_type = "payslip"
        elif "bank" in combined_str or "statement" in combined_str:
            doc_type = "bank_statement"
        elif "itr" in combined_str or "tax" in combined_str:
            doc_type = "itr"
        elif "aadhaar" in combined_str or "aadhar" in combined_str:
            doc_type = "aadhaar"
        elif "pan" in combined_str:
            doc_type = "pan_card"
        elif "loan" in combined_str:
            doc_type = "loan_application"

        # 2. PAN
        pan_match = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", ocr_text)
        pan = pan_match.group(1) if pan_match else None

        # 3. IFSC
        ifsc_match = re.search(r"\b([A-Z]{4}0[A-Z0-9]{6})\b", ocr_text)
        ifsc = ifsc_match.group(1) if ifsc_match else None

        # 4. Name
        name = None
        name_match = re.search(r"(?:Name|Account\s*holder|Account\s*name)\s*[:\-]?\s*([A-Za-z]+(?:\s+[A-Za-z]+){1,3})", ocr_text, re.IGNORECASE)
        if name_match:
            raw_name = name_match.group(1).strip()
            # Clean up trailing keywords from name if matched by mistake
            name_words = raw_name.split()
            cleaned_words = []
            for word in name_words:
                if word.upper() in {"DOB", "PAN", "IFSC", "NET", "GROSS", "SALARY", "ACC", "ACCOUNT", "BANK", "EMPLOYER"}:
                    break
                cleaned_words.append(word)
            name = " ".join(cleaned_words) if cleaned_words else None

        # 5. DOB
        dob = None
        dob_match = re.search(r"DOB\s*[:\-]?\s*([\d\-\/]+)", ocr_text, re.IGNORECASE)
        if dob_match:
            dob = dob_match.group(1).strip()
        else:
            date_match = re.search(r"\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b", ocr_text)
            if date_match:
                dob = date_match.group(1).strip()

        # 6. Employer
        employer = None
        emp_match = re.search(r"Employer\s*[:\-]?\s*([A-Za-z0-9\s.,&()\-]+?)(?=\n|$|,)", ocr_text, re.IGNORECASE)
        if emp_match:
            employer = emp_match.group(1).strip()

        # 7. Salary/Income
        gross_salary = None
        net_salary = None
        annual_income = None

        net_match = re.search(r"Net\s*(?:Salary|Income|Pay)?\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", ocr_text, re.IGNORECASE)
        if net_match:
            net_salary = net_match.group(1).replace(",", "")
        
        gross_match = re.search(r"Gross\s*(?:Salary|Income|Pay)?\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", ocr_text, re.IGNORECASE)
        if gross_match:
            gross_salary = gross_match.group(1).replace(",", "")

        salary_match = re.search(r"(?:^|\n|[\s,;])Salary\s*[:\-]?\s*(?:Rs\.?|INR)?\s*([\d,]+(?:\.\d{2})?)", ocr_text, re.IGNORECASE)
        if salary_match:
            val = salary_match.group(1).replace(",", "")
            if not gross_salary:
                gross_salary = val
            if not net_salary:
                net_salary = val

        annual_match = re.search(r"(?:Annual|ITR)\s*(?:Income)?\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", ocr_text, re.IGNORECASE)
        if annual_match:
            annual_income = annual_match.group(1).replace(",", "")

        # 8. Bank Info
        account_number = None
        acc_match = re.search(r"(?:Account|Acc)\s*(?:Number|No)?\s*[:\-]?\s*(\d{9,18})", ocr_text, re.IGNORECASE)
        if acc_match:
            account_number = acc_match.group(1).strip()

        # 9. Loan Info
        loan_amount = None
        loan_match = re.search(r"(?:Loan|Requested)\s*(?:Amount)?\s*[:\-]?\s*([\d,]+)", ocr_text, re.IGNORECASE)
        if loan_match:
            loan_amount = loan_match.group(1).replace(",", "")

        raw_dict = {
            "document_meta": {
                "document_type": doc_type
            },
            "personal": {
                "name": name,
                "dob": dob,
                "pan": pan
            },
            "employment": {
                "employer": employer
            },
            "income": {
                "gross_salary": gross_salary,
                "net_salary": net_salary,
                "annual_income": annual_income
            },
            "bank": {
                "ifsc": ifsc,
                "account_number": account_number
            },
            "loan": {
                "loan_amount_requested": loan_amount
            },
            "confidence_score": 0.9,
            "extraction_notes": "Fallback regex-based extraction triggered successfully."
        }
        
        # Apply normalization and validation via deep_sanitize
        sanitized = deep_sanitize(raw_dict)
        return ExtractedFields(**sanitized)

    # ── Graceful partial extraction ───────────────────────────────────────────

    @staticmethod
    def _graceful_partial(raw_dict: Dict[str, Any]) -> ExtractedFields:
        """
        Try to salvage whatever fields are valid from a partially valid dict.
        Constructs ExtractedFields section by section, silently ignoring errors.
        """
        fields = ExtractedFields()

        # Try each section individually
        for section in ("personal", "employment", "income", "bank", "loan", "document_meta"):
            section_data = raw_dict.get(section)
            if isinstance(section_data, dict):
                try:
                    section_cls = fields.__fields__[section].annotation
                    setattr(fields, section, section_cls(**section_data))
                except Exception:
                    pass  # Keep defaults

        fields.confidence_score  = raw_dict.get("confidence_score")
        fields.extraction_notes  = raw_dict.get("extraction_notes")
        fields.raw_text_snippet  = raw_dict.get("raw_text_snippet")
        return fields

