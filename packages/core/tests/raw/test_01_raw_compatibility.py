import pytest
from unittest.mock import patch
from datetime import datetime
import calendar
from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.connection import DeviceState
from interfaces.errors.bootloader_error import (
    DeviceBootloaderError,
    DeviceBootloaderErrorType,
    deviceBootloaderErrorTypeDetails,
)
from interfaces.errors.compatibility_error import (
    DeviceCompatibilityError,
    DeviceCompatibilityErrorType,
    deviceCompatibilityErrorTypeDetails,
)
from core import SDK
from core.utils.packetversion import PacketVersionMap
from core.deprecated import DeprecatedCommunication


@pytest.fixture
async def setup():
    constant_date = datetime(2023, 3, 7, 9, 43, 48, 755000)
    with (
        patch(
            "time.time",
            return_value=calendar.timegm(constant_date.timetuple())
            + constant_date.microsecond / 1e6,
        ),
        patch(
            "core.encoders.packet.packet.time.time",
            return_value=calendar.timegm(constant_date.timetuple())
            + constant_date.microsecond / 1e6,
        ),
        patch("os.times", return_value=type("MockTimes", (), {"elapsed": 16778725})()),
    ):

        connection = await MockDeviceConnection.create()
        applet_id = 0

        async def on_data():
            # SDK Version: 2.7.1, Packet Version: v3
            await connection.mock_device_send(
                bytes(
                    [
                        170,
                        1,
                        7,
                        0,
                        1,
                        0,
                        1,
                        0,
                        69,
                        133,
                        170,
                        88,
                        12,
                        0,
                        1,
                        0,
                        1,
                        0,
                        2,
                        0,
                        7,
                        0,
                        1,
                        130,
                        112,
                    ]
                )
            )

        connection.configure_listeners(on_data)

        sdk = await SDK.create(connection, applet_id)

        if sdk.deprecated is None:
            sdk.deprecated = DeprecatedCommunication(sdk)

        sdk.get_version = lambda: "2.7.1"
        sdk.get_packet_version = lambda: PacketVersionMap.v3
        sdk.get_connection = lambda: connection
        sdk.get_device_state = lambda: DeviceState.MAIN
        sdk.is_in_bootloader = lambda: False

        async def async_get_device_state():
            return DeviceState.MAIN

        async def async_is_in_bootloader():
            return False

        async def async_is_supported():
            return False

        sdk.get_device_state = async_get_device_state
        sdk.is_in_bootloader = async_is_in_bootloader
        sdk.is_supported = async_is_supported

        await connection.before_operation()
        await sdk.before_operation()

        connection.remove_listeners()

        yield connection, sdk

        await connection.destroy()


@pytest.mark.asyncio
async def test_should_have_the_right_sdk_version_and_packet_version(setup):
    connection, sdk = await setup.__anext__()
    assert sdk.get_version() == "2.7.1"
    assert sdk.get_packet_version() == PacketVersionMap.v3
    assert await sdk.deprecated.is_raw_operation_supported() is True


@pytest.mark.asyncio
async def test_should_be_able_to_get_status(setup):
    connection, sdk = await setup.__anext__()

    async def on_data(data: bytes):
        # Import necessary functions for dynamic packet generation
        from core.encoders.packet.packet import (
            encode_packet,
            decode_packet,
            decode_payload_data,
        )
        from core.config import v3 as config_v3

        decoded_packet = decode_packet(data, "v3")
        if decoded_packet:
            seq_num = decoded_packet[0]["sequence_number"]

            original_response = bytes(
                [
                    85,
                    85,
                    193,
                    143,
                    0,
                    1,
                    0,
                    1,
                    255,
                    255,
                    4,
                    1,
                    0,
                    18,
                    8,
                    11,
                    0,
                    0,
                    0,
                    4,
                    35,
                    0,
                    0,
                    50,
                    4,
                    0,
                    132,
                ]
            )

            # Decode the original response to extract its payload
            decoded_response = decode_packet(original_response, "v3")
            if decoded_response:
                original_payload = decoded_response[0]["payload_data"]

                # Extract the actual payload data (raw_data and proto_data)
                payload_data = decode_payload_data(original_payload, "v3")

                status_packet = encode_packet(
                    raw_data=payload_data["raw_data"],
                    proto_data=payload_data["protobuf_data"],
                    version="v3",
                    sequence_number=seq_num,
                    packet_type=config_v3.commands.PACKET_TYPE.STATUS,
                )[
                    0
                ]  # Take first packet from list

                await connection.mock_device_send(status_packet)

    connection.configure_listeners(on_data)

    status = await sdk.deprecated.get_command_status()
    assert isinstance(status, dict)
    assert status.get("isStatus") is True


@pytest.mark.asyncio
async def test_should_be_able_to_send_command(setup):
    connection, sdk = await setup.__anext__()

    async def on_data(data: bytes):
        assert data == bytes(
            [
                85,
                85,
                70,
                22,
                0,
                1,
                0,
                1,
                0,
                16,
                2,
                1,
                0,
                17,
                254,
                24,
                0,
                0,
                0,
                20,
                0,
                0,
                0,
                12,
                98,
                110,
                1,
                88,
                234,
                189,
                103,
                120,
                176,
                24,
                231,
                183,
                92,
                134,
                213,
                11,
            ]
        )
        await connection.mock_device_send(
            bytes(
                [
                    85,
                    85,
                    233,
                    246,
                    0,
                    1,
                    0,
                    1,
                    0,
                    16,
                    5,
                    1,
                    0,
                    5,
                    229,
                    0,
                ]
            )
        )

    connection.configure_listeners(on_data)
    await connection.before_operation()

    await sdk.deprecated.send_command(
        {
            "data": "626e0158eabd6778b018e7b75c86d50b",
            "commandType": 12,
            "sequenceNumber": 16,
            "maxTries": 1,
        }
    )


@pytest.mark.asyncio
async def test_should_throw_error_when_accessing_functions_for_v1(setup):
    connection, sdk = await setup.__anext__()

    invalid_sdk_operation_message = deviceCompatibilityErrorTypeDetails[
        DeviceCompatibilityErrorType.INVALID_SDK_OPERATION
    ]["message"]

    with pytest.raises(DeviceCompatibilityError) as exc_info:
        await sdk.deprecated.send_legacy_command(1, "00")
    assert invalid_sdk_operation_message in str(exc_info.value)

    with pytest.raises(DeviceCompatibilityError) as exc_info:
        await sdk.deprecated.receive_legacy_command([1], 500)
    assert invalid_sdk_operation_message in str(exc_info.value)


@pytest.mark.asyncio
async def test_should_throw_error_when_accessing_functions_for_proto(setup):
    connection, sdk = await setup.__anext__()

    invalid_sdk_operation_message = deviceCompatibilityErrorTypeDetails[
        DeviceCompatibilityErrorType.INVALID_SDK_OPERATION
    ]["message"]

    with pytest.raises(DeviceCompatibilityError) as exc_info:
        await sdk.send_query(bytes([10]))
    assert invalid_sdk_operation_message in str(exc_info.value)

    with pytest.raises(DeviceCompatibilityError) as exc_info:
        await sdk.get_result()
    assert invalid_sdk_operation_message in str(exc_info.value)

    with pytest.raises(DeviceCompatibilityError) as exc_info:
        await sdk.wait_for_result()
    assert invalid_sdk_operation_message in str(exc_info.value)

    with pytest.raises(DeviceCompatibilityError) as exc_info:
        await sdk.get_status()
    assert invalid_sdk_operation_message in str(exc_info.value)

    with pytest.raises(DeviceCompatibilityError) as exc_info:
        await sdk.send_abort()
    assert invalid_sdk_operation_message in str(exc_info.value)


@pytest.mark.asyncio
async def test_should_throw_error_when_accessing_bootloader_functions(setup):
    connection, sdk = await setup.__anext__()

    not_in_bootloader_error = deviceBootloaderErrorTypeDetails[
        DeviceBootloaderErrorType.NOT_IN_BOOTLOADER
    ]["message"]

    with pytest.raises(DeviceBootloaderError) as exc_info:
        await sdk.send_bootloader_abort()
    assert not_in_bootloader_error in str(exc_info.value)

    with pytest.raises(DeviceBootloaderError) as exc_info:
        await sdk.send_bootloader_data("12")
    assert not_in_bootloader_error in str(exc_info.value)
