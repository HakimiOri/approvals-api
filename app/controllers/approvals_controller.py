from fastapi import APIRouter, HTTPException, Depends, Request

from app.utils.config_loader import config
from app.dal.infura_approvals_dal import InfuraDAL
from app.models.approvals_request import ApprovalsRequest
from app.models.approvals_response import ApprovalsResponse
from app.services.approvals_service import ApprovalsService
from app.services.approvals_service_abc import ApprovalsServiceABC

router = APIRouter()


def get_approvals_service() -> ApprovalsServiceABC:
    dal: InfuraDAL = InfuraDAL.get_instance()
    return ApprovalsService.get_instance(dal, config)


@router.post("/get_approvals", response_model=ApprovalsResponse)
async def get_approvals(request: ApprovalsRequest,
                  service: ApprovalsServiceABC = Depends(get_approvals_service)) -> ApprovalsResponse:
    try:
        return await service.get_latest_approvals(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
