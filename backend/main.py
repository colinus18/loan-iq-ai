from fastapi import FastAPI

from api.upload import router as upload_router
from api.ocr import router as ocr_router


app = FastAPI(
    title="LoanIQ AI",
    description="AI-powered Loan Document Processing Platform",
    version="1.0.0",
)


app.include_router(upload_router)
app.include_router(ocr_router)


@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "LoanIQ AI"
    }