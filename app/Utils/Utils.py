from typing import Final

MAX_UINT256: Final[int] = 2 ** 256 - 1

def format_amount(amount: int) -> str:
    if amount >= MAX_UINT256:
        return "Unlimited"
    return f"{amount:,}"