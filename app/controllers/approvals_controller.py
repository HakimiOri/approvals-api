from fastapi import APIRouter, HTTPException, Depends

from app.utils.config_loader import config
from app.dal.approvals.infura_approvals_dal import InfuraDAL
from app.dal.token_price.coingecko_token_price_dal import CoingeckoTokenPriceDAL
from app.models.approvals.approvals_request import ApprovalsRequest
from app.models.approvals.approvals_response import ApprovalsResponse
from app.services.approvals_service import ApprovalsService
from app.services.approvals_service_base import ApprovalsServiceBase

router = APIRouter()


def get_approvals_service() -> ApprovalsServiceBase:
    dal: InfuraDAL = InfuraDAL.get_instance()
    token_price_dal = CoingeckoTokenPriceDAL.get_instance()
    return ApprovalsService.get_instance(dal, config, token_price_dal)


@router.post("/get_approvals", response_model=ApprovalsResponse)
async def get_approvals(request: ApprovalsRequest,
                        service: ApprovalsServiceBase = Depends(get_approvals_service)) -> ApprovalsResponse:
    try:
        return await service.get_latest_approvals(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
