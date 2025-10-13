from typing import List, Any, Optional, Union
from dataclasses import dataclass
from app_btc.operations.signTxn.types import SignTxnParams, SignTxnResult


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
class SignTxnTestCase:
    name: str
    params: Optional[SignTxnParams]
    queries: List[QueryData]
    results: List[ResultData]
    mocks: Optional[MockData] = None
    output: Optional[SignTxnResult] = None
    error_instance: Optional[type] = None
    error_message: Optional[Union[str, Any]] = None


@dataclass
class Fixtures:
    valid: List[SignTxnTestCase]
    invalid_data: List[SignTxnTestCase]
    error: List[SignTxnTestCase]
    invalid_args: List[SignTxnTestCase]


__all__ = [
    "QueryData",
    "StatusData",
    "ResultData",
    "MockData",
    "SignTxnTestCase",
    "Fixtures",
]
