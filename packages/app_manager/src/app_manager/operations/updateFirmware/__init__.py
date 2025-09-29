from typing import Optional
from packages.core.src.types import ISDK
from packages.util.utils import create_logger_with_prefix, create_status_listener, string_to_version, uint8array_to_hex
from packages.app_manager.src.constants.appId import APP_VERSION
from packages.app_manager.src.proto.generated.manager import FirmwareUpdateErrorResponse, FirmwareUpdateError
from packages.app_manager.src.proto.types import UpdateFirmwareStatus
from packages.app_manager.src.services import firmware_service
from packages.app_manager.src.utils import assert_or_throw_invalid_result, OperationHelper
from packages.app_manager.src.utils import logger as rootlogger
from .error import UpdateFirmwareError, UpdateFirmwareErrorType
from .helpers import create_bootloader_sdk, handle_legacy_device, wait_for_reconnection
from .types import IUpdateFirmwareParams, UpdateFirmwareEventHandler

# Re-export types
__all__ = ['update_firmware', 'IUpdateFirmwareParams', 'UpdateFirmwareEventHandler']

logger = create_logger_with_prefix(rootlogger, 'UpdateFirmware')


async def parse_firmware_update_error(error: Optional[FirmwareUpdateErrorResponse]) -> None:
    if not error:
        return

    error_types_map = {
        FirmwareUpdateError.UNRECOGNIZED: UpdateFirmwareErrorType.UNKNOWN_ERROR,
        FirmwareUpdateError.FIRMWARE_UPDATE_ERROR_UNKNOWN: UpdateFirmwareErrorType.UNKNOWN_ERROR,
        FirmwareUpdateError.FIRMWARE_UPDATE_ERROR_VERSION_NOT_ALLOWED: UpdateFirmwareErrorType.VERSION_NOT_ALLOWED,
    }

    raise UpdateFirmwareError(error_types_map[error.error])


async def update_firmware(
    sdk: ISDK,
    params: IUpdateFirmwareParams,
) -> None:
    logger.info('Started')

    firmware = params.firmware
    version = params.version
    on_event = params.onEvent

    on_status, force_status_update = create_status_listener({
        'enums': UpdateFirmwareStatus,
        'onEvent': on_event,
        'logger': logger,
    })

    if not firmware or not version:
        logger.info('Fetching latest firmware version')

        latest_firmware = await firmware_service.get_latest({
            'prerelease': params.allowPrerelease,
            'doDownload': True,
        })

        if not latest_firmware.firmware:
            raise Exception('No downloaded firmware found')

        firmware = latest_firmware.firmware
        version = string_to_version(latest_firmware.version)

    logger.info('Updating firmware', {'version': version})

    helper = OperationHelper(sdk, 'firmwareUpdate', 'firmwareUpdate')

    if not await sdk.is_in_bootloader():
        if await sdk.is_supported():
            await sdk.check_app_compatibility(APP_VERSION)

            await helper.send_query({'initiate': {'version': version}})
            result = await helper.wait_for_result()
            await parse_firmware_update_error(result.error)
            logger.verbose('FirmwareUpdateConfirmedResponse', {'result': result})
            assert_or_throw_invalid_result(result.confirmed)
        else:
            await handle_legacy_device(sdk, version)

    force_status_update(UpdateFirmwareStatus.UPDATE_FIRMWARE_STATUS_USER_CONFIRMED)

    bootloader_sdk = await create_bootloader_sdk(
        sdk,
        params.getDevices,
        params.createConnection,
    )

    await bootloader_sdk.before_operation()
    await bootloader_sdk.send_bootloader_data(
        uint8array_to_hex(firmware),
        params.onProgress,
    )
    await bootloader_sdk.destroy()

    try:
        await wait_for_reconnection(params.getDevices, params.createConnection)
    except Exception as error:
        logger.warn('Failed to reconnect to device')
        logger.warn(error)

    logger.info('Completed')
