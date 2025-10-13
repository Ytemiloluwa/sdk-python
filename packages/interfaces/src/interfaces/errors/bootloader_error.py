from enum import Enum
from typing import Dict
from .device_error import DeviceError


class DeviceBootloaderErrorType(Enum):
    NOT_IN_BOOTLOADER = "BTL_0000"
    FIRMWARE_SIZE_LIMIT_EXCEEDED = "BTL_0100"
    WRONG_HARDWARE_VERSION = "BTL_0101"
    WRONG_MAGIC_NUMBER = "BTL_0102"
    SIGNATURE_NOT_VERIFIED = "BTL_0103"
    LOWER_FIRMWARE_VERSION = "BTL_0104"
    NOT_IN_RECEIVING_MODE = "BTL_0105"
    FLASH_WRITE_ERROR = "BTL_0106"
    FLASH_CRC_MISMATCH = "BTL_0107"
    FLASH_TIMEOUT_ERROR = "BTL_0108"
    FLASH_NACK = "BTL_0109"


class CodeToErrorMap:
    def __init__(self):
        self._map: Dict[DeviceBootloaderErrorType, Dict[str, str]] = {
            DeviceBootloaderErrorType.NOT_IN_BOOTLOADER: {
                "message": "The device is not in bootloader mode"
            },
            DeviceBootloaderErrorType.FIRMWARE_SIZE_LIMIT_EXCEEDED: {
                "message": "Firmware Size Limit Exceed"
            },
            DeviceBootloaderErrorType.WRONG_HARDWARE_VERSION: {
                "message": "Wrong Hardware version"
            },
            DeviceBootloaderErrorType.WRONG_MAGIC_NUMBER: {
                "message": "Wrong Magic Number"
            },
            DeviceBootloaderErrorType.SIGNATURE_NOT_VERIFIED: {
                "message": "Signature not verified"
            },
            DeviceBootloaderErrorType.LOWER_FIRMWARE_VERSION: {
                "message": "Lower Firmware version"
            },
            DeviceBootloaderErrorType.FLASH_WRITE_ERROR: {
                "message": "Flash Write Error"
            },
            DeviceBootloaderErrorType.FLASH_CRC_MISMATCH: {
                "message": "Flash CRC Mismatch"
            },
            DeviceBootloaderErrorType.FLASH_TIMEOUT_ERROR: {
                "message": "Flash Timeout Error"
            },
            DeviceBootloaderErrorType.FLASH_NACK: {
                "message": "Flash Negative Acknowledgement"
            },
            DeviceBootloaderErrorType.NOT_IN_RECEIVING_MODE: {
                "message": "The device is in fault state"
            },
        }

    def __getitem__(self, key: DeviceBootloaderErrorType) -> Dict[str, str]:
        return self._map.get(key)


deviceBootloaderErrorTypeDetails = CodeToErrorMap()


class DeviceBootloaderError(DeviceError):

    def __init__(self, error_code: DeviceBootloaderErrorType):
        super().__init__(
            error_code.value,
            deviceBootloaderErrorTypeDetails[error_code]["message"],
            DeviceBootloaderError,
        )
