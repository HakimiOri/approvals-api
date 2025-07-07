from pydantic import BaseModel

from app.models.approvals import Approval


class ApprovalsResponse(BaseModel):
    approvalsByAddress: dict[str, list[Approval]]
