
from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.risk.integration_service import process_application


router = APIRouter(
    prefix="/risk-assessment",
    tags=["Risk & Summary — Member 5"],
)


class RiskAssessmentRequest(BaseModel):
    application_id: str


@router.post("")
def risk_assessment(request: RiskAssessmentRequest):
    return process_application(request.application_id)