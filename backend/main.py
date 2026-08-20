"""
LoanIQ AI — FastAPI application entry point.
Member 3 owns the /extract routes.
Other members' routes are stubbed/included as they build them.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Member 3 router (extraction)
from backend.api.extract import router as extract_router

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


# ── App lifecycle ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 LoanIQ AI backend starting up…")
    yield
    logger.info("🛑 LoanIQ AI backend shutting down.")


# ── FastAPI instance ──────────────────────────────────────────────────────────
app = FastAPI(
    title="LoanIQ AI — Backend API",
    description=(
        "AI-powered loan application processing platform.\n\n"
        "**Member 3** — Extraction Agent (`/extract`): "
        "Converts OCR text → structured fields using Gemini AI."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Member 4 router (validation)
from backend.api.validate import router as validate_router
from backend.api.risk import router as risk_router

# Routers
app.include_router(extract_router)
app.include_router(validate_router)
app.include_router(risk_router)

# Other members' routers will be included here as they build them:
# from backend.api.upload   import router as upload_router
# from backend.api.risk     import router as risk_router
# from backend.api.summary  import router as summary_router
# app.include_router(upload_router)
# app.include_router(risk_router)
# app.include_router(summary_router)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "project":  "LoanIQ AI",
        "version":  "0.1.0",
        "docs":     "/docs",
        "member_3": "POST /extract  |  GET /fields/{application_id}",
    }
