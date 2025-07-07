from abc import ABC, abstractmethod

from app.models import ApprovalsResponse, ApprovalsRequest


class ApprovalsServiceBase(ABC):
    @abstractmethod
    async def get_latest_approvals(self, request: ApprovalsRequest) -> ApprovalsResponse:
        pass
