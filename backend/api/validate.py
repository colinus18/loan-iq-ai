"""
FastAPI router — Validation & Fraud Detection Agent endpoints (Member 4).

Endpoints:
    POST /validate                      → Run validation/fraud detection on extracted data
    GET  /validation/{application_id}  → Retrieve stored validation results for an application
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status

from backend.agents.extraction import store as extraction_store
from backend.agents.validation.schemas import ValidateRequest, ValidationResult
from backend.agents.validation.validator import ValidationEngine
from backend.agents.validation import store as validation_store

logger = logging.getLogger("api.validate")
router = APIRouter(tags=["Validation & Fraud — Member 4"])
engine = ValidationEngine()


@router.post(
    "/validate",
    response_model=ValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Validate extracted fields and detect fraud indicators",
    response_description="Validation checklist results and fraud summary",
)
async def validate_application(payload: ValidateRequest) -> ValidationResult:
    """
    **Member 4 — Validation & Fraud Detection Agent**

    Retrieves Member 3's extracted fields for the given `application_id`,
    executes deterministic validation rules, computes the fraud risk score,
    and returns a structured validation report.

    Calling this endpoint multiple times for the same application ID will
    recalculate and replace the existing result in-memory.
    """
    app_id = payload.application_id
    logger.info("POST /validate — application_id=%s", app_id)

    # Verify that Member 3 has extracted fields first
    if not extraction_store.exists(app_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No extracted fields found for application_id='{app_id}'. "
                   f"Please extract fields using POST /extract first.",
        )

    try:
        # Run validation engine
        result = engine.validate(app_id)
        return result
    except ValueError as exc:
        logger.error("Validation error for %s: %s", app_id, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected validation error for %s: %s", app_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Validation failed due to an internal error. Check server logs.",
        )


@router.get(
    "/validation/{application_id}",
    response_model=ValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Retrieve validation and fraud results for an application",
    response_description="Previously generated validation and fraud report",
)
async def get_validation(application_id: str) -> ValidationResult:
    """
    **Member 4 — Validation & Fraud Detection Agent**

    Returns the stored validation result for the given `application_id`.
    This endpoint is consumed by **Member 5 (Risk)** and **Member 1 (Frontend)**.

    Returns `404` if validation has not been run for this ID yet.
    """
    logger.info("GET /validation/%s", application_id)

    result = validation_store.get(application_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No validation results found for application_id='{application_id}'. "
                   f"Run POST /validate first.",
        )

    return result


@router.get(
    "/validation/health/check",
    status_code=status.HTTP_200_OK,
    summary="Health check for the validation service",
    tags=["Health"],
)
async def health() -> Dict[str, Any]:
    """Returns service health and the number of validated applications."""
    return {
        "service":     "validation-agent",
        "member":      4,
        "status":      "ok",
        "cached_apps": len(validation_store.all_ids()),
    }
