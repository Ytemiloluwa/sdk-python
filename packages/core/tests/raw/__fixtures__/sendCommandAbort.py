from datetime import datetime
from interfaces.errors.communication_error import DeviceCommunicationError
from interfaces.errors.app_error import DeviceAppError

raw_send_abort_test_cases = {
    "constantDate": datetime(2023, 3, 7, 9, 43, 48, 755000),
    "invalidArgs": [
        {
            "sequenceNumber": None,
        },
        {
            "sequenceNumber": None,
        },
        {
            "sequenceNumber": 123423,
        },
    ],
    "valid": [
        {
            "name": "CmdSeq: 18",
            "abortRequest": bytes([
                85, 85, 135, 124, 0, 1, 0, 1, 0, 18, 8, 1, 0, 17, 254, 0,
            ]),
            "ackPackets": [
                bytes([
                    85, 85, 143, 73, 0, 1, 0, 1, 0, 18, 4, 1, 0, 18, 86, 11, 0, 0, 0, 4,
                    35, 0, 0, 18, 4, 0, 132,
                ]),
            ],
            "sequenceNumber": 18,
            "status": {
                "deviceState": "23",
                "deviceIdleState": 3,
                "deviceWaitingOn": 2,
                "abortDisabled": False,
                "currentCmdSeq": 18,
                "cmdState": 0,
                "flowStatus": 0,
                "isStatus": True,
            },
        },
        {
            "name": "CmdSeq: 78",
            "abortRequest": bytes([
                85, 85, 63, 128, 0, 1, 0, 1, 0, 78, 8, 1, 0, 17, 254, 0,
            ]),
            "ackPackets": [
                bytes([
                    170, 63, 27, 0, 2, 0, 2, 10, 16, 97, 6, 47, 150, 92, 178, 86, 238, 68,
                    168, 147, 34, 27, 233, 174, 197, 213, 124, 255, 32, 26,
                ]),
                bytes([170, 1, 6, 0, 0, 0, 0, 0]),
                bytes([
                    85, 85, 75, 43, 0, 1, 0, 1, 0, 78, 4, 1, 0, 18, 90, 11, 0, 0, 0, 4, 3,
                    0, 0, 78, 1, 0, 164,
                ]),
            ],
            "sequenceNumber": 78,
            "status": {
                "deviceState": "13",
                "deviceIdleState": 3,
                "deviceWaitingOn": 1,
                "abortDisabled": False,
                "currentCmdSeq": 78,
                "cmdState": 0,
                "flowStatus": 0,
                "isStatus": True,
            },
        },
    ],
    "error": [
        {
            "name": "Invalid CRC",
            "abortRequest": bytes([
                85, 85, 135, 124, 0, 1, 0, 1, 0, 18, 8, 1, 0, 17, 254, 0,
            ]),
            "ackPackets": [
                bytes([
                    85, 85, 100, 73, 0, 1, 0, 1, 0, 18, 4, 1, 0, 18, 86, 11, 0, 0, 0, 4,
                    35, 0, 0, 18, 4, 0, 132,
                ]),
            ],
            "sequenceNumber": 18,
            "errorInstance": DeviceCommunicationError,
        },
        {
            "name": "Invalid sequenceNumber",
            "abortRequest": bytes([
                85, 85, 63, 128, 0, 1, 0, 1, 0, 78, 8, 1, 0, 17, 254, 0,
            ]),
            "ackPackets": [
                bytes([
                    170, 63, 27, 0, 2, 0, 2, 10, 16, 97, 6, 47, 150, 92, 178, 86, 238, 68,
                    168, 147, 34, 27, 233, 174, 197, 213, 124, 255, 32, 26,
                ]),
                bytes([170, 1, 6, 0, 0, 0, 0, 0]),
                bytes([
                    85, 85, 143, 73, 0, 1, 0, 1, 0, 18, 4, 1, 0, 18, 86, 11, 0, 0, 0, 4,
                    35, 0, 0, 18, 4, 0, 132,
                ]),
            ],
            "errorInstance": DeviceAppError,
            "sequenceNumber": 78,
        },
    ],
}

__all__ = ['raw_send_abort_test_cases']