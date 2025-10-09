from typing import List, Dict, Any, Optional, TypedDict


class IGetDeviceInfoTestCase(TypedDict, total=False):
    name: str
    query: bytes
    result: bytes
    output: Optional[Dict[str, Any]]
    error_instance: Optional[Any]
    error_message: Optional[str]


class IFixtures(TypedDict):
    valid: List[IGetDeviceInfoTestCase]
    invalid_data: List[IGetDeviceInfoTestCase]
    error: List[IGetDeviceInfoTestCase]
