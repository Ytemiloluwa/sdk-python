import asyncio
from typing import Optional, Dict, Any, Callable

from interfaces.errors import (
    DeviceBootloaderError,
    DeviceBootloaderErrorType,
    DeviceCommunicationError,
    DeviceCommunicationErrorType,
    DeviceConnectionError,
    DeviceConnectionErrorType,
)
from interfaces import IDeviceConnection
from util.utils import hex_to_uint8array, uint8array_to_hex, assert_condition
from ...utils.logger import logger
from ...encoders.packet.Bootloader import stm_xmodem_encode

RECHECK_TIME = 1
ACK_PACKET = "06"
RECEIVING_MODE_PACKET = "43"

ERROR_CODES = [
    {
        "code": "07",
        "error_obj": DeviceBootloaderErrorType.FIRMWARE_SIZE_LIMIT_EXCEEDED,
    },
    {
        "code": "08",
        "error_obj": DeviceBootloaderErrorType.WRONG_HARDWARE_VERSION,
    },
    {
        "code": "09",
        "error_obj": DeviceBootloaderErrorType.LOWER_FIRMWARE_VERSION,
    },
    {
        "code": "0a",
        "error_obj": DeviceBootloaderErrorType.WRONG_MAGIC_NUMBER,
    },
    {
        "code": "0b",
        "error_obj": DeviceBootloaderErrorType.SIGNATURE_NOT_VERIFIED,
    },
    {
        "code": "0c",
        "error_obj": DeviceBootloaderErrorType.FLASH_WRITE_ERROR,
    },
    {
        "code": "0d",
        "error_obj": DeviceBootloaderErrorType.FLASH_CRC_MISMATCH,
    },
    {
        "code": "0e",
        "error_obj": DeviceBootloaderErrorType.FLASH_TIMEOUT_ERROR,
    },
    {
        "code": "15",
        "error_obj": DeviceBootloaderErrorType.FLASH_NACK,
    },
]


async def write_packet(
    connection: IDeviceConnection,
    packet: bytes,
    options: Optional[Dict[str, Any]] = None,
) -> Optional[Exception]:
    if options is None:
        options = {}

    timeout_val = options.get("timeout", 2000)
    is_completed = False
    success = False
    error_result = None
    timeout_task = None
    recheck_task = None

    def cleanup():
        nonlocal is_completed, timeout_task, recheck_task
        is_completed = True
        if timeout_task and not timeout_task.done():
            timeout_task.cancel()
        if recheck_task and not recheck_task.done():
            recheck_task.cancel()

    async def recheck_packet():
        nonlocal success, error_result
        while not is_completed:
            try:
                if not await connection.is_connected():
                    cleanup()
                    return

                if is_completed:
                    return

                raw_packet = await connection.receive()
                if not raw_packet:
                    await asyncio.sleep(RECHECK_TIME / 1000)
                    continue

                e_packet_data = uint8array_to_hex(raw_packet)

                for error in ERROR_CODES:
                    if error["code"] in e_packet_data:
                        error_result = DeviceBootloaderError(error["error_obj"])
                        cleanup()
                        return

                if ACK_PACKET in e_packet_data:
                    success = True
                    cleanup()
                    return

                await asyncio.sleep(RECHECK_TIME / 1000)

            except Exception as error:
                if hasattr(error, "code") and error.code in [
                    e.value for e in DeviceConnectionErrorType
                ]:
                    cleanup()
                    return

                logger.warn(
                    "Error while rechecking packet on `writePacket`, bootloader"
                )
                logger.warn(str(error))
                await asyncio.sleep(RECHECK_TIME / 1000)

    try:
        await connection.send(packet)

        timeout_task = asyncio.create_task(asyncio.sleep(timeout_val / 1000))
        recheck_task = asyncio.create_task(recheck_packet())

        done, pending = await asyncio.wait(
            [timeout_task, recheck_task], return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel any remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Check results
        if error_result:
            return error_result
        elif success:
            return None
        else:
            # Timeout case
            cleanup()
            if not await connection.is_connected():
                raise DeviceConnectionError(DeviceConnectionErrorType.CONNECTION_CLOSED)
            else:
                raise DeviceCommunicationError(
                    DeviceCommunicationErrorType.WRITE_TIMEOUT
                )

    except Exception as err:
        cleanup()
        if not await connection.is_connected():
            raise DeviceConnectionError(DeviceConnectionErrorType.CONNECTION_CLOSED)
        raise err


async def check_if_in_receiving_mode(
    connection: IDeviceConnection, options: Optional[Dict[str, Any]] = None
) -> None:
    if options is None:
        options = {}

    timeout_val = options.get("timeout", 2000)
    is_completed = False
    success = False
    timeout_task = None
    recheck_task = None

    def cleanup():
        nonlocal is_completed, timeout_task, recheck_task
        is_completed = True
        if timeout_task and not timeout_task.done():
            timeout_task.cancel()
        if recheck_task and not recheck_task.done():
            recheck_task.cancel()

    async def recheck_packet():
        nonlocal success
        while not is_completed:
            try:
                if not await connection.is_connected():
                    cleanup()
                    return

                if is_completed:
                    return

                raw_packet = await connection.receive()
                if not raw_packet:
                    await asyncio.sleep(RECHECK_TIME / 1000)
                    continue

                e_packet_data = uint8array_to_hex(raw_packet)

                if RECEIVING_MODE_PACKET in e_packet_data:
                    success = True
                    cleanup()
                    return

                await asyncio.sleep(RECHECK_TIME / 1000)

            except Exception as error:
                if hasattr(error, "code") and error.code in [
                    e.value for e in DeviceConnectionErrorType
                ]:
                    cleanup()
                    return

                logger.warn("Error while rechecking packet on `sendBootloaderData`")
                logger.warn(str(error))
                await asyncio.sleep(RECHECK_TIME / 1000)

    timeout_task = asyncio.create_task(asyncio.sleep(timeout_val / 1000))
    recheck_task = asyncio.create_task(recheck_packet())

    done, pending = await asyncio.wait(
        [timeout_task, recheck_task], return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel any remaining tasks
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    # Check if we succeeded
    if success:
        return

    # If we get here, it means we timed out or failed
    cleanup()
    if not await connection.is_connected():
        raise DeviceConnectionError(DeviceConnectionErrorType.CONNECTION_CLOSED)
    else:
        raise DeviceBootloaderError(DeviceBootloaderErrorType.NOT_IN_RECEIVING_MODE)


async def send_bootloader_data(
    connection: IDeviceConnection,
    data: str,
    on_progress: Optional[Callable[[int], None]] = None,
    options: Optional[Dict[str, Any]] = None,
) -> None:
    if options is None:
        options = {}

    assert_condition(connection, "Invalid connection")

    packets_list = stm_xmodem_encode(data)

    await check_if_in_receiving_mode(connection, options)

    async def process_packet(packet_data: str, index: int) -> None:
        tries = 1
        inner_max_tries = options.get("max_tries", 5)
        first_error = None

        while tries <= inner_max_tries:
            try:
                timeout_option = {}
                if index == 0 or index == len(packets_list) - 1:
                    timeout_option["timeout"] = options.get("first_timeout", 10000)
                else:
                    timeout_option["timeout"] = options.get("timeout")

                error_msg = await write_packet(
                    connection, hex_to_uint8array(packet_data), timeout_option
                )

                if not error_msg:
                    if on_progress:
                        on_progress((index * 100) // len(packets_list))
                    return
                else:
                    raise error_msg

            except Exception as e:
                if hasattr(e, "code") and e.code in [
                    err.value for err in DeviceConnectionErrorType
                ]:
                    tries = inner_max_tries

                if not first_error:
                    first_error = e

                logger.warn("Error in sending bootloader data")
                logger.warn(str(e))

            tries += 1

        if first_error:
            raise first_error
        else:
            raise DeviceCommunicationError(DeviceCommunicationErrorType.WRITE_ERROR)

    for index, packet in enumerate(packets_list):
        await process_packet(packet, index)
