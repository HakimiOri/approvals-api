import asyncio
from typing import Dict, Tuple, List, Callable, Awaitable, Final, Optional

from app.models.approvals.approvals import Approval, ApprovalLog
from app.utils.config_loader import config

MAX_UINT256: Final[int] = 2 ** 256 - 1


def _format_amount(amount: int) -> str:
    if amount >= MAX_UINT256:
        return "Unlimited"
    return f"{amount:,}"


async def _process_log_with_semaphore(approval_log: ApprovalLog, get_token_symbol, get_token_price_usd, include_prices,
                                      semaphore) -> Approval:
    async with semaphore:
        price: Optional[float] = None
        if include_prices and get_token_price_usd is not None:
            price = await get_token_price_usd(approval_log.token_address)
        token_symbol = await get_token_symbol(approval_log.token_address)
        return Approval(
            amount=_format_amount(approval_log.amount),
            spender_address=approval_log.spender,
            token_symbol=token_symbol,
            price_usd=price
        )


async def process_approval_logs(
        approval_logs: List[ApprovalLog],
        get_token_symbol: Callable[[str], Awaitable[str]],
        get_token_price_usd: Optional[Callable[[str], Awaitable[Optional[float]]]] = None,
        include_prices: bool = False
) -> List[Approval]:
    latest_approvals: Dict[Tuple[str, str], ApprovalLog] = {}
    for log in approval_logs:
        token = log.token_address.lower()
        spender = log.spender.lower()
        key = (token, spender)
        if key not in latest_approvals or is_latest_approval(log, latest_approvals[key]):
            latest_approvals[key] = log
    semaphore = asyncio.Semaphore(config.log_processor_concurrency_limit)
    results = await asyncio.gather(*(
        _process_log_with_semaphore(log, get_token_symbol, get_token_price_usd, include_prices, semaphore)
        for log in latest_approvals.values()
    ))
    return results


def is_latest_approval(new_log: ApprovalLog, current_log: ApprovalLog) -> bool:
    return (new_log.block_number, new_log.log_index or 0) > (current_log.block_number, current_log.log_index or 0)
