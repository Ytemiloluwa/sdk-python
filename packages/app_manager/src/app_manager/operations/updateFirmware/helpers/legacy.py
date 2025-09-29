from packages.core.src.types import ISDK
from packages.interfaces.errors import (
    DeviceCompatibilityError,
    DeviceCompatibilityErrorType,
)
from packages.interfaces.errors.app_error import DeviceAppError,DeviceAppErrorType
from packages.core.src.encoders.proto.generated.common import Version


def create_version_hex(version: Version) -> str:
    hex_str = f"{version.major:02x}"
    hex_str += f"{version.minor:02x}"
    hex_str += f"{version.patch:04x}"
    return hex_str


async def handle_legacy_device(sdk: ISDK, version: Version) -> None:
    is_confirmed = False
    firmware_version_hex = create_version_hex(version)

    if await sdk.deprecated.is_raw_operation_supported():
        sequence_number = await sdk.get_new_sequence_number()

        await sdk.deprecated.send_command({
            'commandType': 77,
            'data': firmware_version_hex,
            'sequenceNumber': sequence_number,
        })

        update_confirmed = await sdk.deprecated.wait_for_command_output({
            'sequenceNumber': sequence_number,
            'expectedCommandTypes': [78],
        })

        is_confirmed = update_confirmed.data.startswith('01')
    else:
        raise DeviceCompatibilityError(DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED)

    if not is_confirmed:
        raise DeviceAppError(DeviceAppErrorType.USER_REJECTION)
