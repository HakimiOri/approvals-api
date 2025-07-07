from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ApprovalLog:
    block_number: int
    transaction_hash: str
    spender: str
    amount: int
    token_address: str
    log_index: Optional[int] = None
