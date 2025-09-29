import pytest
import asyncio
from packages.app_btc.src.operations.getPublicKey.publicKeyToAddress.__fixtures__ import (
    get_address_from_public_key_test_cases
)
from packages.app_btc.src.operations.getPublicKey.publicKeyToAddress import (
    get_address_from_public_key
)
from packages.app_btc.src.utils.bitcoinlib import set_bitcoin_py_lib

try:
    import bitcoinlib
except ImportError:
    pytest.skip("bitcoinlib not available", allow_module_level=True)


class TestGetAddressFromPublicKey:
    @pytest.fixture(autouse=True)
    def setup_bitcoin_lib(self):
        set_bitcoin_py_lib(bitcoinlib)
    
    @pytest.mark.asyncio
    async def test_should_return_valid_addresses(self):
        for test_case in get_address_from_public_key_test_cases['valid']:
            result = get_address_from_public_key(
                test_case['input']['public_key'],
                test_case['input']['derivation_path'],
            )
            assert result == test_case['output']
    
    @pytest.mark.asyncio
    async def test_should_throw_error_for_invalid_path(self):
        for test_case in get_address_from_public_key_test_cases['invalid']:
            with pytest.raises(Exception):
                 get_address_from_public_key(
                    test_case['public_key'],
                    test_case['derivation_path'],
                )

def test_valid_addresses():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Setup
    set_bitcoin_py_lib(bitcoinlib)
    
    try:
        for test_case in get_address_from_public_key_test_cases['valid']:
            result = loop.run_until_complete(
                get_address_from_public_key(
                    test_case['input']['public_key'],
                    test_case['input']['derivation_path'],
                )
            )
            assert result == test_case['output']
    finally:
        loop.close()


def test_invalid_addresses():
    """Synchronous wrapper for invalid address tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Setup
    set_bitcoin_py_lib(bitcoinlib)
    
    try:
        for test_case in get_address_from_public_key_test_cases['invalid']:
            with pytest.raises(Exception):
                loop.run_until_complete(
                    get_address_from_public_key(
                        test_case['public_key'],
                        test_case['derivation_path'],
                    )
                )
    finally:
        loop.close()
