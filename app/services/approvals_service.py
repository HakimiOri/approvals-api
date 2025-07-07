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

    def __init__(self, dal: ApprovalsDAL):
        if getattr(self, '_initialized', False):
            return
        self.dal = dal
        self._initialized = True

    @classmethod
    def get_instance(cls, dal: ApprovalsDAL):
        return cls(dal)

    @staticmethod
    def is_latest_approval(new_log: ApprovalLog, current_log: ApprovalLog) -> bool:
        return (new_log.block_number, new_log.log_index or 0) > (current_log.block_number, current_log.log_index or 0)

    def get_latest_approvals(self, request: ApprovalsRequest) -> ApprovalsResponse:
        approvals_by_address: dict[str, list[Approval]] = {}

        for owner_address in request.addresses:
            approval_logs: list[ApprovalLog] = self.dal.fetch_approval_logs(owner_address)
            latest_approvals = {}

            for log in approval_logs:
                token = log.token_address.lower()
                spender = log.spender.lower()

                key = (token, spender)
                if key not in latest_approvals or self.is_latest_approval(log, latest_approvals[key]):
                    latest_approvals[key] = log

            approvals_by_address[owner_address] = [
                Approval(
                    amount=approval_log.amount,
                    spender_address=approval_log.spender,
                    token_symbol=getattr(approval_log, 'token_symbol', '')
                )
                for approval_log in latest_approvals.values()
            ]
        return ApprovalsResponse(approvalsByAddress=approvals_by_address)
