from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType, deviceAppErrorTypeDetails
from .types import GetXpubsTestCase, QueryData, ResultData
from app_btc.proto.generated.btc import Query, GetXpubsRequest, GetXpubsIntiateRequest, GetXpubDerivationPath

# Common parameters for invalid data tests
common_params = {
    'params': {
        'wallet_id': bytes([
            199, 89, 252, 26, 32, 135, 183, 211, 90, 220, 38, 17, 160, 103, 233, 62,
            110, 172, 92, 20, 35, 250, 190, 146, 62, 8, 53, 86, 128, 26, 3, 187, 121,
            64,
        ]),
        'derivation_paths': [
            {
                'path': [0x8000002c, 0x80000000, 0x80000000],
            },
        ],
    },
    'queries': [
        QueryData(
            name='Initiate query',
            data=Query(
                get_xpubs=GetXpubsRequest(
                    initiate=GetXpubsIntiateRequest(
                        wallet_id=bytes([
                            199, 89, 252, 26, 32, 135, 183, 211, 90, 220, 38, 17, 160,
                            103, 233, 62, 110, 172, 92, 20, 35, 250, 190, 146, 62, 8, 53,
                            86, 128, 26, 3, 187, 121, 64,
                        ]),
                        derivation_paths=[
                            GetXpubDerivationPath(
                                path=[0x8000002c, 0x80000000, 0x80000000],
                            ),
                        ],
                    )
                )
            ).SerializeToString()
        )
    ],
    'error_instance': DeviceAppError,
    'error_message': deviceAppErrorTypeDetails[DeviceAppErrorType.INVALID_MSG_FROM_DEVICE]['message'],
}

invalid_data_fixtures = [
    GetXpubsTestCase(
        name='Invalid data',
        results=[
            ResultData(
                name='error',
                data=bytes([
                    109, 112, 102, 98, 72, 57, 117, 109, 75, 69, 83, 117, 117, 49, 103,
                    78, 100, 105, 87, 83, 116, 106, 71, 54, 67, 110, 104, 77, 86, 49, 113,
                    97, 78, 111, 50, 98, 118, 52, 67, 113, 72, 122, 120, 85, 98, 53, 86,
                    68, 115, 86, 52, 77, 86, 112, 83, 70, 86, 78, 121, 121, 109, 83, 112,
                    98, 74, 76, 55, 57, 75, 89, 86, 57, 75, 56, 88, 82, 100, 105, 98, 70,
                    109, 118, 54, 116, 86, 54, 116, 50, 122, 52, 100, 87, 110, 111, 110,
                    78, 52, 78, 77, 89, 109,
                ])
            )
        ],
        **common_params
    ),
    GetXpubsTestCase(
        name='Invalid data',
        results=[
            ResultData(
                name='error',
                data=bytes([
                    18, 34, 10, 3, 90, 221, 135, 18, 2, 8, 1, 24, 1, 34, 11, 8, 2, 18, 7,
                    8,
                ])
            )
        ],
        **common_params
    ),
    GetXpubsTestCase(
        name='Invalid data',
        results=[
            ResultData(
                name='error',
                data=bytes([18])
            )
        ],
        **common_params
    ),
    GetXpubsTestCase(
        name='Invalid data',
        results=[
            ResultData(
                name='error',
                data=bytes([])
            )
        ],
        **common_params
    ),
]

__all__ = ['invalid_data_fixtures']

