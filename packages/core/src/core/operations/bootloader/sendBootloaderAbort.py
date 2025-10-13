import asyncio
from typing import Optional, Dict, Any
from interfaces.errors import (
    DeviceCommunicationError,
    DeviceCommunicationErrorType,
    DeviceConnectionError,
    DeviceConnectionErrorType,
)
from interfaces import IDeviceConnection
from util.utils.crypto import (
    hex_to_uint8array,
    uint8array_to_hex,
    assert_condition,
)
from core.config import v1
from ..helpers.can_retry import can_retry

ACK_PACKET = "18"


async def send_bootloader_abort(
    connection: IDeviceConnection, options: Optional[Dict[str, Any]] = None
) -> None:
    if options is None:
        options = {}

    timeout = options.get("timeout", 2000)  # Default timeout
    first_timeout = options.get("first_timeout", 2000)  # Default first timeout
    max_tries = options.get("max_tries", 5)

    assert_condition(connection, "Invalid connection")

    # Check if connection is still active before proceeding
    if not await connection.is_connected():
        raise DeviceConnectionError(DeviceConnectionErrorType.CONNECTION_CLOSED)

    packets_list = ["41"]
    data_list = [hex_to_uint8array(packet) for packet in packets_list]

    for index, data in enumerate(data_list):
        tries = 1
        inner_max_tries = max_tries
        first_error = None
        success = False

        while tries <= inner_max_tries:
            try:
                await write_packet(
                    connection=connection,
                    data=data,
                    timeout=first_timeout if index == 0 else timeout,
                    recheck_time=v1.constants.RECHECK_TIME,
                )
                success = True
                break  # Success
            except Exception as e:
                if not can_retry(e):
                    tries = inner_max_tries
                if not first_error:
                    first_error = e
                tries += 1

        # Only raise error if we didn't succeed
        if not success:
            if first_error:
                raise first_error
            else:
                raise DeviceCommunicationError(DeviceCommunicationErrorType.WRITE_ERROR)


async def write_packet(
    connection: IDeviceConnection,
    data: bytes,
    timeout: Optional[int] = 2000,
    recheck_time: int = 500,  # in milliseconds
) -> None:
    if timeout is None:
        timeout = 2000

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
                    await asyncio.sleep(recheck_time / 1000)
                    continue

                e_packet_data = uint8array_to_hex(raw_packet)

                if ACK_PACKET in e_packet_data:
                    success = True
                    cleanup()
                    return

                await asyncio.sleep(recheck_time / 1000)

            except Exception as error:
                if hasattr(error, "code") and error.code in [
                    e.value for e in DeviceConnectionErrorType
                ]:
                    cleanup()
                    return
                await asyncio.sleep(recheck_time / 1000)

    try:
        await connection.send(data)

        timeout_task = asyncio.create_task(asyncio.sleep(timeout / 1000))
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

        # If we get here, it means we timed out
        cleanup()
        if not await connection.is_connected():
            raise DeviceConnectionError(DeviceConnectionErrorType.CONNECTION_CLOSED)
        else:
            raise DeviceCommunicationError(DeviceCommunicationErrorType.WRITE_TIMEOUT)

    except Exception as err:
        cleanup()
        if not await connection.is_connected():
            raise DeviceConnectionError(DeviceConnectionErrorType.CONNECTION_CLOSED)
        raise err
