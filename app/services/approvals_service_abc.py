from abc import ABC, abstractmethod

class ApprovalsServiceABC(ABC):
    @abstractmethod
    def get_latest_approvals(self, owner_address: str):
        pass
