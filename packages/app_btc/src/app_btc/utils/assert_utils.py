from typing import TypeVar, Optional
from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType
from util.utils.assert_utils import assert_condition
from ..proto.generated.error import CommonError

T = TypeVar("T")


def assert_or_throw_invalid_result(condition: T) -> T:
    """
    Assert that condition is not None or undefined, throw DeviceAppError if it is.
    Equivalent to TypeScript assertOrThrowInvalidResult function.

    Args:
        condition: The value to check

    Returns:
        The condition if it's not None

    Raises:
        DeviceAppError: If condition is None or falsy
    """
    assert_condition(
        condition, DeviceAppError(DeviceAppErrorType.INVALID_MSG_FROM_DEVICE)
    )
    return condition


def parse_common_error(error: Optional[CommonError]) -> None:
    """
    Parse common error and raise appropriate DeviceAppError.
    Equivalent to TypeScript parseCommonError function.

    Args:
        error: The common error object to parse

    Raises:
        DeviceAppError: If any error is found in the error object
    """
    if error is None:
        return

    error_fields = [
        ("unknown_error", DeviceAppErrorType.UNKNOWN_ERROR),
        ("device_setup_required", DeviceAppErrorType.DEVICE_SETUP_REQUIRED),
        ("wallet_not_found", DeviceAppErrorType.WALLET_NOT_FOUND),
        ("wallet_partial_state", DeviceAppErrorType.WALLET_PARTIAL_STATE),
        ("card_error", DeviceAppErrorType.CARD_OPERATION_FAILED),
        ("user_rejection", DeviceAppErrorType.USER_REJECTION),
        ("corrupt_data", DeviceAppErrorType.CORRUPT_DATA),
    ]

    for field_name, error_type in error_fields:
        if hasattr(error, field_name):
            error_value = getattr(error, field_name)
            if error_value is not None and error_value != 0:
                raise DeviceAppError(error_type, error_value)
