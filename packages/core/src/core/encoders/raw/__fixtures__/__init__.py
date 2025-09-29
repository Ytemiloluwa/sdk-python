from packages.core.src.utils.packetversion import PacketVersionMap

# Raw data test cases for valid encodings
raw_data_test_cases = {
    "valid_encodings": [
        {
            "raw_data": {
                "commandType": 1,
                "data": "",
                "isRawData": True,
                "isStatus": False,
            },
            "encoded": "00000001",
        },
        {
            "raw_data": {
                "commandType": 53,
                "data": "3b986b12c84e96ee4d20e8dd9835b14b1767c09dd3eb24c203c1",
                "isRawData": True,
                "isStatus": False,
            },
            "encoded": "000000353b986b12c84e96ee4d20e8dd9835b14b1767c09dd3eb24c203c1",
        },
        {
            "raw_data": {
                "commandType": 213,
                "data": "d70a9bb4b65fd5b0b838a26092cd3886816c1586a7d8fb6e177b83258a39bb86714775390f5a4ba4d428fecc9ecfb65f5c08cd07ee9a3bc95f1ae7d72526a3c65debf711b9c5ccf380a69e7086bfa77a6c378fed71639888f2610fb44f5ee45ea207862e01578d629ac3cb4efb2a262c78c4d65d1c3578b97514789618d84beef1c2bd34396d7c5b6eb42bb054cee9d78da362cdaf43b5d7a9e799889733e596f2ef",
                "isRawData": True,
                "isStatus": False,
            },
            "encoded": "000000d5d70a9bb4b65fd5b0b838a26092cd3886816c1586a7d8fb6e177b83258a39bb86714775390f5a4ba4d428fecc9ecfb65f5c08cd07ee9a3bc95f1ae7d72526a3c65debf711b9c5ccf380a69e7086bfa77a6c378fed71639888f2610fb44f5ee45ea207862e01578d629ac3cb4efb2a262c78c4d65d1c3578b97514789618d84beef1c2bd34396d7c5b6eb42bb054cee9d78da362cdaf43b5d7a9e799889733e596f2ef",
        },
    ],
}

# Encode raw data test cases for invalid scenarios
encode_raw_data_test_cases = {
    "invalid": [
        {
            "raw_data": {
                "commandType": 1,
                "data": "",
            },
            "version": PacketVersionMap.v1,
        },
        {
            "raw_data": {
                "commandType": 1,
                "data": "",
            },
            "version": PacketVersionMap.v2,
        },
        {
            "raw_data": {
                "commandType": 1,
                "data": "",
            },
            "version": "invalid",
        },
        {
            "raw_data": None,
            "version": PacketVersionMap.v3,
        },
        {
            "raw_data": {
                "commandType": 1,
                "data": "",
            },
            "version": None,
        },
        {
            "raw_data": None,
            "version": PacketVersionMap.v3,
        },
        {
            "raw_data": {
                "commandType": 1,
                "data": "",
            },
            "version": None,
        },
        {
            "raw_data": {
                "commandType": None,
                "data": "",
            },
            "version": PacketVersionMap.v3,
        },
        {
            "raw_data": {
                "commandType": 1,
                "data": None,
            },
            "version": PacketVersionMap.v3,
        },
        {
            "raw_data": {
                "commandType": None,
                "data": "",
            },
            "version": PacketVersionMap.v3,
        },
        {
            "raw_data": {
                "commandType": 1,
                "data": None,
            },
            "version": PacketVersionMap.v3,
        },
        {
            "raw_data": {
                "commandType": -1,
                "data": "",
            },
            "version": PacketVersionMap.v3,
        },
        {
            "raw_data": {
                "commandType": 9999999999,
                "data": "",
            },
            "version": PacketVersionMap.v3,
        },
    ],
}

# Decode raw data test cases for invalid scenarios
decode_raw_data_test_cases = {
    "invalid": [
        {
            "payload": "",
            "version": PacketVersionMap.v1,
        },
        {
            "payload": "",
            "version": PacketVersionMap.v2,
        },
        {
            "payload": "",
            "version": "invalid",
        },
        {
            "payload": None,
            "version": PacketVersionMap.v3,
        },
        {
            "payload": "",
            "version": None,
        },
        {
            "payload": None,
            "version": PacketVersionMap.v3,
        },
        {
            "payload": "",
            "version": None,
        },
        {
            "payload": "5818f605bc3531741s",
            "version": PacketVersionMap.v3,
        },
        {
            "payload": "0x12s",
            "version": PacketVersionMap.v3,
        },
    ],
}

# Decode status test cases
decode_status_test_cases = {
    "valid_encodings": [
        {
            "encoded": "",
            "status": {
                "deviceState": "0",
                "deviceIdleState": 0,
                "deviceWaitingOn": 0,
                "abortDisabled": False,
                "currentCmdSeq": 0,
                "cmdState": 0,
                "flowStatus": 0,
                "isStatus": True,
            },
        },
        {
            "encoded": "01010002010004",
            "status": {
                "deviceState": "1",
                "deviceIdleState": 1,
                "deviceWaitingOn": 0,
                "abortDisabled": True,
                "currentCmdSeq": 2,
                "cmdState": 1,
                "flowStatus": 4,
                "isStatus": True,
            },
        },
        {
            "encoded": "03000f020100a4",
            "status": {
                "deviceState": "3",
                "deviceIdleState": 3,
                "deviceWaitingOn": 0,
                "abortDisabled": False,
                "currentCmdSeq": 3842,
                "cmdState": 1,
                "flowStatus": 164,
                "isStatus": True,
            },
        },
        {
            "encoded": "23000032070084",
            "status": {
                "deviceState": "23",
                "deviceIdleState": 3,
                "deviceWaitingOn": 2,
                "abortDisabled": False,
                "currentCmdSeq": 50,
                "cmdState": 7,
                "flowStatus": 132,
                "isStatus": True,
            },
        },
    ],
    "invalid": [
        {
            "payload": "",
            "version": PacketVersionMap.v1,
        },
        {
            "payload": "",
            "version": PacketVersionMap.v2,
        },
        {
            "payload": "",
            "version": "invalid",
        },
        {
            "payload": None,
            "version": PacketVersionMap.v3,
        },
        {
            "payload": "",
            "version": None,
        },
        {
            "payload": None,
            "version": PacketVersionMap.v3,
        },
        {
            "payload": "",
            "version": None,
        },
        {
            "payload": "5818f605bc3531741s",
            "version": PacketVersionMap.v3,
        },
        {
            "payload": "0x12s",
            "version": PacketVersionMap.v3,
        },
    ],
}

__all__ = [
    "raw_data_test_cases",
    "encode_raw_data_test_cases",
    "decode_raw_data_test_cases",
    "decode_status_test_cases",
]


