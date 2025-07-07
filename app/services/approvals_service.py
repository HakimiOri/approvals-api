import asyncio

from app.services.approvals_service_base import ApprovalsServiceBase
from app.utils.config_loader import Config
from app.utils.log_processor import process_approval_logs
from app.dal.approvals.approvals_dal import ApprovalsDAL
from app.models.approvals.approvals import Approval, ApprovalLog
from app.models.approvals.approvals_request import ApprovalsRequest
from app.models.approvals.approvals_response import ApprovalsResponse
from app.dal.token_price.coingecko_token_price_dal import CoingeckoTokenPriceDAL


class ApprovalsService(ApprovalsServiceBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, dal: ApprovalsDAL, config: Config, token_price_dal: CoingeckoTokenPriceDAL):
        if getattr(self, '_initialized', False):
            return
        self.dal = dal
        self._config = config
        self.token_price_dal = token_price_dal
        self._initialized = True

    @classmethod
    def get_instance(cls, dal: ApprovalsDAL, config: Config, token_price_dal=None):
        return cls(dal, config, token_price_dal)

    @staticmethod
    def _is_latest_approval(new_log: ApprovalLog, current_log: ApprovalLog) -> bool:
        return (new_log.block_number, new_log.log_index or 0) > (current_log.block_number, current_log.log_index or 0)

    async def _fetch_for_address(self, owner_address: str, approvals_by_address: dict, errors_by_address: dict,
                                 semaphore: asyncio.Semaphore, include_prices: bool = False):
        config = self._config
        last_exception = None
        for attempt in range(config.approvals_api_retries):
            try:
                async with semaphore:
                    approval_logs: list[ApprovalLog] = await self.dal.fetch_approval_logs(owner_address)
                    approvals_by_address[owner_address] = await process_approval_logs(
                        approval_logs,
                        self.dal.get_token_symbol,
                        get_token_price_usd=self.token_price_dal.get_token_price_usd,
                        include_prices=include_prices
                    )
                return
            except Exception as e:
                last_exception = e
                if attempt < config.approvals_api_retries - 1:
                    await asyncio.sleep(config.approvals_api_retry_delay)

        approvals_by_address[owner_address] = []
        errors_by_address[owner_address] = str(last_exception)

    async def get_latest_approvals(self, request: ApprovalsRequest) -> ApprovalsResponse:
        approvals_by_address: dict[str, list[Approval]] = {}
        errors_by_address: dict[str, str] = {}
        semaphore = asyncio.Semaphore(self._config.approvals_api_concurrency_limit)
        include_prices = bool(getattr(request, 'include_prices', False))
        await asyncio.gather(
            *(self._fetch_for_address(addr, approvals_by_address, errors_by_address, semaphore, include_prices=include_prices) for addr in
              request.addresses))
        return ApprovalsResponse(approvalsByAddress=approvals_by_address, errorsByAddress=errors_by_address)
