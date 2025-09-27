from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from packages.app_btc.tests.__helpers__ import (
    setup_mocks as super_setup_mocks,
    clear_mocks as super_clear_mocks,
    expect_mock_calls as super_expect_mock_calls,
)

if TYPE_CHECKING:
    from packages.app_btc.tests.test_03_getXpubs.__fixtures__.types import GetXpubsTestCase


def setup_mocks(test_case: 'GetXpubsTestCase') -> MagicMock:
    """Setup mocks for getXpubs test case."""
    return super_setup_mocks(test_case)


def clear_mocks() -> None:
    """Clear all mocks for getXpubs tests."""
    super_clear_mocks()


def expect_mock_calls(test_case: 'GetXpubsTestCase', on_event: MagicMock) -> None:
    """Verify mock calls for getXpubs test case."""
    super_expect_mock_calls(test_case, on_event)


__all__ = [
    'setup_mocks',
    'clear_mocks', 
    'expect_mock_calls',
]

