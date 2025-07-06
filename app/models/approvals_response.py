from pydantic import BaseModel
from typing import List, Dict

class ApprovalsResponse(BaseModel):
    approvals: List[Dict]

