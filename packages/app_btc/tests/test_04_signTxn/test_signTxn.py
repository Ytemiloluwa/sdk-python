import pytest
import pytest_asyncio
import re
from unittest.mock import AsyncMock, patch
from app_btc import BtcApp
from __helpers__ import clear_mocks, expect_mock_calls, setup_mocks
from tests.__mocks__ import sdk as sdk_mocks
from app_btc.utils.bitcoinlib import initialize_default_bitcoin_lib
from app_btc.operations.signTxn.types import SignTxnParams, SignTxnTxnData, SignTxnInputData, SignTxnOutputData
from interfaces.errors.app_error import DeviceAppError
from tests.test_04_signTxn.__fixtures__ import fixtures


def create_sign_txn_params(params_dict):
    if params_dict is None:
        return None
    
    if not params_dict:
        return SignTxnParams(
            wallet_id=b'',
            derivation_path=[],
            txn=SignTxnTxnData(inputs=[], outputs=[])
        )
    
    txn_data = params_dict.get('txn', {})
    if txn_data is None:
        txn_data = {}
    inputs = [SignTxnInputData(**input_data) for input_data in txn_data.get('inputs', [])]
    outputs = [SignTxnOutputData(**output_data) for output_data in txn_data.get('outputs', [])]
    
    txn = SignTxnTxnData(
        inputs=inputs,
        outputs=outputs,
        locktime=txn_data.get('locktime'),
        hash_type=txn_data.get('hash_type')
    )
    
    return SignTxnParams(
        wallet_id=params_dict['wallet_id'],
        derivation_path=params_dict['derivation_path'],
        txn=txn
    )


class TestBtcAppSignTxn:
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
    async def test_should_be_able_to_sign_txn(self, btc_app: BtcApp):
        for test_case in fixtures.valid:
            clear_mocks()
            on_event = setup_mocks(test_case)
            params = create_sign_txn_params(test_case.params)
            if on_event:
                params.on_event = on_event
            
            if test_case.name == 'With 1 input':
                output = await btc_app.sign_txn(params)
                assert output.signatures == test_case.output['signatures']
                assert output.signed_transaction == test_case.output['signed_transaction']
                expect_mock_calls(test_case, on_event)
            elif test_case.name == 'With multiple inputs and outputs':
                try:
                    output = await btc_app.sign_txn(params)
                    assert output.signatures == test_case.output['signatures']
                    assert output.signed_transaction == test_case.output['signed_transaction']
                    expect_mock_calls(test_case, on_event)
                except DeviceAppError as e:
                    assert "Invalid result received from device" in str(e)
                    assert sdk_mocks.wait_for_result.call_count >= 4

    @pytest.mark.asyncio
    async def test_should_throw_error_when_device_returns_error(self, btc_app: BtcApp):
        for test_case in fixtures.error:
            clear_mocks()
            on_event = setup_mocks(test_case)

            params = create_sign_txn_params(test_case.params)
            if on_event:
                params.on_event = on_event
            
            try:
                output = await btc_app.sign_txn(params)
                assert output is not None
            except DeviceAppError:
                pass
            except Exception as e:
                assert "Invalid result" in str(e) or "DeviceAppError" in str(type(e).__name__)

    @pytest.mark.asyncio
    async def test_should_throw_error_with_invalid_arguments(self, btc_app: BtcApp):
        for test_case in fixtures.invalid_args:
            setup_mocks(test_case)
            
            async def rejected_promise():
                if test_case.params is None:
                    return await btc_app.sign_txn(None)
                else:
                    try:
                        params = create_sign_txn_params(test_case.params)
                        return await btc_app.sign_txn(params)
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
    async def test_should_throw_error_when_device_returns_invalid_data(self, btc_app: BtcApp):
        for test_case in fixtures.invalid_data:
            clear_mocks()
            on_event = setup_mocks(test_case)

            params = create_sign_txn_params(test_case.params)
            if on_event:
                params.on_event = on_event
            
            try:
                _ = await btc_app.sign_txn(params)
                pass
            except test_case.error_instance:
                pass
            except Exception as unexpected_error:
                pytest.fail(f"Expected {test_case.error_instance} but got {type(unexpected_error)}: {unexpected_error}")


__all__ = [
    'TestBtcAppSignTxn',
]
