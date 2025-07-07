from typing import Optional

from pydantic import BaseModel


class ApprovalLog(BaseModel):
    block_number: int
    transaction_hash: str
    spender: str
    amount: int
    token_address: str
    log_index: Optional[int] = None

class Approval(BaseModel):
    amount: str
    spender_address: str
    token_symbol: str
    price_usd: Optional[float] = None

    class Config:
        exclude_none = True
