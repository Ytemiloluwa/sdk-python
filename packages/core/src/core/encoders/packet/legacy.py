from typing import TypedDict, List
from packages.core.src import config
from packages.util.utils.assert_utils import assert_condition
from packages.util.utils import is_hex, uint8array_to_hex, hex_to_uint8array, int_to_uint_byte, crc16, pad_start
from packages.core.src.utils.packetversion import PacketVersion, PacketVersionMap
from packages.core.src.utils.crypto import byte_unstuffing, byte_stuffing
from packages.interfaces.errors import DeviceCompatibilityError, DeviceCompatibilityErrorType

class LegacyDecodedPacketData(TypedDict):
    startOfFrame: str
    commandType: int
    currentPacketNumber: int
    totalPacket: int
    dataSize: int
    dataChunk: str
    crc: str
    errorList: List[str]

def xmodem_encode(
    data: str,
    command_type: int,
    version: PacketVersion,
) -> List[bytes]:
    assert_condition(data, 'Invalid data')
    assert_condition(len(data) > 0, 'data cannot be empty')
    assert_condition(command_type, 'Invalid commandType')
    assert_condition(version, 'Invalid version')
    assert_condition(is_hex(data), 'Invalid hex data')
    assert_condition(command_type >= 0, 'Command type should not be negative')

    if version not in [PacketVersionMap.v1, PacketVersionMap.v2]:
        raise DeviceCompatibilityError(
            DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
        )

    usable_config = config.v1
    if version == PacketVersionMap.v2:
        usable_config = config.v2

    chunk_size = usable_config.constants.CHUNK_SIZE
    start_of_frame = usable_config.constants.START_OF_FRAME

    rounds = (len(data) + chunk_size - 1) // chunk_size
    packet_list: List[bytes] = []

    for i in range(1, rounds + 1):
        current_packet_number = int_to_uint_byte(
            i,
            usable_config.radix.current_packet_number,
        )
        total_packet = int_to_uint_byte(rounds, usable_config.radix.total_packet)
        data_chunk = data[
            (i - 1) * chunk_size : (i - 1) * chunk_size + chunk_size
        ]
        comm_data = current_packet_number + total_packet + data_chunk
        crc = int_to_uint_byte(crc16(hex_to_uint8array(comm_data)), 16)
        stuffed_data = byte_stuffing(hex_to_uint8array(comm_data + crc), version)
        comm_header = (
            start_of_frame
            + int_to_uint_byte(command_type, usable_config.radix.command_type)
            + int_to_uint_byte(len(stuffed_data) // 2, usable_config.radix.data_size)
        )
        packet = comm_header + stuffed_data
        packet_list.append(hex_to_uint8array(packet))

    return packet_list

def xmodem_decode(
    packet_data: bytes,
    version: PacketVersion,
) -> List[LegacyDecodedPacketData]:
    assert_condition(packet_data, 'Invalid packetData')
    assert_condition(version, 'Invalid version')

    if version not in [PacketVersionMap.v1, PacketVersionMap.v2]:
        raise DeviceCompatibilityError(
            DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
        )

    usable_config = config.v1
    if version == PacketVersionMap.v2:
        usable_config = config.v2

    chunk_size = usable_config.constants.CHUNK_SIZE
    start_of_frame = usable_config.constants.START_OF_FRAME

    data = uint8array_to_hex(packet_data).upper()
    packet_list: List[LegacyDecodedPacketData] = []
    offset = data.find(start_of_frame)

    while len(data) > 0:
        offset = data.find(start_of_frame)
        if offset == -1:
            return packet_list

        start_of_frame = data[offset : offset + len(start_of_frame)]
        offset += len(start_of_frame)

        command_type = int(
            data[offset : offset + usable_config.radix.command_type // 4],
            16,
        )
        offset += usable_config.radix.command_type // 4

        data_size = int(
            data[offset : offset + usable_config.radix.data_size // 4],
            16,
        )
        offset += usable_config.radix.data_size // 4

        stuffed_data = data[offset : offset + data_size * 2]
        data = data[offset + data_size * 2 :]

        un_stuffed_data = byte_unstuffing(hex_to_uint8array(stuffed_data), version)
        offset = 0

        current_packet_number = un_stuffed_data[
            offset : offset + usable_config.radix.current_packet_number // 4
        ]
        offset += usable_config.radix.current_packet_number // 4

        total_packet = un_stuffed_data[
            offset : offset + usable_config.radix.total_packet // 4
        ]
        offset += usable_config.radix.total_packet // 4

        data_chunk = un_stuffed_data[
            offset : len(un_stuffed_data) - usable_config.radix.crc // 4
        ]
        offset += len(un_stuffed_data) - usable_config.radix.crc // 4

        crc = un_stuffed_data[
            offset : offset + usable_config.radix.crc // 4
        ]
        crc_input = un_stuffed_data[
            0 : len(un_stuffed_data) - usable_config.radix.crc // 4
        ]
        actual_crc = pad_start(
            hex(crc16(hex_to_uint8array(crc_input))).replace('0x', ''),
            4,
            '0',
        )

        error_list = []
        if start_of_frame.upper() != start_of_frame:
            error_list.append('Invalid Start of frame')
        if int(current_packet_number, 16) > int(total_packet, 16):
            error_list.append('currentPacketNumber is greater than totalPacketNumber')
        if data_size > chunk_size:
            error_list.append('invalid data size')
        if actual_crc != crc:
            error_list.append('invalid crc')

        packet_list.append(
            LegacyDecodedPacketData(
                startOfFrame=start_of_frame,
                commandType=command_type,
                currentPacketNumber=int(current_packet_number, 16),
                totalPacket=int(total_packet, 16),
                dataSize=data_size,
                dataChunk=data_chunk,
                crc=crc,
                errorList=error_list,
            )
        )
    return packet_list

def create_ack_packet(
    command_type: int,
    packet_number: str,
    version: PacketVersion,
) -> str:
    assert_condition(command_type, 'Invalid commandType')
    assert_condition(packet_number, 'Invalid packetNumber')
    assert_condition(version, 'Invalid version')
    assert_condition(command_type >= 0, 'Command type cannot be negative')

    if version not in [PacketVersionMap.v1, PacketVersionMap.v2]:
        raise DeviceCompatibilityError(
            DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
        )

    usable_config = config.v1
    if version == PacketVersionMap.v2:
        usable_config = config.v2

    start_of_frame = usable_config.constants.START_OF_FRAME

    current_packet_number = int_to_uint_byte(
        int(packet_number),
        usable_config.radix.current_packet_number,
    )
    total_packet = int_to_uint_byte(0, usable_config.radix.total_packet)
    data_chunk = '00000000'
    comm_data = current_packet_number + total_packet + data_chunk
    crc = pad_start(hex(crc16(hex_to_uint8array(comm_data))).replace('0x', ''), 4, '0')
    temp = comm_data + crc
    stuffed_data = byte_stuffing(hex_to_uint8array(temp), version)
    comm_header = (
        start_of_frame
        + int_to_uint_byte(command_type, usable_config.radix.command_type)
        + int_to_uint_byte(len(stuffed_data) // 2, usable_config.radix.data_size)
    )
    return (comm_header + stuffed_data).lower()



