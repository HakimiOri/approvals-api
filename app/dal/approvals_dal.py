from abc import ABC, abstractmethod

from app.models.approvals import ApprovalLog


class ApprovalsDAL(ABC):
    @abstractmethod
    async def get_token_symbol(self, token_address: str) -> str:
        pass

    @abstractmethod
    async def fetch_approval_logs(self, owner_address: str) -> list[ApprovalLog]:
        pass
