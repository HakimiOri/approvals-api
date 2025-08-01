import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    lru_cache_maxsize: int
    approvals_api_retries: int
    approvals_service_concurrency_limit: int
    log_processor_concurrency_limit: int
    approvals_api_retry_delay: int
    coingecko_api_url: str


class ConfigProvider(ABC):
    @abstractmethod
    def load(self) -> Config:
        pass


class DefaultConfigProvider(ConfigProvider):
    def __init__(self, module_name: str = 'config'):
        self.module_name = module_name

    def load(self) -> Config:
        mod = importlib.import_module(self.module_name)
        data = {k: v for k, v in vars(mod).items() if k.isupper()}
        return Config(
            lru_cache_maxsize=int(data['LRU_CACHE_MAXSIZE']),
            approvals_api_retries=int(data['APPROVALS_API_RETRIES']),
            approvals_service_concurrency_limit=int(data['APPROVALS_SERVICE_CONCURRENCY_LIMIT']),
            log_processor_concurrency_limit=int(data['LOG_PROCESSOR_CONCURRENCY_LIMIT']),
            approvals_api_retry_delay=int(data['APPROVALS_API_RETRY_DELAY']),
            coingecko_api_url=data['COINGECKO_API_URL'],
        )


config = DefaultConfigProvider().load()
