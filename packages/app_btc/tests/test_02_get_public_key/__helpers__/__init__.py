from typing import TYPE_CHECKING
from unittest.mock import MagicMock, AsyncMock

from tests.__helpers__ import (
    setup_mocks as super_setup_mocks,
    clear_mocks as super_clear_mocks,
    expect_mock_calls as super_expect_mock_calls,
)
from tests.__mocks__ import sdk as sdk_mocks

if TYPE_CHECKING:
    from ..__fixtures__.types import GetPublicKeyTestCase


def setup_mocks(test_case: "GetPublicKeyTestCase") -> MagicMock:
    """Setup mocks for getPublicKey test case."""
    on_event = MagicMock()

    # Mock sendQuery for each query
    for _ in test_case.queries:
        sdk_mocks.send_query.return_value = AsyncMock(return_value=None)()

    # Mock waitForResult - return the first result's data
    if test_case.results:
        first_result = test_case.results[0]

        async def mock_wait_for_result(params=None):
            if (
                params
                and hasattr(params, "on_status")
                and params.on_status
                and first_result.statuses
            ):
                on_event_calls = 0

                for status in first_result.statuses:
                    # Call onStatus with flowStatus
                    await params.on_status({"flow_status": status.flow_status})

                    if status.expect_event_calls is not None:
                        for j, expected_call in enumerate(status.expect_event_calls):
                            mock_index = (
                                len(on_event.call_args_list)
                                - len(status.expect_event_calls)
                                + j
                            )

                            # Verify the mock call
                            assert on_event.call_args_list[mock_index] == (
                                (expected_call,),
                            )

                        on_event_calls += len(status.expect_event_calls)
                        assert on_event.call_count == on_event_calls
                    else:
                        assert on_event.call_count == on_event_calls

            # For invalid data tests, return data that will cause parsing to fail
            # or result in an invalid result that gets caught by assert_or_throw_invalid_result
            if len(first_result.data) == 0:
                # Return empty data that will cause parsing to fail
                return b""
            else:
                # Return the raw data - the operation will parse it
                return first_result.data

        sdk_mocks.wait_for_result.side_effect = mock_wait_for_result

    return on_event


def clear_mocks() -> None:
    """Clear all mocks for getPublicKey tests."""
    super_clear_mocks()


def expect_mock_calls(test_case: "GetPublicKeyTestCase", on_event: MagicMock) -> None:
    """Verify mock calls for getPublicKey test case."""
    # Verify runOperation was called once
    assert sdk_mocks.run_operation.call_count == 1

    # Verify sendQuery calls match expected queries
    send_query_calls = [call[0][0] for call in sdk_mocks.send_query.call_args_list]
    expected_query_data = [query.data for query in test_case.queries]
    assert send_query_calls == expected_query_data

    # Verify event calls if specified
    if test_case.mocks and test_case.mocks.event_calls:
        actual_calls = [list(call[0]) for call in on_event.call_args_list]
        assert actual_calls == test_case.mocks.event_calls


__all__ = [
    "setup_mocks",
    "clear_mocks",
    "expect_mock_calls",
]
