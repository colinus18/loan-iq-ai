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

        raw_response = self._call_gemini_with_retry(prompt)
        if raw_response is None:
            logger.error("Gemini returned no response for '%s'.", filename)
            return ExtractedFields(), ExtractionStatus.FAILED

        parsed = extract_json_from_response(raw_response)
        if parsed is None:
            logger.error("Could not parse Gemini JSON for '%s'.", filename)
            return ExtractedFields(), ExtractionStatus.FAILED

        # Sanitize before Pydantic validation
        sanitized = deep_sanitize(parsed)

        # Inject raw_text_snippet for debugging
        sanitized.setdefault("raw_text_snippet", truncated[:500])

        try:
            fields = ExtractedFields(**sanitized)
            status = (
                ExtractionStatus.SUCCESS
                if fields.confidence_score and fields.confidence_score >= 0.5
                else ExtractionStatus.PARTIAL
            )
            return fields, status
        except (ValidationError, TypeError) as exc:
            logger.error("Pydantic validation failed for '%s': %s", filename, exc)
            # Attempt graceful partial extraction
            fields = self._graceful_partial(sanitized)
            return fields, ExtractionStatus.PARTIAL

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
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_S * attempt)  # Exponential back-off

        logger.error("All %d Gemini retry attempts exhausted.", MAX_RETRIES)
        return None

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
