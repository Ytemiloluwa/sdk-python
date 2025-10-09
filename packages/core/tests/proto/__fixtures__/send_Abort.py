from datetime import datetime
from interfaces.errors.communication_error import DeviceCommunicationError
from interfaces.errors.app_error import DeviceAppError

# Constant date for mocking Date.now() in tests
constant_date = datetime(2023, 3, 7, 9, 43, 48, 755000)

# Send abort test fixtures
fixtures = {
    "invalid_args": [
        {
            "sequence_number": 123423,
        }
    ],
    "valid": [
        {
            "name": "CmdSeq: 18",
            "packets": [
                bytes([
                    85, 85, 135, 124, 0, 1, 0, 1, 0, 18, 8, 1, 0, 17, 254, 0,
                ]),
                bytes([
                    85, 85, 169, 56, 0, 1, 0, 1, 255, 255, 1, 1, 0, 17, 254, 0,
                ])
            ],
            "ack_packets": [
                [
                    bytes([
                        85, 85, 28, 162, 0, 1, 0, 1, 255, 255, 4, 1, 0, 17, 254, 15, 0, 11,
                        0, 0, 8, 2, 16, 3, 32, 18, 40, 7, 48, 132, 1,
                    ])
                ],
                [
                    bytes([
                        85, 85, 30, 138, 0, 1, 0, 1, 255, 255, 4, 1, 1, 112, 220, 12, 0, 8,
                        0, 0, 8, 1, 16, 1, 32, 1, 40, 7,
                    ])
                ]
            ],
            "sequence_number": 18,
            "status": {
                "device_idle_state": 3,
                "device_waiting_on": 2,
                "abort_disabled": False,
                "current_cmd_seq": 18,
                "cmd_state": 7,
                "flow_status": 132,
            }
        },
        {
            "name": "CmdSeq: 78",
            "packets": [
                bytes([
                    85, 85, 63, 128, 0, 1, 0, 1, 0, 78, 8, 1, 0, 17, 254, 0,
                ]),
                bytes([
                    85, 85, 169, 56, 0, 1, 0, 1, 255, 255, 1, 1, 0, 17, 254, 0,
                ])
            ],
            "ack_packets": [
                [
                    bytes([
                        170, 63, 27, 0, 2, 0, 2, 10, 16, 97, 6, 47, 150, 92, 178, 86, 238,
                        68, 168, 147, 34, 27, 233, 174, 197, 213, 124, 255, 32, 26,
                    ]),
                    bytes([170, 1, 6, 0, 0, 0, 0, 0]),
                    bytes([
                        85, 85, 154, 161, 0, 1, 0, 1, 0, 78, 4, 1, 0, 17, 254, 13, 0, 9, 0,
                        0, 16, 3, 32, 78, 40, 1, 48, 164, 1,
                    ])
                ],
                [
                    bytes([
                        85, 85, 30, 138, 0, 1, 0, 1, 255, 255, 4, 1, 1, 112, 220, 12, 0, 8,
                        0, 0, 8, 1, 16, 1, 32, 1, 40, 7,
                    ])
                ]
            ],
            "sequence_number": 78,
            "status": {
                "device_idle_state": 3,
                "device_waiting_on": 0,
                "abort_disabled": False,
                "current_cmd_seq": 78,
                "cmd_state": 1,
                "flow_status": 164,
            }
        }
    ],
    "error": [
        {
            "name": "Invalid CRC",
            "packets": [
                bytes([
                    85, 85, 135, 124, 0, 1, 0, 1, 0, 18, 8, 1, 0, 17, 254, 0,
                ])
            ],
            "ack_packets": [
                [
                    bytes([
                        85, 85, 200, 162, 0, 1, 0, 1, 255, 255, 4, 1, 0, 17, 254, 15, 0, 11,
                        0, 0, 8, 2, 16, 3, 32, 18, 40, 7, 48, 132, 1,
                    ])
                ]
            ],
            "sequence_number": 18,
            "error_instance": DeviceCommunicationError
        },
        {
            "name": "Invalid sequenceNumber",
            "packets": [
                bytes([
                    85, 85, 63, 128, 0, 1, 0, 1, 0, 78, 8, 1, 0, 17, 254, 0,
                ])
            ],
            "ack_packets": [
                [
                    bytes([
                        170, 63, 27, 0, 2, 0, 2, 10, 16, 97, 6, 47, 150, 92, 178, 86, 238,
                        68, 168, 147, 34, 27, 233, 174, 197, 213, 124, 255, 32, 26,
                    ]),
                    bytes([170, 1, 6, 0, 0, 0, 0, 0]),
                    bytes([
                        85, 85, 28, 162, 0, 1, 0, 1, 255, 255, 4, 1, 0, 17, 254, 15, 0, 11,
                        0, 0, 8, 2, 16, 3, 32, 18, 40, 7, 48, 132, 1,
                    ])
                ]
            ],
            "error_instance": DeviceAppError,
            "sequence_number": 78
        }
    ]
}
