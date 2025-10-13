from typing import TYPE_CHECKING
from unittest.mock import MagicMock, AsyncMock
from tests.__helpers__ import (
    clear_mocks as super_clear_mocks,
    expect_mock_calls as super_expect_mock_calls,
)
from app_btc.proto.generated.btc import Query, Result
from tests.__mocks__ import sdk as sdk_mocks

if TYPE_CHECKING:
    from ..__fixtures__.types import SignTxnTestCase


def setup_mocks(test_case: "SignTxnTestCase") -> MagicMock:
    """Setup mocks for signTxn test case with protobuf deserialization."""
    on_event = MagicMock()

    for _ in test_case.queries:
        sdk_mocks.send_query.return_value = AsyncMock(return_value=None)()

    mock_implementations = []

    for result in test_case.results:

        async def mock_wait_for_result(params=None):
            if (
                params
                and hasattr(params, "on_status")
                and params.on_status
                and result.statuses
            ):
                on_event_calls = 0

                for status in result.statuses:
                    await params.on_status({"flow_status": status.flow_status})

                    if status.expect_event_calls is not None:
                        for i, expected_call in enumerate(status.expect_event_calls):
                            mock_index = (
                                len(on_event.call_args_list)
                                - len(status.expect_event_calls)
                                + i
                            )

                            assert on_event.call_args_list[mock_index] == (
                                (expected_call,),
                            )

                        on_event_calls += len(status.expect_event_calls)
                        assert on_event.call_count == on_event_calls
                    else:
                        assert on_event.call_count == on_event_calls

            return result.data

        mock_implementations.append(mock_wait_for_result)

    async def side_effect_handler(*args, **kwargs):
        if mock_implementations:
            return await mock_implementations.pop(0)(*args, **kwargs)
        return bytes([])

    sdk_mocks.wait_for_result.side_effect = side_effect_handler

    return on_event


def clear_mocks() -> None:
    """Clear all mocks for signTxn tests."""
    super_clear_mocks()


def expect_mock_calls(test_case: "SignTxnTestCase", on_event: MagicMock) -> None:
    """Verify mock calls for signTxn test case."""
    super_expect_mock_calls(test_case, on_event)


def query_to_bytes(query_data: dict) -> bytes:
    """Convert query data to bytes using protobuf serialization."""
    return Query(**query_data).SerializeToString()


def result_to_bytes(result_data: dict) -> bytes:
    """Convert result data to bytes using protobuf serialization."""
    return Result(**result_data).SerializeToString()


__all__ = [
    "setup_mocks",
    "clear_mocks",
    "expect_mock_calls",
    "query_to_bytes",
    "result_to_bytes",
]
