"""
In-memory store for validation results.
Keyed by application_id — persists for the lifetime of the process.
Member 4 only. No shared DB dependency.
"""

from __future__ import annotations

from typing import Dict, Optional
from backend.agents.validation.schemas import ValidationResult

# Simple in-memory registry for validation results
_store: Dict[str, ValidationResult] = {}


def save(result: ValidationResult) -> None:
    """Persist a ValidationResult in memory."""
    _store[result.application_id] = result


def get(application_id: str) -> Optional[ValidationResult]:
    """Retrieve a ValidationResult by application ID."""
    return _store.get(application_id)


def exists(application_id: str) -> bool:
    """Check if validation has been run for an application ID."""
    return application_id in _store


def all_ids() -> list[str]:
    """Get all cached application IDs."""
    return list(_store.keys())
