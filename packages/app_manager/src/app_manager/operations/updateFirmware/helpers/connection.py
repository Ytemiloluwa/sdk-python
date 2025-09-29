from typing import Optional
from packages.core.src.types import ISDK
from packages.core.src import sdk as core_sdk
from packages.interfaces import (
    IDeviceConnection,
    DeviceState,
    DeviceConnectionError,
    DeviceConnectionErrorType,
    IDevice,
)
from packages.util.utils import sleep
from packages.app_manager.src.utils import logger
from ..types import GetDevices, CreateDeviceConnection

MAX_WAIT_TIME_TO_ENTER_BOOTLOADER = 3_000
MAX_WAIT_TIME_TO_RECONNECT_AFTER_UPDATE = 10_000
CONNECTION_RECHECK_TIME = 200


async def wait_for_device_to_be_connected(params: dict) -> Optional[IDeviceConnection]:
    get_devices = params['getDevices']
    create_connection = params['createConnection']
    in_bootloader = params['inBootloader']
    max_tries = params['maxTries']
    recheck_time = params['recheckTime']
    dont_connect = params.get('dontConnect', False)

    tries = 0
    connection: Optional[IDeviceConnection] = None
    is_connected = False

    while tries < max_tries:
        devices = await get_devices()

        device: Optional[IDevice] = None
        for d in devices:
            if in_bootloader:
                if d.deviceState == DeviceState.BOOTLOADER:
                    device = d
                    break
            else:
                if d.deviceState != DeviceState.BOOTLOADER:
                    device = d
                    break

        if device:
            try:
                if not dont_connect:
                    connection = await create_connection(device)
                is_connected = True
            except Exception as error:
                logger.error('Error while creating connection')
                logger.error(error)

        if is_connected:
            break

        tries += 1
        await sleep(recheck_time)

    if not is_connected:
        raise DeviceConnectionError(DeviceConnectionErrorType.CONNECTION_CLOSED)

    return connection


async def create_bootloader_sdk(
    initial_sdk: ISDK,
    get_devices: GetDevices,
    create_connection: CreateDeviceConnection,
) -> ISDK:
    if await initial_sdk.is_in_bootloader():
        return initial_sdk
    
    await initial_sdk.destroy()
    logger.info('Waiting for device to enter bootloader mode')

    max_tries = (MAX_WAIT_TIME_TO_ENTER_BOOTLOADER + CONNECTION_RECHECK_TIME - 1) // CONNECTION_RECHECK_TIME

    connection = await wait_for_device_to_be_connected({
        'createConnection': create_connection,
        'getDevices': get_devices,
        'inBootloader': True,
        'maxTries': max_tries,
        'recheckTime': CONNECTION_RECHECK_TIME,
    })

    if not connection:
        raise DeviceConnectionError(DeviceConnectionErrorType.CONNECTION_CLOSED)

    return core_sdk.SDK.create(connection, 0)


async def wait_for_reconnection(
    get_devices: GetDevices,
    create_connection: CreateDeviceConnection,
) -> None:
    logger.info('Waiting for device to be reconnected after update')

    max_tries = (MAX_WAIT_TIME_TO_RECONNECT_AFTER_UPDATE + CONNECTION_RECHECK_TIME - 1) // CONNECTION_RECHECK_TIME

    await wait_for_device_to_be_connected({
        'createConnection': create_connection,
        'getDevices': get_devices,
        'inBootloader': False,
        'maxTries': max_tries,
        'recheckTime': CONNECTION_RECHECK_TIME,
        'dontConnect': True,
    })

    logger.info('Device reconnected after update')
