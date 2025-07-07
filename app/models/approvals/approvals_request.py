from pydantic import BaseModel
from typing import Optional

class ApprovalsRequest(BaseModel):
    addresses: list[str]
    include_prices: Optional[bool] = False
