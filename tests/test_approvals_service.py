import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.approvals_service import ApprovalsService
from app.models.approvals.approvals_request import ApprovalsRequest
from app.models.approvals.approvals_response import ApprovalsResponse
from app.models.approvals.approvals import Approval

def get_mocks(concurrency=1, retries=1, retry_delay=0):
    mock_approvals_dal = MagicMock()
    mock_config = MagicMock()
    mock_token_price_dal = MagicMock()
    mock_config.approvals_service_concurrency_limit = concurrency
    mock_config.approvals_api_retries = retries
    mock_config.approvals_api_retry_delay = retry_delay
    service = ApprovalsService(mock_approvals_dal, mock_token_price_dal)
    return service, mock_approvals_dal, mock_config, mock_token_price_dal

def test_singleton():
    # Arrange
    dal = MagicMock()
    config = MagicMock()
    token_price_dal = MagicMock()

    # Act
    s1 = ApprovalsService.get_instance(dal, token_price_dal)
    s2 = ApprovalsService.get_instance(dal, token_price_dal)

    # Assert
    assert s1 is s2

@pytest.mark.asyncio
async def test_get_latest_approvals_success(monkeypatch):
    # Arrange
    service, mock_dal, mock_config, mock_token_price_dal = get_mocks(concurrency=2)
    mock_dal.fetch_approval_logs = AsyncMock(return_value=[])
    async def mock_process_approval_logs(*args, **kwargs):
        return [
            Approval(amount="100", spender_address="0xsp1", token_symbol="TKN"),
            Approval(amount="200", spender_address="0xsp2", token_symbol="TKN2")
        ]
    monkeypatch.setattr("app.services.approvals_service.process_approval_logs", mock_process_approval_logs)
    addresses = ["0x123", "0x456"]
    request = ApprovalsRequest(addresses=addresses)

    # Act
    response = await service.get_latest_approvals(request)

    # Assert
    assert isinstance(response, ApprovalsResponse)
    assert set(response.approvalsByAddress.keys()) == set(addresses)
    for addr in addresses:
        assert response.approvalsByAddress[addr] == [
            Approval(amount="100", spender_address="0xsp1", token_symbol="TKN"),
            Approval(amount="200", spender_address="0xsp2", token_symbol="TKN2")
        ]
    assert response.errorsByAddress == {}

@pytest.mark.asyncio
async def test_get_latest_approvals_with_error(monkeypatch):
    # Arrange
    service, mock_dal, mock_config, mock_token_price_dal = get_mocks()
    async def raise_exc(*args, **kwargs):
        raise Exception("fetch error")
    mock_dal.fetch_approval_logs = raise_exc
    monkeypatch.setattr("app.services.approvals_service.process_approval_logs", AsyncMock(return_value=[]))
    addresses = ["0xabc"]
    request = ApprovalsRequest(addresses=addresses)

    # Act
    response = await service.get_latest_approvals(request)

    # Assert
    assert isinstance(response, ApprovalsResponse)
    assert response.approvalsByAddress["0xabc"] == []
    if "0xabc" not in response.errorsByAddress:
        print("errorsByAddress:", response.errorsByAddress)
    assert "0xabc" in response.errorsByAddress
    assert "fetch error" in response.errorsByAddress["0xabc"]

@pytest.mark.asyncio
async def test_get_latest_approvals_include_prices(monkeypatch):
    # Arrange
    service, mock_dal, mock_config, mock_token_price_dal = get_mocks()
    mock_dal.fetch_approval_logs = AsyncMock(return_value=[])
    async def mock_process_approval_logs(*args, **kwargs):
        assert kwargs.get("include_prices") is True
        return [Approval(amount="300", spender_address="0xsp3", token_symbol="TKN3", price_usd=1.23)]
    monkeypatch.setattr("app.services.approvals_service.process_approval_logs", mock_process_approval_logs)
    addresses = ["0xdef"]
    request = ApprovalsRequest(addresses=addresses, include_prices=True)

    # Act
    response = await service.get_latest_approvals(request)

    # Assert
    assert isinstance(response, ApprovalsResponse)
    assert response.approvalsByAddress["0xdef"] == [Approval(amount="300", spender_address="0xsp3", token_symbol="TKN3", price_usd=1.23)]
    assert response.errorsByAddress == {}

def teardown_function():
    ApprovalsService._instance = None
