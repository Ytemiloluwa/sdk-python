from interfaces.errors.app_error import (
    DeviceAppError,
    DeviceAppErrorType,
    deviceAppErrorTypeDetails,
)
from .types import GetXpubsTestCase, QueryData, ResultData
from app_btc.proto.generated.btc import (
    Query,
    Result,
    GetXpubsRequest,
    GetXpubsIntiateRequest,
    GetXpubDerivationPath,
    GetXpubsResponse,
)
from app_btc.proto.generated.error import CommonError


def create_get_xpubs_error_result(common_error):
    """Create a properly structured GetXpubs error result."""
    get_xpubs_response = GetXpubsResponse()
    get_xpubs_response.common_error = common_error

    result = Result()
    result.get_xpubs = get_xpubs_response

    return result.SerializeToString()


# Common parameters shared across error test cases
common_params = {
    "params": {
        "wallet_id": bytes(
            [
                199,
                89,
                252,
                26,
                32,
                135,
                183,
                211,
                90,
                220,
                38,
                17,
                160,
                103,
                233,
                62,
                110,
                172,
                92,
                20,
                35,
                250,
                190,
                146,
                62,
                8,
                53,
                86,
                128,
                26,
                3,
                187,
                121,
                64,
            ]
        ),
        "derivation_paths": [
            {
                "path": [0x8000002C, 0x80000000, 0x80000000],
            },
        ],
    },
    "queries": [
        QueryData(
            name="Initiate query",
            data=Query(
                get_xpubs=GetXpubsRequest(
                    initiate=GetXpubsIntiateRequest(
                        wallet_id=bytes(
                            [
                                199,
                                89,
                                252,
                                26,
                                32,
                                135,
                                183,
                                211,
                                90,
                                220,
                                38,
                                17,
                                160,
                                103,
                                233,
                                62,
                                110,
                                172,
                                92,
                                20,
                                35,
                                250,
                                190,
                                146,
                                62,
                                8,
                                53,
                                86,
                                128,
                                26,
                                3,
                                187,
                                121,
                                64,
                            ]
                        ),
                        derivation_paths=[
                            GetXpubDerivationPath(
                                path=[0x8000002C, 0x80000000, 0x80000000],
                            ),
                        ],
                    )
                )
            ).SerializeToString(),
        )
    ],
}

with_unknown_error = GetXpubsTestCase(
    name="With unknown error",
    params=common_params["params"],
    queries=common_params["queries"],
    results=[
        ResultData(
            name="error",
            data=create_get_xpubs_error_result(CommonError(unknown_error=1)),
        )
    ],
    error_instance=DeviceAppError,
    error_message=deviceAppErrorTypeDetails[DeviceAppErrorType.UNKNOWN_ERROR][
        "message"
    ],
)

with_invalid_app_id = GetXpubsTestCase(
    name="With invalid msg from device",
    params=common_params["params"],
    queries=common_params["queries"],
    results=[
        ResultData(
            name="error",
            data=create_get_xpubs_error_result(CommonError(corrupt_data=1)),
        )
    ],
    error_instance=DeviceAppError,
    error_message=deviceAppErrorTypeDetails[DeviceAppErrorType.CORRUPT_DATA]["message"],
)

error_fixtures = [
    with_unknown_error,
    with_invalid_app_id,
]

__all__ = ["error_fixtures"]
