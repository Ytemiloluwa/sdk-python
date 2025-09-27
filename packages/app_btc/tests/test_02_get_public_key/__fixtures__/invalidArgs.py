import re
from .types import GetPublicKeyTestCase, QueryData, ResultData

# Common parameters for invalid argument tests - matches TypeScript exactly
common_params = {
    'queries': [QueryData(name='empty', data=bytes([]))],
    'results': [ResultData(name='empty', data=bytes([]))],
    'error_instance': Exception,  # TypeScript uses Error, Python equivalent is Exception
    'error_message': re.compile(r'AssertionError|Params should be defined|missing.*required.*argument|DerivationPath should be of depth'),  # Match various error messages
}

invalid_args_fixtures = [
    GetPublicKeyTestCase(
        name='Null',
        params=None,
        **common_params
    ),
    GetPublicKeyTestCase(
        name='Undefined', 
        params=None,
        **common_params
    ),
    GetPublicKeyTestCase(
        name='Empty Object',
        params={},
        **common_params
    ),
    GetPublicKeyTestCase(
        name='No derivation path',
        params={'wallet_id': bytes([])},
        **common_params
    ),
    GetPublicKeyTestCase(
        name='No wallet id',
        params={
            'derivation_path': [0x80000000 + 44, 0x80000000, 0x80000000, 0, 0],
        },
        **common_params
    ),
    GetPublicKeyTestCase(
        name='Invalid derivation path',
        params={
            'wallet_id': bytes([10]),
            'derivation_path': [0, 0, 0],
        },
        **common_params
    ),
]

__all__ = ['invalid_args_fixtures']

