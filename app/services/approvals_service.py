import asyncio

from app.Utils.config_loader import Config
from app.dal.approvals_dal import ApprovalsDAL
from app.models.approvals import Approval, ApprovalLog
from app.models.approvals_request import ApprovalsRequest
from app.models.approvals_response import ApprovalsResponse
from .approvals_service_abc import ApprovalsServiceABC


class ApprovalsService(ApprovalsServiceABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, dal: ApprovalsDAL, config: Config):
        if getattr(self, '_initialized', False):
            return
        self.dal = dal
        self._config = config
        self._initialized = True

    @classmethod
    def get_instance(cls, dal: ApprovalsDAL, config: Config):
        return cls(dal, config)

    @staticmethod
    def _is_latest_approval(new_log: ApprovalLog, current_log: ApprovalLog) -> bool:
        return (new_log.block_number, new_log.log_index or 0) > (current_log.block_number, current_log.log_index or 0)

    async def _fetch_for_address(self, owner_address: str, approvals_by_address: dict, errors_by_address: dict,
                                 semaphore: asyncio.Semaphore):
        config = self._config
        for attempt in range(config.approvals_api_retries):
            try:
                async with semaphore:
                    approval_logs: list[ApprovalLog] = await self.dal.fetch_approval_logs(owner_address)
                    latest_approvals = {}
                    for log in approval_logs:
                        token = log.token_address.lower()
                        spender = log.spender.lower()
                        key = (token, spender)
                        if key not in latest_approvals or self._is_latest_approval(log, latest_approvals[key]):
                            latest_approvals[key] = log
                    approvals_by_address[owner_address] = [
                        Approval(
                            amount=approval_log.amount,
                            spender_address=approval_log.spender,
                            token_symbol=await self.dal.get_token_symbol(approval_log.token_address),
                        )
                        for approval_log in latest_approvals.values()
                    ]
                return
            except Exception as e:
                if attempt < config.approvals_api_retries - 1:
                    await asyncio.sleep(config.approvals_api_retry_delay)
                    errors_by_address[owner_address] = str(e)

    async def get_latest_approvals(self, request: ApprovalsRequest) -> ApprovalsResponse:
        approvals_by_address: dict[str, list[Approval]] = {}
        errors_by_address: dict[str, str] = {}
        semaphore = asyncio.Semaphore(self._config.approvals_api_concurrency_limit)
        await asyncio.gather(
            *(self._fetch_for_address(addr, approvals_by_address, errors_by_address, semaphore) for addr in
              request.addresses))
        return ApprovalsResponse(approvalsByAddress=approvals_by_address, errorsByAddress=errors_by_address)
