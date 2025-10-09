from typing import List
from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType, deviceAppErrorTypeDetails
from .types import IGetWalletsTestCase

with_unknown_error: IGetWalletsTestCase = {
    'name': 'With unknown error',
    'query': bytes([18, 2, 10, 0]),
    'result': bytes([18, 4, 18, 2, 8, 0]),
    'error_instance': DeviceAppError,
    'error_message': deviceAppErrorTypeDetails[DeviceAppErrorType.UNKNOWN_ERROR]['message'],
}

with_invalid_app_id: IGetWalletsTestCase = {
    'name': 'With corrupt msg from device',
    'query': bytes([18, 2, 10, 0]),
    'result': bytes([18, 4, 18, 2, 16, 0]),
    'error_instance': DeviceAppError,
    'error_message': deviceAppErrorTypeDetails[DeviceAppErrorType.CORRUPT_DATA]['message'],
}

error: List[IGetWalletsTestCase] = [with_unknown_error, with_invalid_app_id]
