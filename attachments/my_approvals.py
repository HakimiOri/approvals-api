import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, Final

from eth_abi import decode
from eth_typing import ChecksumAddress, HexStr
from eth_utils import to_bytes, to_hex
from web3 import Web3
from web3.contract import Contract
from web3.types import FilterParams, LogReceipt

INFURA_API_KEY: Final[str] = "INFURA_API_KEY"
APPROVAL_EVENT_SIGNATURE_HASH: Final[str] = Web3.keccak(text="Approval(address,address,uint256)").hex()
MAX_UINT256: Final[int] = 2 ** 256 - 1
ERC20_SYMBOL_ABI: Final = [{
    "constant": True,
    "inputs": [],
    "name": "symbol",
    "outputs": [{"name": "", "type": "string"}],
    "type": "function"
}]


def get_infura_provider(api_key: str) -> Web3:
    infura_url = f"https://mainnet.infura.io/v3/{api_key}"
    w3: Web3 = Web3(Web3.HTTPProvider(infura_url))

    if not w3.is_connected():
        sys.exit("Error: Failed to connect to Infura. Check your API key and network connection.")
    return w3


def get_token_symbol(w3: Web3, token_address: ChecksumAddress, symbol_cache: Dict[str, str]) -> str:
    if token_address in symbol_cache:
        return symbol_cache[token_address]
    try:
        contract: Contract = w3.eth.contract(address=token_address, abi=ERC20_SYMBOL_ABI)
        symbol: str = contract.functions.symbol().call()
    except Exception:
        symbol = "UnknownERC20"
    symbol_cache[token_address] = symbol
    return symbol


def format_amount(amount: int) -> str:
    if amount >= MAX_UINT256:
        return "Unlimited"
    return f"{amount:,}"


def fetch_approval_logs(w3: Web3, owner_address: str) -> list[LogReceipt]:
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
        logs: list[LogReceipt] = w3.eth.get_logs(filter_params)
        return logs
    except Exception as e:
        sys.exit(f"Error fetching logs: {e}")


def parse_and_print_approvals(w3: Web3, approval_logs: list[LogReceipt]) -> None:
    latest_approvals = get_latest_approvals(approval_logs)
    symbol_cache = {}

    print("\nFetching latest approvals: \n")

    for log in latest_approvals.values():
        print_approval_info(w3, log, symbol_cache)


def get_latest_approvals(approval_logs: list[LogReceipt]) -> dict:
    latest_approvals = {}
    for log in approval_logs:
        token: str = log['address'].lower()
        spender: str = '0x' + log['topics'][2].hex()[-40:].lower()

        key = (token, spender)

        if key not in latest_approvals or (log['blockNumber'], log['logIndex']) > (latest_approvals[key]['blockNumber'],
                                                                                   latest_approvals[key]['logIndex']):
            latest_approvals[key] = log
    return latest_approvals


def print_approval_info(w3: Web3, log: LogReceipt, symbol_cache: dict) -> None:
    try:
        amount: int = decode(['uint256'], log['data'])[0]
        token: ChecksumAddress = Web3.to_checksum_address(log['address'])
        spender: ChecksumAddress = Web3.to_checksum_address('0x' + log['topics'][2].hex()[-40:])
        symbol: str = get_token_symbol(w3, token, symbol_cache)
        print(f"Approval on {symbol} for {format_amount(amount)} to {spender}")
    except Exception as e:
        print(f"Error decoding log: {e}")


def get_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        description="Fetch all ERC-20 Approval events ever made by an address."
    )
    parser.add_argument('--address', required=True,
                        help='Ethereum address to scan (checksum not required)')
    args: Namespace = parser.parse_args()
    return args


def main():
    args: Namespace = get_args()

    infura_api_key: str = os.environ.get(INFURA_API_KEY)
    if not infura_api_key:
        sys.exit("Exiting - INFURA_API_KEY environment variable is required")

    w3: Web3 = get_infura_provider(infura_api_key)

    try:
        owner_address: ChecksumAddress = Web3.to_checksum_address(args.address)
    except Exception:
        sys.exit("Error: Invalid Ethereum address")

    approval_logs: list[LogReceipt] = fetch_approval_logs(w3, owner_address)

    parse_and_print_approvals(w3, approval_logs)


if __name__ == "__main__":
    main()
