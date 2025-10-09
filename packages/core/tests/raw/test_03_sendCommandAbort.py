import pytest
from unittest.mock import patch
import calendar

from core import SDK
from tests.raw.__fixtures__.sendCommandAbort import raw_send_abort_test_cases
from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.errors.connection_error import DeviceConnectionError
from tests.__fixtures__.config import config


@pytest.fixture
async def setup():
    """Setup fixture for each test"""
    constant_date = raw_send_abort_test_cases["constantDate"]

    with (
        patch(
            "time.time",
            return_value=calendar.timegm(constant_date.timetuple())
            + constant_date.microsecond / 1e6,
        ),
        patch("os.times", return_value=type("MockTimes", (), {"elapsed": 16778725})()),
    ):

        connection = await MockDeviceConnection.create()

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

        sdk = await SDK.create(connection, 0)
        await sdk.before_operation()

        connection.remove_listeners()

        yield connection, sdk

        await connection.destroy()


@pytest.mark.asyncio
async def test_should_be_able_to_send_abort(setup):
    connection, sdk = await setup.__anext__()

    for test_case in raw_send_abort_test_cases["valid"]:

        async def on_data(data: bytes):
            print(f"🔍 on_data called with packet: {data.hex()}")
            from core.encoders.packet.packet import (
                decode_packet,
                decode_payload_data,
                encode_packet,
            )
            from core.config import v3 as config_v3

            decoded_packet = decode_packet(data, "v3")
            if decoded_packet:
                seq_num = decoded_packet[0]["sequence_number"]
                print(f"🔍 Decoded packet sequence: {seq_num}")

                original_response = test_case["ackPackets"][0]
                decoded_response = decode_packet(original_response, "v3")
                if decoded_response:
                    original_payload = decoded_response[0]["payload_data"]
                    payload_data = decode_payload_data(original_payload, "v3")

                    # Generate correct response packet
                    response_packet = encode_packet(
                        raw_data=payload_data["raw_data"],
                        proto_data=payload_data["protobuf_data"],
                        version="v3",
                        sequence_number=seq_num,
                        packet_type=config_v3.commands.PACKET_TYPE.STATUS,
                    )[0]
                    print(f"🔍 Sending response packet: {response_packet.hex()}")
                    await connection.mock_device_send(response_packet)
                else:
                    seq_hex = f"{seq_num:02x}"
                    response_packet = encode_packet(
                        raw_data=f"130000{seq_hex}00",
                        proto_data="",
                        version="v3",
                        sequence_number=seq_num,
                        packet_type=config_v3.commands.PACKET_TYPE.STATUS,
                    )[0]
                    print(
                        f"🔍 Sending fallback response packet: {response_packet.hex()}"
                    )
                    await connection.mock_device_send(response_packet)
            else:
                print(f"❌ Failed to decode incoming packet")

        connection.configure_listeners(on_data)
        status = await sdk.deprecated.send_command_abort(
            test_case["sequenceNumber"],
            1,
            config.defaultTimeout,
        )

        assert status == test_case["status"]


@pytest.mark.asyncio
async def test_should_throw_error_when_device_is_disconnected(setup):
    connection, sdk = await setup.__anext__()

    for test_case in raw_send_abort_test_cases["valid"]:

        async def on_data(data: bytes):
            print(f"🔍 on_data called with packet: {data.hex()}")
            from core.encoders.packet.packet import (
                decode_packet,
                decode_payload_data,
                encode_packet,
            )
            from core.config import v3 as config_v3

            decoded_packet = decode_packet(data, "v3")
            if decoded_packet:
                seq_num = decoded_packet[0]["sequence_number"]
                print(f"🔍 Decoded packet sequence: {seq_num}")

                original_response = test_case["ackPackets"][0]
                decoded_response = decode_packet(original_response, "v3")
                if decoded_response:
                    original_payload = decoded_response[0]["payload_data"]
                    payload_data = decode_payload_data(original_payload, "v3")

                    # Generate correct response packet
                    response_packet = encode_packet(
                        raw_data=payload_data["raw_data"],
                        proto_data=payload_data["protobuf_data"],
                        version="v3",
                        sequence_number=seq_num,
                        packet_type=config_v3.commands.PACKET_TYPE.STATUS,
                    )[0]
                    print(f"🔍 Sending response packet: {response_packet.hex()}")
                    await connection.mock_device_send(response_packet)
                    await connection.destroy()
            else:
                print(f" Failed to decode incoming packet")

        connection.configure_listeners(on_data)
        with pytest.raises(DeviceConnectionError):
            await sdk.deprecated.send_command_abort(
                test_case["sequenceNumber"],
                1,
                config.defaultTimeout,
            )


@pytest.mark.asyncio
async def test_should_throw_error_when_device_is_disconnected_in_between(setup):
    connection, sdk = await setup.__anext__()

    for test_case in raw_send_abort_test_cases["valid"]:

        async def on_data(data: bytes):
            print(f"🔍 on_data called with packet: {data.hex()}")
            from core.encoders.packet.packet import (
                decode_packet,
                decode_payload_data,
                encode_packet,
            )
            from core.config import v3 as config_v3

            decoded_packet = decode_packet(data, "v3")
            if decoded_packet:
                seq_num = decoded_packet[0]["sequence_number"]
                print(f"🔍 Decoded packet sequence: {seq_num}")

                original_response = test_case["ackPackets"][0]
                decoded_response = decode_packet(original_response, "v3")
                if decoded_response:
                    original_payload = decoded_response[0]["payload_data"]
                    payload_data = decode_payload_data(original_payload, "v3")

                    # Generate correct response packet
                    response_packet = encode_packet(
                        raw_data=payload_data["raw_data"],
                        proto_data=payload_data["protobuf_data"],
                        version="v3",
                        sequence_number=seq_num,
                        packet_type=config_v3.commands.PACKET_TYPE.STATUS,
                    )[0]
                    print(f"🔍 Sending response packet: {response_packet.hex()}")
                    await connection.mock_device_send(response_packet)
                    await connection.destroy()
            else:
                print(f" Failed to decode incoming packet")

        connection.configure_listeners(on_data)
        with pytest.raises(DeviceConnectionError):
            await sdk.deprecated.send_command_abort(
                test_case["sequenceNumber"],
                1,
                config.defaultTimeout,
            )
