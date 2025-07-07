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
    amount: int
    spender_address: str
    token_symbol: str