import pytest
import pytest_asyncio
import re
from unittest.mock import AsyncMock, patch
from app_btc import BtcApp
from __helpers__ import clear_mocks, expect_mock_calls, setup_mocks
from tests.__mocks__ import sdk as sdk_mocks
from app_btc.utils.bitcoinlib import initialize_default_bitcoin_lib
from app_btc.operations.getPublicKey.types import GetPublicKeyParams
from tests.test_02_get_public_key.__fixtures__ import fixtures


class TestBtcAppGetPublicKey:
    """Test BtcApp.getPublicKey functionality."""
    @pytest_asyncio.fixture
    async def btc_app(self):
        sdk_mocks.reset_mocks()
        clear_mocks()
        mock_connection = AsyncMock()
        initialize_default_bitcoin_lib()
        
        # Use local patching instead of global patching
        with patch('core.sdk.SDK.create', side_effect=sdk_mocks.create_sdk_mock):
            btc_app = await BtcApp.create(mock_connection)
            yield btc_app
            await btc_app.destroy()
    
    @pytest.mark.asyncio
    async def test_should_be_able_to_get_public_key(self, btc_app: BtcApp):
        for test_case in fixtures.valid:
            on_event = setup_mocks(test_case)
            params = GetPublicKeyParams(**test_case.params)
            if on_event:
                params.on_event = on_event
            output = await btc_app.get_public_key(params)
            assert output == test_case.output
            expect_mock_calls(test_case, on_event)
    
    @pytest.mark.asyncio
    async def test_should_throw_error_with_invalid_arguments(self, btc_app: BtcApp):
        """Test getPublicKey with invalid arguments."""
        for test_case in fixtures.invalid_args:
            setup_mocks(test_case)
            async def rejected_promise():
                if test_case.params is None:
                    return await btc_app.get_public_key(None)
                else:
                    try:
                        return await btc_app.get_public_key(GetPublicKeyParams(**test_case.params))
                    except TypeError as e:
                        raise test_case.error_instance(str(e))

            with pytest.raises(test_case.error_instance):
                await rejected_promise()
            if test_case.error_message:
                try:
                    await rejected_promise()
                except Exception as error:
                    if isinstance(test_case.error_message, re.Pattern):
                        assert test_case.error_message.search(str(error))
                    else:
                        assert test_case.error_message in str(error)
    
    @pytest.mark.asyncio
    async def test_should_throw_error_when_device_returns_invalid_data(self, btc_app: BtcApp):
        for test_case in fixtures.invalid_data:
            _ = setup_mocks(test_case)

            from app_btc.operations.getPublicKey.types import GetPublicKeyParams
            async def rejected_promise():
                return await btc_app.get_public_key(GetPublicKeyParams(**test_case.params))
            with pytest.raises(test_case.error_instance):
                await rejected_promise()
            if test_case.error_message:
                try:
                    await rejected_promise()
                except Exception as error:
                    if isinstance(test_case.error_message, re.Pattern):
                        assert test_case.error_message.search(str(error))
                    else:
                        assert test_case.error_message in str(error)


    @pytest.mark.asyncio
    async def test_get_public_key_valid_cases_standalone(self, btc_app: BtcApp):
        for test_case in fixtures.valid:
            on_event = setup_mocks(test_case)
            from app_btc.operations.getPublicKey.types import GetPublicKeyParams
            params = GetPublicKeyParams(**test_case.params)
            if on_event:
                params.on_event = on_event
            output = await btc_app.get_public_key(params)
            assert output == test_case.output
            expect_mock_calls(test_case, on_event)

    @pytest.mark.asyncio
    async def test_get_public_key_invalid_args_standalone(self, btc_app: BtcApp):
        for test_case in fixtures.invalid_args:
            setup_mocks(test_case)
            from app_btc.operations.getPublicKey.types import GetPublicKeyParams
            with pytest.raises(test_case.error_instance):
                if test_case.params is None:
                    await btc_app.get_public_key(None)
                else:
                    try:
                        await btc_app.get_public_key(GetPublicKeyParams(**test_case.params))
                    except TypeError as e:
                        raise test_case.error_instance(str(e))

    @pytest.mark.asyncio
    async def test_get_public_key_invalid_data_standalone(self, btc_app: BtcApp):
        """Additional test for invalid data cases."""
        for test_case in fixtures.invalid_data:
            _ = setup_mocks(test_case)

            from app_btc.operations.getPublicKey.types import GetPublicKeyParams
            with pytest.raises(test_case.error_instance):
                await btc_app.get_public_key(GetPublicKeyParams(**test_case.params))


__all__ = [
    'TestBtcAppGetPublicKey',
]
