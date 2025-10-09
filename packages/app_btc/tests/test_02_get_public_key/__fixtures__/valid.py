from util.utils import create_flow_status
from .types import GetPublicKeyTestCase, QueryData, ResultData, StatusData, MockData
from app_btc.proto.generated.btc import Query, GetPublicKeyRequest, GetPublicKeyIntiateRequest

request_address = GetPublicKeyTestCase(
    name='Request Address',
    params={
        'wallet_id': bytes([
            199, 89, 252, 26, 32, 135, 183, 211, 90, 220, 38, 17, 160, 103, 233, 62,
            110, 172, 92, 20, 35, 250, 190, 146, 62, 8, 53, 86, 128, 26, 3, 187, 121,
            64,
        ]),
        'derivation_path': [0x80000000 + 44, 0x80000000, 0x80000000, 0, 0],
    },
    queries=[
        QueryData(
            name='Initiate query',
            data=Query(
                get_public_key=GetPublicKeyRequest(
                    initiate=GetPublicKeyIntiateRequest(
                        wallet_id=bytes([
                            199, 89, 252, 26, 32, 135, 183, 211, 90, 220, 38, 17, 160,
                            103, 233, 62, 110, 172, 92, 20, 35, 250, 190, 146, 62, 8, 53,
                            86, 128, 26, 3, 187, 121, 64,
                        ]),
                        derivation_path=[0x80000000 + 44, 0x80000000, 0x80000000, 0, 0],
                    )
                )
            ).SerializeToString()
        )
    ],
    results=[
        ResultData(
            name='result',
            data=bytes([
                10, 37, 10, 35, 10, 33, 2, 189, 157, 191, 154, 193, 155, 2, 138, 82,
                57, 142, 71, 103, 29, 184, 233, 203, 158, 111, 1, 240, 55, 168, 209,
                3, 189, 5, 195, 30, 25, 250, 238,
            ]),
            statuses=[
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
            ],
        )
    ],
    mocks=MockData(event_calls=[[0], [1], [2], [3], [4]]),
    output={
        'public_key': bytes([
            2, 189, 157, 191, 154, 193, 155, 2, 138, 82, 57, 142, 71, 103, 29, 184,
            233, 203, 158, 111, 1, 240, 55, 168, 209, 3, 189, 5, 195, 30, 25, 250, 238,
        ]),
        'address': '1AN4L3cNXoY61hoXHNngbNszmrjtKFm9Vk',
    },
)

valid_fixtures = [request_address]

__all__ = ['valid_fixtures']
