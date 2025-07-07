import logging
import os
import sys
from typing import Final, List

import cachetools
from eth_abi import decode
from eth_typing import ChecksumAddress, HexStr
from eth_utils import to_bytes, to_hex
from web3.eth import AsyncEth
from web3 import AsyncWeb3
from web3.types import FilterParams, LogReceipt

from app.models.approvals import ApprovalLog
from app.Utils.config_loader import config
from .approvals_dal import ApprovalsDAL

APPROVAL_EVENT_SIGNATURE_HASH: Final[str] = AsyncWeb3.keccak(text="Approval(address,address,uint256)").hex()
ERC20_SYMBOL_ABI: Final = [{
    "constant": True,
    "inputs": [],
    "name": "symbol",
    "outputs": [{"name": "", "type": "string"}],
    "type": "function"
}]

INFURA_API_KEY = os.environ.get("INFURA_API_KEY")
if not INFURA_API_KEY:
    sys.exit("Error: INFURA_API_KEY environment variable not set.")

class InfuraDAL(ApprovalsDAL):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, logger=None):
        if getattr(self, '_initialized', False):
            return
        self.w3 = self._get_infura_provider()
        self.symbol_cache = cachetools.LRUCache(maxsize=config.lru_cache_maxsize)
        self._logger = logger or logging.getLogger(__name__)
        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()

    @staticmethod
    def _get_infura_provider() -> AsyncWeb3:
        infura_url = f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"
        w3: AsyncWeb3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(infura_url), modules={"eth": (AsyncEth,)})
        return w3

#Todo: Change Dal name as get_token_symbol has nothing to do with approvals
    async def get_token_symbol(self, token_address: ChecksumAddress) -> str:
        if token_address in self.symbol_cache:
            return self.symbol_cache[token_address]
        try:
            contract = self.w3.eth.contract(address=token_address, abi=ERC20_SYMBOL_ABI)
            symbol: str = await contract.functions.symbol().call()
        except (ValueError, ConnectionError, KeyError, AttributeError) as e:
            self._logger.warning(f"Failed to fetch token symbol for {token_address}: {e}")
            symbol = "UnknownERC20"
        self.symbol_cache[token_address] = symbol
        return symbol

    async def fetch_approval_logs(self, owner_address: str) -> List[ApprovalLog]:
        address_bytes: bytes = to_bytes(hexstr=owner_address)
        topic_owner: HexStr = to_hex(b'\x00' * 12 + address_bytes)

        filter_params: FilterParams = {
            "fromBlock": 0,
            "toBlock": "latest",
            "topics": [
                '0x' + APPROVAL_EVENT_SIGNATURE_HASH,
                topic_owner
            ]
        }

        try:
            logs: list[LogReceipt] = await self.w3.eth.get_logs(filter_params)
            approval_logs = []
            for log in logs:
                approval_logs.append(ApprovalLog(
                    block_number=log.get('blockNumber'),
                    transaction_hash=log.get('transactionHash').hex() if log.get('transactionHash') else '',
                    amount=decode(['uint256'], log['data'])[0],
                    spender='0x' + log['topics'][2].hex()[-40:].lower(),
                    token_address=log.get('address'),
                    log_index=log.get('logIndex')
                ))
            return approval_logs
        except (ValueError, ConnectionError, KeyError) as e:
            self._logger.error(f"Error fetching approval logs for {owner_address}: {e}")
            raise RuntimeError(f"Error fetching logs: {e}")
