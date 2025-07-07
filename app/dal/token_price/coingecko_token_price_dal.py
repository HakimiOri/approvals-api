from typing import Optional

import httpx
import cachetools

from app.dal.token_price.token_price_dal import TokenPriceDAL
from app.utils.config_loader import config


class CoingeckoTokenPriceDAL(TokenPriceDAL):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        self._price_cache = cachetools.LRUCache(maxsize=config.lru_cache_maxsize)
        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()

    async def get_token_price_usd(self, token_address: str) -> Optional[float]:
        if token_address in self._price_cache:
            return self._price_cache[token_address]
        params = {
            "contract_addresses": token_address,
            "vs_currencies": "usd"
        }
        api_url = getattr(config, "coingecko_api_url", "https://api.coingecko.com/api/v3/simple/token_price/ethereum")
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            if response.status_code != 200:
                return None
            data = response.json()
            price_info = data.get(token_address.lower())
            if price_info and "usd" in price_info:
                price = float(price_info["usd"])
                self._price_cache[token_address] = price
                return price
            self._price_cache[token_address] = None
            return None
