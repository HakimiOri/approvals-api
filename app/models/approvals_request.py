from pydantic import BaseModel
from typing import List, Dict

class ApprovalsRequest(BaseModel):
    addresses: List[str]

