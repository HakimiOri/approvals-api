from fastapi import APIRouter, HTTPException
from app.models import ApprovalsRequest, ApprovalsResponse
from app.services.approvals_service import get_approvals_for_addresses

router = APIRouter()

@router.post("/get_approvals", response_model=ApprovalsResponse)
def get_approvals(request: ApprovalsRequest):
    try:
        approvals = get_approvals_for_addresses(request.addresses)
        return ApprovalsResponse(approvals=approvals)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
