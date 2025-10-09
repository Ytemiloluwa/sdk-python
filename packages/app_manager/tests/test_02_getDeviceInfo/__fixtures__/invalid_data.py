from typing import List
from interfaces.errors.app_error import DeviceAppError
from .types import IGetDeviceInfoTestCase

invalid_data: List[IGetDeviceInfoTestCase] = [
    {
        "name": "Invalid data",
        "query": bytes([10, 2, 10, 0]),
        "result": bytes([2, 8, 1, 24, 1, 34, 8, 8, 12, 18, 4, 8, 1, 24, 26]),
        "error_instance": DeviceAppError,
    },
    {
        "name": "Invalid data",
        "query": bytes([10, 2, 10, 0]),
        "result": bytes(
            [
                10,
                34,
                10,
                3,
                90,
                221,
                135,
                18,
                2,
                8,
                1,
                24,
                1,
                34,
                11,
                8,
                2,
                18,
                7,
                8,
            ]
        ),
        "error_instance": DeviceAppError,
    },
    {
        "name": "Invalid data",
        "query": bytes([10, 2, 10, 0]),
        "result": bytes([10]),
        "error_instance": DeviceAppError,
    },
    {
        "name": "Invalid data",
        "query": bytes([10, 2, 10, 0]),
        "result": bytes([]),
        "error_instance": DeviceAppError,
    },
]
