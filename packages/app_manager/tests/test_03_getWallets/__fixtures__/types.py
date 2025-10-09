from typing import List, Dict, Any, Optional, TypedDict


class IGetWalletsTestCase(TypedDict, total=False):
    name: str
    query: bytes
    result: bytes
    output: Optional[Dict[str, Any]]
    error_instance: Optional[Any]
    error_message: Optional[str]


class IFixtures(TypedDict):
    valid: List[IGetWalletsTestCase]
    error: List[IGetWalletsTestCase]
    invalid_data: List[IGetWalletsTestCase]
