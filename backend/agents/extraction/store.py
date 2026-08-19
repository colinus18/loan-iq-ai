"""
In-memory store for extraction results.
Keyed by application_id — persists for the lifetime of the process.
Member 3 only. No shared DB dependency.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from backend.agents.extraction.schemas import ExtractResponse

# Simple in-memory registry
_store: Dict[str, ExtractResponse] = {}


def save(response: ExtractResponse) -> None:
    """Persist an ExtractResponse in memory."""
    _store[response.application_id] = response


def get(application_id: str) -> Optional[ExtractResponse]:
    """Retrieve an ExtractResponse by application ID."""
    return _store.get(application_id)


def exists(application_id: str) -> bool:
    return application_id in _store


def all_ids() -> list[str]:
    return list(_store.keys())
