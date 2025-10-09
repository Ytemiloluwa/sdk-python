from util.utils import create_flow_status
from .types import GetXpubsTestCase, QueryData, ResultData, StatusData, MockData
from app_btc.proto.generated.btc import (
    Query, 
    Result, 
    GetXpubsRequest, 
    GetXpubsIntiateRequest, 
    GetXpubDerivationPath, 
    GetXpubsResultResponse, 
    GetXpubsResponse
)


def _create_get_xpubs_result(xpubs: list[str]) -> bytes:
    result_response = GetXpubsResultResponse()
    result_response.xpubs = xpubs
    
    get_xpubs_response = GetXpubsResponse()
    get_xpubs_response.result = result_response
    
    result = Result()
    result.get_xpubs = get_xpubs_response
    
    return result.SerializeToString()


def _create_query_data(wallet_id: bytes, derivation_paths: list[dict]) -> bytes:
    query = Query(
        get_xpubs=GetXpubsRequest(
            initiate=GetXpubsIntiateRequest(
                wallet_id=wallet_id,
                derivation_paths=[
                    GetXpubDerivationPath(path=path['path'])
                    for path in derivation_paths
                ],
            )
        )
    )
    return query.SerializeToString()


# Common wallet ID used across test cases
_COMMON_WALLET_ID = bytes([
    199, 89, 252, 26, 32, 135, 183, 211, 90, 220, 38, 17, 160, 103, 233, 62,
    110, 172, 92, 20, 35, 250, 190, 146, 62, 8, 53, 86, 128, 26, 3, 187, 121,
    64,
])

# Common xpubs used in test cases
_COMMON_XPUBS = [
    'xpub6BsXdv4PfBcemMJH8Pea913XswhLexTZQFSbRBbSaJ8jkpyi26r4qA9WALLLSYxiNRp8YiSwPqMuJGCyN6sRWRptY41SAS1Bha2u2yLvGks',
    'xpub6BsXdv4PfBceoqbjdgUr2WonPfBm7VHN64kxdzBjBvhcP7KWLRKLRM4MpvQJP5cHfJeJw5BbJNsGtnKCEdQwaZvVP4cbgb15XRS9oi4wj8J',
    'xpub6BsXdv4PfBcese3x7arVEtwB5PoLn1pdLGjNTfpY2fTDX9VBFVRRjQA76MU8GL1Xbc8HHogjzLMjpCfMnBN9qKsbvvYTCnT7f23yHbXCNPf',
    'xpub6BsXdv4PfBceujuiTDrhP3dQ3MRk7qRAdEdKhfJmvqPSqN2g9naZ79ZNxRHSSrea3eJEHpusbXMBHCnxuvFtTWqm8aJciNHgXUooXpfFd7U',
]

# Common derivation paths
_COMMON_DERIVATION_PATHS = [
    {'path': [0x80000000 + 44, 0x80000000, 0x80000000]},
    {'path': [0x80000000 + 44, 0x80000000, 0x80000000 + 1]},
    {'path': [0x80000000 + 44, 0x80000000, 0x80000000 + 2]},
    {'path': [0x80000000 + 44, 0x80000000, 0x80000000 + 3]},
]

# Common status data for all test cases
_COMMON_STATUSES = [
    StatusData(
        flow_status=create_flow_status(0, 0),
        expect_event_calls=[0],
    ),
    StatusData(
        flow_status=create_flow_status(1, 0),
        expect_event_calls=[1],
    ),
    StatusData(
        flow_status=create_flow_status(2, 1),
        expect_event_calls=[2],
    ),
]

# Common mock data
_COMMON_MOCKS = MockData(event_calls=[[0], [1], [2], [3]])


def create_request_one_xpub() -> GetXpubsTestCase:
    derivation_paths = [_COMMON_DERIVATION_PATHS[0]]
    xpubs = [_COMMON_XPUBS[0]]
    
    return GetXpubsTestCase(
        name='Request 1 xpub',
        params={
            'wallet_id': _COMMON_WALLET_ID,
            'derivation_paths': derivation_paths,
        },
        queries=[
            QueryData(
                name='Initiate query',
                data=_create_query_data(_COMMON_WALLET_ID, derivation_paths)
            )
        ],
        results=[
            ResultData(
                name='result',
                data=_create_get_xpubs_result(xpubs),
                statuses=_COMMON_STATUSES,
            )
        ],
        mocks=_COMMON_MOCKS,
        output={'xpubs': xpubs},
    )


def create_request_four_xpubs() -> GetXpubsTestCase:
    derivation_paths = _COMMON_DERIVATION_PATHS
    xpubs = _COMMON_XPUBS
    
    return GetXpubsTestCase(
        name='Request 4 xpubs',
        params={
            'wallet_id': _COMMON_WALLET_ID,
            'derivation_paths': derivation_paths,
        },
        queries=[
            QueryData(
                name='Initiate query',
                data=_create_query_data(_COMMON_WALLET_ID, derivation_paths)
            )
        ],
        results=[
            ResultData(
                name='result',
                data=_create_get_xpubs_result(xpubs),
                statuses=_COMMON_STATUSES,
            )
        ],
        mocks=_COMMON_MOCKS,
        output={'xpubs': xpubs},
    )


# Create test case instances
request_one_xpub = create_request_one_xpub()
request_four_xpubs = create_request_four_xpubs()

# Export fixtures list
valid_fixtures = [request_one_xpub, request_four_xpubs]

__all__ = ['valid_fixtures', 'create_request_one_xpub', 'create_request_four_xpubs']

