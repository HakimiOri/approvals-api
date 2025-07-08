from typing import Optional

from pydantic import BaseModel

from app.models.approvals.approvals import Approval


class ApprovalsResponse(BaseModel):
    approvalsByAddress: dict[str, list[Approval]]
    errorsByAddress: Optional[dict[str, str]] = None

