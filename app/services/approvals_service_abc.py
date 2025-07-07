from abc import ABC, abstractmethod

from app.models import ApprovalsResponse, ApprovalsRequest


class ApprovalsServiceABC(ABC):
    @abstractmethod
    async def get_latest_approvals(self, request: ApprovalsRequest) -> ApprovalsResponse:
        pass
