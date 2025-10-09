from typing import List, Any, Optional, Union
from dataclasses import dataclass
from app_btc.operations.getXpubs.types import GetXpubsParams, GetXpubsEvent


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
class GetXpubsTestCase:
    name: str
    params: Optional[GetXpubsParams]
    queries: List[QueryData]
    results: List[ResultData]
    mocks: Optional[MockData] = None
    output: Optional[GetXpubsEvent] = None
    error_instance: Optional[type] = None
    error_message: Optional[Union[str, Any]] = None  # Can be string or regex pattern


@dataclass
class Fixtures:
    valid: List[GetXpubsTestCase]
    invalid_data: List[GetXpubsTestCase]
    error: List[GetXpubsTestCase]
    invalid_args: List[GetXpubsTestCase]


__all__ = [
    'QueryData',
    'StatusData', 
    'ResultData',
    'MockData',
    'GetXpubsTestCase',
    'Fixtures',
]


