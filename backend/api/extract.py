"""
FastAPI router — AI Extraction Agent endpoints (Member 3).

Endpoints:
    POST /extract          → Run Gemini extraction on OCR text(s)
    GET  /fields/{app_id}  → Retrieve stored extraction for an application
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse

from backend.agents.extraction import (
    GeminiExtractor,
    ExtractRequest,
    ExtractResponse,
    ExtractionStatus,
    FieldsResponse,
)
from backend.agents.extraction import store as extraction_store
from backend.agents.extraction.schemas import ErrorResponse

logger     = logging.getLogger("api.extract")
router     = APIRouter(tags=["Extraction — Member 3"])
extractor  = GeminiExtractor()   # Singleton — Gemini model is lazy-loaded


# ─────────────────────────────────────────────────────────────────────────────
# POST /extract
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/extract",
    response_model=ExtractResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract structured fields from OCR text using Gemini AI",
    response_description="Extraction results for all documents in the application batch",
)
async def extract_fields(payload: ExtractRequest) -> ExtractResponse:
    """
    **Member 3 — AI Extraction Agent**

    Accepts a batch of OCR text blocks (one per document uploaded by the user)
    and calls Gemini to extract structured financial and personal data.

    ### Input (from Member 2 — OCR layer)
    ```json
    {
      "application_id": "APP-2024-001",
      "documents": [
        {"filename": "payslip.pdf",       "ocr_text": "..."},
        {"filename": "bank_statement.pdf", "ocr_text": "...", "hint": "bank_statement"}
      ]
    }
    ```

    ### Output (for Members 4 & 5 — Validation & Risk)
    Structured JSON with `personal`, `employment`, `income`, `bank`, `loan` fields.
    """
    app_id = payload.application_id
    logger.info("POST /extract — application_id=%s, docs=%d", app_id, len(payload.documents))

    if not payload.documents:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'documents' list cannot be empty.",
        )

    t0 = time.perf_counter()
    try:
        doc_results, merged = extractor.extract_batch(payload.documents)
    except EnvironmentError as exc:
        # GEMINI_API_KEY not set
        logger.error("Environment error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected extraction error for %s: %s", app_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Extraction failed due to an internal error. Check server logs.",
        )

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

    # Determine overall status
    statuses = {r.status for r in doc_results}
    if all(s in (ExtractionStatus.COMPLETED, ExtractionStatus.SUCCESS) for s in statuses):
        overall = ExtractionStatus.COMPLETED
    elif all(s == ExtractionStatus.FAILED for s in statuses):
        overall = ExtractionStatus.FAILED
    else:
        overall = ExtractionStatus.PARTIAL

    response = ExtractResponse(
        application_id=app_id,
        status=overall,
        documents=doc_results,
        merged_fields=merged,
        processing_time_ms=elapsed_ms,
    )

    # Persist in memory for GET /fields/{app_id}
    extraction_store.save(response)

    logger.info(
        "Extraction done — app=%s status=%s docs=%d merged=%s time=%.1fms",
        app_id, overall, len(doc_results),
        "yes" if merged else "no", elapsed_ms,
    )
    return response


# ─────────────────────────────────────────────────────────────────────────────
# GET /fields/{application_id}
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/fields/{application_id}",
    response_model=FieldsResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve extracted fields for an application",
    response_description="Previously extracted and merged fields for the application",
)
async def get_fields(application_id: str) -> FieldsResponse:
    """
    **Member 3 — AI Extraction Agent**

    Returns the stored extraction result for a given `application_id`.
    This endpoint is consumed by **Member 4 (Validation)** and **Member 5 (Risk)**.

    Returns `404` if no extraction has been run for this ID yet.
    """
    logger.info("GET /fields/%s", application_id)

    stored = extraction_store.get(application_id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No extraction found for application_id='{application_id}'. "
                   f"Run POST /extract first.",
        )

    return FieldsResponse(
        application_id=application_id,
        status=stored.status,
        fields=stored.merged_fields,
        documents=stored.documents,
        created_at=stored.created_at,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /fields/{application_id}/flat
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/fields/{application_id}/flat",
    status_code=status.HTTP_200_OK,
    summary="Get flat key-value dict of extracted fields",
    response_description="Flat dict of all non-null extracted fields",
)
async def get_fields_flat(application_id: str) -> Dict[str, Any]:
    """
    Returns a flat `{field: value}` dictionary of all extracted fields —
    convenient for downstream agents that don't want to navigate nested objects.
    """
    stored = extraction_store.get(application_id)
    if not stored or not stored.merged_fields:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No extraction found for application_id='{application_id}'.",
        )

    flat = stored.merged_fields.to_flat_dict()
    # Filter out nulls for cleanliness
    return {k: v for k, v in flat.items() if v is not None}


# ─────────────────────────────────────────────────────────────────────────────
# GET /extract/health
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check for the extraction service",
    tags=["Health"],
)
async def health() -> Dict[str, Any]:
    """Returns service health and the number of cached applications."""
    return {
        "service":     "extraction-agent",
        "member":      3,
        "status":      "ok",
        "cached_apps": len(extraction_store.all_ids()),
    }
