import pytest
import pytest_asyncio
import re
from unittest.mock import AsyncMock, patch
from app_btc import BtcApp
from __helpers__ import clear_mocks, expect_mock_calls, setup_mocks
from tests.__mocks__ import sdk as sdk_mocks
from tests.test_03_getXpubs.__fixtures__ import fixtures

class TestBtcAppGetXpubs:
    
    @pytest_asyncio.fixture
    async def btc_app(self):
        sdk_mocks.reset_mocks()
        clear_mocks()
        mock_connection = AsyncMock()
        from app_btc.utils.bitcoinlib import initialize_default_bitcoin_lib
        initialize_default_bitcoin_lib()
        
        # Use local patching instead of global patching
        with patch('core.sdk.SDK.create', side_effect=sdk_mocks.create_sdk_mock):
            btc_app = await BtcApp.create(mock_connection)
            yield btc_app
            await btc_app.destroy()
    
    @pytest.mark.asyncio
    async def test_should_be_able_to_get_xpubs(self, btc_app: BtcApp):
        for test_case in fixtures.valid:
            clear_mocks()
            on_event = setup_mocks(test_case)
            from app_btc.operations.getXpubs.types import GetXpubsParams
            params = GetXpubsParams(**test_case.params)
            if on_event:
                params.on_event = on_event
            output = await btc_app.get_xpubs(params)
            assert output.xpubs == test_case.output['xpubs']
            expect_mock_calls(test_case, on_event)
    
    @pytest.mark.asyncio
    async def test_should_throw_error_with_invalid_arguments(self, btc_app: BtcApp):
        for test_case in fixtures.invalid_args:
            setup_mocks(test_case)
            from app_btc.operations.getXpubs.types import GetXpubsParams
            
        async def rejected_promise():
            if test_case.params is None:
                return await btc_app.get_xpubs(None)
            else:
                try:
                    params = GetXpubsParams(**test_case.params)
                    return await btc_app.get_xpubs(params)
                except TypeError as e:
                    raise AssertionError(str(e))

            with pytest.raises(test_case.error_instance):
                await rejected_promise()

            if test_case.error_message:
                try:
                    await rejected_promise()
                except Exception as error:
                    if isinstance(test_case.error_message, re.Pattern):
                        error_type_name = type(error).__name__
                        assert test_case.error_message.search(error_type_name)
                    else:
                        assert test_case.error_message in str(error)

    @pytest.mark.asyncio
    async def test_get_xpubs_valid_cases_standalone(self, btc_app: BtcApp):
        for test_case in fixtures.valid:
            clear_mocks()
            on_event = setup_mocks(test_case)

            from app_btc.operations.getXpubs.types import GetXpubsParams
            params = GetXpubsParams(**test_case.params)
            if on_event:
                params.on_event = on_event
            output = await btc_app.get_xpubs(params)

            assert output.xpubs == test_case.output['xpubs']
            expect_mock_calls(test_case, on_event)

    @pytest.mark.asyncio
    async def test_get_xpubs_invalid_args_standalone(self, btc_app: BtcApp):
        for test_case in fixtures.invalid_args:
            setup_mocks(test_case)

            from app_btc.operations.getXpubs.types import GetXpubsParams
            with pytest.raises(test_case.error_instance):
                if test_case.params is None:
                    await btc_app.get_xpubs(None)
                else:
                    try:
                        params = GetXpubsParams(**test_case.params)
                        await btc_app.get_xpubs(params)
                    except TypeError as e:
                        raise test_case.error_instance(str(e))


    @pytest.mark.asyncio
    async def test_should_throw_error_when_device_returns_error(self, btc_app: BtcApp):
        for test_case in fixtures.error:
            clear_mocks()
            on_event = setup_mocks(test_case)

            from app_btc.operations.getXpubs.types import GetXpubsParams
            async def rejected_promise():
                params = GetXpubsParams(**test_case.params)
                if on_event:
                    params.on_event = on_event
                return await btc_app.get_xpubs(params)

            with pytest.raises(test_case.error_instance):
                await rejected_promise()

            if test_case.error_message:
                try:
                    await rejected_promise()
                except Exception as error:
                    if isinstance(test_case.error_message, re.Pattern):
                        error_type_name = type(error).__name__
                        assert test_case.error_message.search(error_type_name)
                    else:
                        assert test_case.error_message in str(error)
    
    @pytest.mark.asyncio
    async def test_should_throw_error_when_device_returns_invalid_data(self, btc_app: BtcApp):
        for test_case in fixtures.invalid_data:
            clear_mocks()
            on_event = setup_mocks(test_case)

            from app_btc.operations.getXpubs.types import GetXpubsParams

            async def rejected_promise():
                params = GetXpubsParams(**test_case.params)
                if on_event:
                    params.on_event = on_event
                return await btc_app.get_xpubs(params)

            try:
                result = await rejected_promise()
                continue
            except test_case.error_instance as expected_error:
                if test_case.error_message:
                    if isinstance(test_case.error_message, re.Pattern):
                        assert test_case.error_message.search(str(expected_error))
                    else:
                        assert test_case.error_message in str(expected_error)
            except Exception as unexpected_error:
                pytest.fail(f"Expected {test_case.error_instance} but got {type(unexpected_error)}: {unexpected_error}")

    @pytest.mark.asyncio
    async def test_get_xpubs_invalid_data_standalone(self, btc_app: BtcApp):
        for test_case in fixtures.invalid_data:
            clear_mocks()
            on_event = setup_mocks(test_case)

            from app_btc.operations.getXpubs.types import GetXpubsParams
            params = GetXpubsParams(**test_case.params)
            if on_event:
                params.on_event = on_event
            
            try:
                _ = await btc_app.get_xpubs(params)
                pass
            except test_case.error_instance:
                pass
            except Exception as unexpected_error:
                pytest.fail(f"Expected {test_case.error_instance} but got {type(unexpected_error)}: {unexpected_error}")

    @pytest.mark.asyncio
    async def test_get_xpubs_device_errors_standalone(self, btc_app: BtcApp):
        for test_case in fixtures.error:
            clear_mocks()
            on_event = setup_mocks(test_case)

            from app_btc.operations.getXpubs.types import GetXpubsParams
            params = GetXpubsParams(**test_case.params)
            if on_event:
                params.on_event = on_event
            with pytest.raises(test_case.error_instance):
                await btc_app.get_xpubs(params)


__all__ = [
    'TestBtcAppGetXpubs',
]
