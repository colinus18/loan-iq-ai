@echo off
:: ──────────────────────────────────────────────────────
:: LoanIQ AI — Start Extraction Agent server (Member 3)
:: Activates venv and launches uvicorn
:: ──────────────────────────────────────────────────────

echo [LoanIQ] Activating virtual environment...
call venv\Scripts\activate.bat

echo [LoanIQ] Checking .env...
if not exist .env (
    echo [WARN] .env not found. Copying from .env.example...
    copy .env.example .env
    echo [WARN] Please edit .env and add your GEMINI_API_KEY, then restart.
    pause
    exit /b 1
)

echo [LoanIQ] Starting extraction agent on http://localhost:8000
echo [LoanIQ] Swagger docs: http://localhost:8000/docs
echo.
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
