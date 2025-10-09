import asyncio
from typing import List, Dict, Any
from interfaces.connection import IDeviceConnection
from interfaces.errors import (
    DeviceConnectionError,
    DeviceConnectionErrorType,
    DeviceCommunicationError,
    DeviceCommunicationErrorType,
    DeviceCompatibilityError,
    DeviceCompatibilityErrorType,
)
from util.utils.assert_utils import assert_condition
from ...utils.packetversion import PacketVersion, PacketVersionMap
from ...encoders.packet.legacy import xmodem_decode, LegacyDecodedPacketData
from core.config import v1 as config_v1

DEFAULT_RECEIVE_TIMEOUT = 15000


async def receive_data(
    connection: IDeviceConnection,
    all_acceptable_commands: List[int],
    version: PacketVersion,
    timeout: int = DEFAULT_RECEIVE_TIMEOUT,
) -> Dict[str, Any]:
    assert_condition(connection, "Invalid connection")
    assert_condition(all_acceptable_commands, "Invalid allAcceptableCommands")
    assert_condition(version, "Invalid version")

    if version not in [PacketVersionMap.v1, PacketVersionMap.v2]:
        raise DeviceCompatibilityError(
            DeviceCompatibilityErrorType.INVALID_SDK_OPERATION
        )

    assert_condition(
        len(all_acceptable_commands) > 0, "allAcceptableCommands should not be empty"
    )

    if not await connection.is_connected():
        raise DeviceConnectionError(DeviceConnectionErrorType.CONNECTION_CLOSED)

    res_data: Dict[int, str] = {}
    future = asyncio.get_event_loop().create_future()
    is_completed = False

    def clean_up():
        nonlocal is_completed
        is_completed = True
        if not future.done():
            future.cancel()

    def process_packet(packet: LegacyDecodedPacketData) -> bool:
        command_type = packet["commandType"]
        current_packet_number = packet["currentPacketNumber"]
        total_packet = packet["totalPacket"]
        data_chunk = packet["dataChunk"]

        if command_type in all_acceptable_commands:
            res_data[current_packet_number] = data_chunk
            if len(res_data) == total_packet:
                data = "".join(res_data[i] for i in range(1, total_packet + 1))
                if not future.done():
                    future.set_result({"commandType": command_type, "data": data})
                return True
        return False

    async def recheck_packet():
        nonlocal is_completed
        try:
            while not is_completed and not future.done():
                if not await connection.is_connected():
                    if not future.done():
                        future.set_exception(
                            DeviceConnectionError(
                                DeviceConnectionErrorType.CONNECTION_CLOSED
                            )
                        )
                    return

                data = await connection.receive()
                if not data:
                    await asyncio.sleep(config_v1.constants.RECHECK_TIME / 1000)
                    continue

                packet_list = xmodem_decode(data, version)
                for packet in packet_list:
                    if process_packet(packet):
                        return

                await asyncio.sleep(config_v1.constants.RECHECK_TIME / 1000)

        except Exception as error:
            if not future.done():
                future.set_exception(
                    DeviceCommunicationError(
                        DeviceCommunicationErrorType.UNKNOWN_COMMUNICATION_ERROR
                    )
                )

    async def timeout_watchdog():
        await asyncio.sleep(timeout / 1000)
        if not future.done():
            future.set_exception(
                DeviceCommunicationError(DeviceCommunicationErrorType.READ_TIMEOUT)
            )

    # Launch recheck and timeout concurrently
    tasks = [
        asyncio.create_task(recheck_packet()),
        asyncio.create_task(timeout_watchdog()),
    ]

    try:
        result = await future
        return result
    finally:
        for t in tasks:
            t.cancel()
        clean_up()
