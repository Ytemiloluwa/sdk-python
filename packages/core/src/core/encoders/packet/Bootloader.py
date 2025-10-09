from typing import TypedDict
from util.utils.assert_utils import assert_condition
from util.utils import crc16, hex_to_uint8array, int_to_uint_byte, is_hex, uint8array_to_hex
from ...utils.packetversion import PacketVersionMap
from ...utils.crypto import byte_unstuffing
from core.config.radix import v1 as radix


START_OF_FRAME = '01'
END_OF_TRANSMISSION = '04'
CHUNK_SIZE = 256

class StmPacket(TypedDict):
    startOfFrame: str
    commandType: int
    currentPacketNumber: int
    totalPacket: int
    dataSize: int
    dataChunk: str
    crc: str
    errorList: str

def stm_xmodem_encode(data: str) -> list[str]:
    assert_condition(data, 'Invalid data')
    hex_data = data
    if hex_data.startswith('0x'):
        hex_data = hex_data[2:]
    assert_condition(bool(hex_data), 'Data cannot be empty')
    assert_condition(is_hex(hex_data), f'Invalid hex: {data}')

    rounds = (len(hex_data) + CHUNK_SIZE - 1) // CHUNK_SIZE
    packet_list: list[str] = []

    for i in range(1, rounds + 1):
        current_packet_number = int_to_uint_byte(i % 255, 8)
        packet_number_xor = int_to_uint_byte(i % 255 ^ 255, 8)
        data_chunk_slice = hex_data[(i - 1) * CHUNK_SIZE : i * CHUNK_SIZE]
        data_chunk = data_chunk_slice
        if len(data_chunk_slice) < CHUNK_SIZE:
            for _ in range(CHUNK_SIZE - len(data_chunk_slice)):
                data_chunk += 'f'

        comm_data = START_OF_FRAME + current_packet_number + packet_number_xor + data_chunk
        crc = int_to_uint_byte(crc16(hex_to_uint8array(data_chunk)), 16)
        packet = comm_data + crc
        packet_list.append(packet)

    packet_list.append(END_OF_TRANSMISSION)
    return packet_list

def stm_xmodem_decode(param: bytes) -> list[StmPacket]:
    data = uint8array_to_hex(param).upper()
    packet_list: list[StmPacket] = []
    offset = data.find(START_OF_FRAME)

    while len(data) > 0:
        start_of_frame = data[offset : offset + 2]
        offset += 2
        command_type = int(data[offset : offset + radix.command_type // 4], 16)
        offset += radix.command_type // 4
        data_size = int(data[offset : offset + radix.data_size // 4], 16)
        offset += radix.data_size // 4
        stuffed_data = data[offset : offset + data_size * 2]
        data = data[offset + data_size * 2 :]

        un_stuffed_data = byte_unstuffing(
            hex_to_uint8array(stuffed_data),
            PacketVersionMap.v1,
        )
        offset = 0
        current_packet_number = un_stuffed_data[
            offset : offset + radix.current_packet_number // 4
        ]
        offset += radix.current_packet_number // 4
        total_packet = un_stuffed_data[
            offset : offset + radix.total_packet // 4
        ]
        offset += radix.total_packet // 4
        data_chunk = un_stuffed_data[
            offset : len(un_stuffed_data) - 6 * 2
        ]
        offset += len(un_stuffed_data) - 6 * 2
        crc = un_stuffed_data[offset : offset + radix.crc // 4]
        crc_input = un_stuffed_data[0 : len(un_stuffed_data) - radix.crc // 4]
        actual_crc = (
            hex(crc16(hex_to_uint8array(crc_input)))
            .replace("0x", "")
            .zfill(4)
        )

        error_list = ''
        if start_of_frame.upper() != 'AA':
            error_list += ' Invalid Start of frame '
        if int(current_packet_number, 16) > int(total_packet, 16):
            error_list += ' currentPacketNumber is greater than totalPacketNumber '
        if data_size > CHUNK_SIZE:
            error_list += ' invalid data size '
        if actual_crc != crc:
            error_list += ' invalid crc '

        packet_list.append(
            StmPacket(
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



