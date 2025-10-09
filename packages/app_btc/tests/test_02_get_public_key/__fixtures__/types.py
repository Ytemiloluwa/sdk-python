from typing import List, Any, Optional, Union
from dataclasses import dataclass
from app_btc.operations.getPublicKey.types import GetPublicKeyParams, GetPublicKeyResult


@dataclass
class QueryData:
    name: str
    data: bytes


@dataclass 
class StatusData:
    flow_status: int
    expect_event_calls: Optional[List[int]] = None


@dataclass
class ResultData:
    name: str
    data: bytes
    statuses: Optional[List[StatusData]] = None


@dataclass
class MockData:
    event_calls: Optional[List[List[int]]] = None


@dataclass
class GetPublicKeyTestCase:
    name: str
    params: Optional[GetPublicKeyParams]
    queries: List[QueryData]
    results: List[ResultData]
    mocks: Optional[MockData] = None
    output: Optional[GetPublicKeyResult] = None
    error_instance: Optional[type] = None
    error_message: Optional[Union[str, Any]] = None  # Can be string or regex pattern


@dataclass
class Fixtures:
    valid: List[GetPublicKeyTestCase]
    invalid_data: List[GetPublicKeyTestCase]
    error: List[GetPublicKeyTestCase]
    invalid_args: List[GetPublicKeyTestCase]


__all__ = [
    'QueryData',
    'StatusData', 
    'ResultData',
    'MockData',
    'GetPublicKeyTestCase',
    'Fixtures',
]


