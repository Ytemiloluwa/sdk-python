import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from app_btc import BtcApp
from tests.__mocks__ import sdk as sdk_mocks
from app_btc.utils.bitcoinlib import initialize_default_bitcoin_lib


class TestBtcAppCreate:
    @pytest_asyncio.fixture
    async def btc_app(self):
        mock_connection = AsyncMock()
        initialize_default_bitcoin_lib()

        # Use local patching instead of global patching
        with patch("core.sdk.SDK.create", side_effect=sdk_mocks.create_sdk_mock):
            btc_app = await BtcApp.create(mock_connection)
            yield btc_app
            await btc_app.destroy()

    @pytest.mark.asyncio
    async def test_should_be_able_to_create_btc_app_instance(self, btc_app: BtcApp):
        assert btc_app is not None
        assert isinstance(btc_app, BtcApp)

    @pytest.mark.asyncio
    async def test_btc_app_create_standalone(self):
        mock_connection = AsyncMock()
        initialize_default_bitcoin_lib()

        # Use local patching instead of global patching
        with patch("core.sdk.SDK.create", side_effect=sdk_mocks.create_sdk_mock):
            btc_app = await BtcApp.create(mock_connection)
            try:
                assert btc_app is not None
                assert isinstance(btc_app, BtcApp)
            finally:
                await btc_app.destroy()


__all__ = [
    "TestBtcAppCreate",
]
