from typing import Optional

import httpx
import cachetools
import logging

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
        self._logger = logging.getLogger(__name__)
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
        api_url = config.coingecko_api_url
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, params=params)
                if response.status_code != 200:
                    self._logger.warning(f"Coingecko API returned status {response.status_code} for {token_address}")
                    return None
                data = response.json()
                price_info = data.get(token_address.lower())
                if price_info and "usd" in price_info:
                    price_usd = float(price_info["usd"])
                    self._logger.info(f"Found USD price for {token_address}: {price_usd}")
                    self._price_cache[token_address] = price_usd
                    return price_usd
                self._logger.info(f"No USD price found in Coingecko response for {token_address}")
                self._price_cache[token_address] = None
                return None
        except httpx.RequestError as e:
            self._logger.error(f"HTTP error fetching price for {token_address}: {e}")
            return None
        except (TypeError, ValueError) as e:
            self._logger.error(f"Data or parsing error processing price for {token_address}: {e}")
            return None
