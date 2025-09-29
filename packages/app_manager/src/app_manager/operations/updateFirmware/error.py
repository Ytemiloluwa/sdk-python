from enum import Enum
from packages.interfaces.errors.device_error import DeviceError


class UpdateFirmwareErrorType(Enum):
    UNKNOWN_ERROR = 'MGA_UF_0000'
    VERSION_NOT_ALLOWED = 'MGA_UF_0100'


update_firmware_error_type_details = {
    UpdateFirmwareErrorType.UNKNOWN_ERROR: {
        'message': 'Unknown firmware update error',
    },
    UpdateFirmwareErrorType.VERSION_NOT_ALLOWED: {
        'message': 'Given firmware version is not allowed',
    },
}


class UpdateFirmwareError(DeviceError):
    def __init__(self, error_code: UpdateFirmwareErrorType):
        error_details = update_firmware_error_type_details[error_code]
        super().__init__(error_code.value, error_details['message'], UpdateFirmwareError)
