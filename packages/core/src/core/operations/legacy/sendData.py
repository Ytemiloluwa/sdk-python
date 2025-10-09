import asyncio
from typing import List, Optional
from interfaces.connection import IDeviceConnection
from interfaces.errors import DeviceConnectionError, DeviceConnectionErrorType, DeviceCommunicationError, DeviceCommunicationErrorType, DeviceCompatibilityError, DeviceCompatibilityErrorType
from util.utils.assert_utils import assert_condition
from util.utils.crypto import is_hex
from core.config import v1, v2
from ...utils.packetversion import PacketVersion, PacketVersionMap
from ...encoders.packet.legacy import xmodem_encode, xmodem_decode

async def write_packet(
    connection: IDeviceConnection,
    packet: bytes,
    version: PacketVersion,
    skip_packet_ids: List[str],
    ack_timeout: Optional[int] = None,
) -> None:
    usable_config = v1
    if version == PacketVersionMap.v2:
        usable_config = v2

    is_completed = False
    timeout_handle = None
    recheck_timeout_handle = None

    def clean_up():
        nonlocal is_completed
        is_completed = True
        if timeout_handle:
            timeout_handle.cancel()
        if recheck_timeout_handle:
            recheck_timeout_handle.cancel()

    async def recheck_ack():
        nonlocal recheck_timeout_handle
        if is_completed:
            return

        try:
            if not await connection.is_connected():
                clean_up()
                raise DeviceConnectionError(
                    DeviceConnectionErrorType.CONNECTION_CLOSED,
                )

            if is_completed:
                return

            pool = await connection.peek()
            for pool_item in pool:
                data = pool_item["data"]
                if pool_item["id"] in skip_packet_ids:
                    continue
                skip_packet_ids.append(pool_item["id"])

                packet_list = xmodem_decode(data, version)
                for pkt in packet_list:
                    if pkt["commandType"] == usable_config.commands.ACK_PACKET:
                        clean_up()
                        return
                    elif pkt["commandType"] == usable_config.commands.NACK_PACKET:
                        clean_up()
                        raise DeviceCommunicationError(
                            DeviceCommunicationErrorType.WRITE_ERROR,
                        )
            recheck_timeout_handle = asyncio.get_event_loop().call_later(
                usable_config.constants.RECHECK_TIME / 1000,
                lambda: asyncio.ensure_future(recheck_ack())
            )
        except Exception as error:
            clean_up()
            raise DeviceCommunicationError(
                DeviceCommunicationErrorType.UNKNOWN_COMMUNICATION_ERROR,
            ) from error

    try:
        await connection.send(packet)
        recheck_timeout_handle = asyncio.get_event_loop().call_later(
            usable_config.constants.RECHECK_TIME / 1000,
            lambda: asyncio.ensure_future(recheck_ack())
        )
    except Exception:
        clean_up()
        raise DeviceCommunicationError(
            DeviceCommunicationErrorType.WRITE_ERROR,
        )

    timeout_val = ack_timeout if ack_timeout is not None else usable_config.constants.ACK_TIME
    timeout_handle = asyncio.get_event_loop().call_later(
        timeout_val / 1000,
        lambda: clean_up() or asyncio.ensure_future(asyncio.get_event_loop().run_in_executor(None, lambda: DeviceCommunicationError(DeviceCommunicationErrorType.WRITE_TIMEOUT)))
    )

    while not is_completed:
        await asyncio.sleep(0.01)

async def send_data(
    connection: IDeviceConnection,
    command: int,
    data: str,
    version: PacketVersion,
    max_tries: Optional[int] = None,
    timeout: Optional[int] = None,
) -> None:
    assert_condition(connection, 'Invalid connection')
    assert_condition(command, 'Invalid command')
    assert_condition(data, 'Invalid data')
    assert_condition(version, 'Invalid version')
    assert_condition(command > 0, 'Command cannot be negative')
    assert_condition(is_hex(data), 'Index hex in data')
    assert_condition(max_tries is None or max_tries > 0, 'Max tries cannot be negative')

    # Check if connection is still active before proceeding
    if not await connection.is_connected():
        raise DeviceConnectionError(
            DeviceConnectionErrorType.CONNECTION_CLOSED
        )

    if version not in [PacketVersionMap.v1, PacketVersionMap.v2]:
        raise DeviceCompatibilityError(
            DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
        )

    inner_max_tries = max_tries if max_tries is not None else 5
    skip_packet_ids: List[str] = []
    packets_list = xmodem_encode(data, command, version)

    for packet in packets_list:
        # Check connection before sending each packet
        if not await connection.is_connected():
            raise DeviceConnectionError(
                DeviceConnectionErrorType.CONNECTION_CLOSED
            )
            
        tries = 1
        is_done = False
        local_max_tries = inner_max_tries
        if command == 255:
            local_max_tries = 1
        first_error: Optional[Exception] = None

        while not is_done and tries <= local_max_tries:
            try:
                await write_packet(connection, packet, version, skip_packet_ids, timeout)
                is_done = True
            except Exception as e:
                if isinstance(e, DeviceConnectionError):
                    tries = local_max_tries
                if not first_error:
                    first_error = e
            tries += 1

        if not is_done:
            if first_error:
                raise first_error
            else:
                raise DeviceCommunicationError(
                    DeviceCommunicationErrorType.WRITE_TIMEOUT,
                )


