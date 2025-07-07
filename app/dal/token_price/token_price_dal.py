from abc import ABC, abstractmethod
from typing import Optional

class TokenPriceDAL(ABC):
    @abstractmethod
    async def get_token_price_usd(self, token_address: str) -> Optional[float]:
        pass

