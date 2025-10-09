from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType, deviceAppErrorTypeDetails
from .types import SignTxnTestCase, QueryData, ResultData
from app_btc.proto.generated.btc import Query, Result, SignTxnRequest, SignTxnInitiateRequest, SignTxnResponse
from app_btc.proto.generated import error
from app_btc.proto.generated.error import DataFlow, UserRejection

common_params = {
    'params': {
        'wallet_id': bytes([
            199, 89, 252, 26, 32, 135, 183, 211, 90, 220, 38, 17, 160, 103, 233, 62,
            110, 172, 92, 20, 35, 250, 190, 146, 62, 8, 53, 86, 128, 26, 3, 187, 121,
            64,
        ]),
        'derivation_path': [0x80000000 + 44, 0x80000000, 0x80000000],
        'txn': {
            'inputs': [
                {
                    'prev_index': 1,
                    'prev_txn_id': 'd92fa216748b164b2bf104594f7ceb6f9ee7ad39d0c9e16bca86ea72df5591a9',
                    'prev_txn': '0200000000010211f852bd83a5ba61877026abda944b419d05c4768df7005a8b8f6cae14e4a57f2600000000fffffffff1ba6c76c0e31ef0b3cbf605d89b523c5bef16a58ec4cfb2550f49a4108aff4f0100000000ffffffff02cda4130000000000160014826979058429649e3160783f8c03c480f98329bb8b8236000000000017a9143291522f1cd6699e8a076a7618da8fa0d68c40e98702483045022100f25f539965a10312dd6657d21c43872618fbab3a2bc6a665192735e5e19b080c022038a8e186621abc01a90e735d50e967e1485f12793a8c10e8ea4a56dc5dca619b0121034ee63fbc1dd72c317179ae76597bd28e8b3fca1c6238760f8fc9bcc1a6b0630802483045022100a5094498a19913bbf1bb9ca129d700b771d637f1cfd46ff419ac0188ad6376c50220346f23f281990f1aaf833c406f23f8439f561a11657310a97a371ee6191c020401210235ec79fc08cf43f6e470e8526ba70c0e92eb65d917f266210eb5a2b4e9eb942400000000',
                    'value': '3572363',
                    'address': 'bc1qgjr28pdztqd6ueh52eah8ttk4nvtx7l65husa9',
                    'change_index': 0,
                    'address_index': 10,
                    'sequence': 0xffffffff,
                },
            ],
            'outputs': [
                {
                    'value': '3547271',
                    'address': 'bc1qn9u8mha55t7s2qmy9f02y92sywnq53mr4504sk',
                    'is_change': False,
                },
            ],
        },
    },
    'queries': [
        QueryData(
            name='Initiate query',
            data=Query(
                sign_txn=SignTxnRequest(
                    initiate=SignTxnInitiateRequest(
                        wallet_id=bytes([
                            199, 89, 252, 26, 32, 135, 183, 211, 90, 220, 38, 17, 160,
                            103, 233, 62, 110, 172, 92, 20, 35, 250, 190, 146, 62, 8, 53,
                            86, 128, 26, 3, 187, 121, 64,
                        ]),
                        derivation_path=[0x80000000 + 44, 0x80000000, 0x80000000],
                    )
                )
            ).SerializeToString()
        )
    ],
}

with_unknown_error = SignTxnTestCase(
    name='With unknown error',
    params=common_params['params'],
    queries=common_params['queries'],
    results=[
        ResultData(
            name='error',
            data=Result(
                sign_txn=SignTxnResponse(
                    common_error=error.CommonError(
                        unknown_error=1
                    )
                )
            ).SerializeToString()
        )
    ],
    error_instance=DeviceAppError,
    error_message=deviceAppErrorTypeDetails[DeviceAppErrorType.UNKNOWN_ERROR]['message'],
)

with_invalid_app_id = SignTxnTestCase(
    name='With invalid msg from device',
    params=common_params['params'],
    queries=common_params['queries'],
    results=[
        ResultData(
            name='error',
            data=Result(
                common_error=error.CommonError(
                    corrupt_data=DataFlow.DATA_FLOW_INVALID_DATA
                )
            ).SerializeToString()
        )
    ],
    error_instance=DeviceAppError,
    error_message=deviceAppErrorTypeDetails[DeviceAppErrorType.CORRUPT_DATA]['message'],
)

with_user_rejection = SignTxnTestCase(
    name='With user rejection',
    params=common_params['params'],
    queries=common_params['queries'],
    results=[
        ResultData(
            name='error',
            data=Result(
                sign_txn=SignTxnResponse(
                    common_error=error.CommonError(
                        user_rejection=UserRejection.USER_REJECTION_UNKNOWN
                    )
                )
            ).SerializeToString()
        )
    ],
    error_instance=DeviceAppError,
    error_message=deviceAppErrorTypeDetails[DeviceAppErrorType.USER_REJECTION]['message'],
)

error_fixtures = [
    with_unknown_error,
    with_invalid_app_id,
    with_user_rejection,
]

__all__ = ['error_fixtures']
