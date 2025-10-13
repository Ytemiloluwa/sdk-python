from typing import List
from .types import IGetLogsTestCase

withUserRejection: IGetLogsTestCase = {
    "name": "When user rejects the operation",
    "queries": [
        {
            "name": "initiate",
            "data": bytes([42, 2, 10, 0]),
        },
    ],
    "results": [
        {
            "name": "userRejection",
            "data": bytes([42, 5, 18, 3, 176, 1, 1]),
        },
    ],
    "errorInstance": "DeviceAppError",
    "errorMessage": "User rejected the operation",
}

withLogsDisabled: IGetLogsTestCase = {
    "name": "When logs are disabled",
    "queries": [
        {
            "name": "initiate",
            "data": bytes([34, 2, 10, 0]),
        },
    ],
    "results": [
        {
            "name": "logs disabled",
            "data": bytes([42, 4, 26, 2, 8, 1]),
        },
    ],
    "errorInstance": "GetLogsError",
    "errorMessage": "Logs are disabled",
}

error: List[IGetLogsTestCase] = [withUserRejection, withLogsDisabled]
