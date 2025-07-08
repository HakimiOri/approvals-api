from fastapi import APIRouter, HTTPException, Depends
import logging
from pydantic import ValidationError

from app.dal.approvals.infura_approvals_dal import InfuraDAL
from app.dal.token_price.coingecko_token_price_dal import CoingeckoTokenPriceDAL
from app.models.approvals.approvals_request import ApprovalsRequest
from app.models.approvals.approvals_response import ApprovalsResponse
from app.services.approvals_service import ApprovalsService
from app.services.approvals_service_base import ApprovalsServiceBase

router = APIRouter()
logger = logging.getLogger(__name__)


def get_approvals_service() -> ApprovalsServiceBase:
    dal: InfuraDAL = InfuraDAL.get_instance()
    token_price_dal = CoingeckoTokenPriceDAL.get_instance()
    return ApprovalsService.get_instance(dal, token_price_dal)


@router.post("/get_approvals", response_model=ApprovalsResponse)
async def get_approvals(request: ApprovalsRequest,
                        service: ApprovalsServiceBase = Depends(get_approvals_service)) -> ApprovalsResponse:
    try:
        logger.info(f"Received get_approvals request with {len(request.addresses)} addresses")
        response = await service.get_latest_approvals(request)
        logger.info(f"Returning approvals response with {len(response.approvalsByAddress)} approvals")
        return response

    except (ValueError, ValidationError) as e:
        logger.warning(f"Bad request in get_approvals: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_approvals: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
