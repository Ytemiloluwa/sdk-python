"""High-fidelity Pythonic port of TypeScript invalidArgs.ts fixtures."""

import re
from .types import GetXpubsTestCase, QueryData, ResultData

# Common parameters shared across all invalid argument test cases
common_params = {
    'queries': [QueryData(name='empty', data=bytes([]))],
    'results': [ResultData(name='empty', data=bytes([]))],
    'error_instance': Exception,
    'error_message': re.compile(r'AssertionError'),
}

invalid_args_fixtures = [
    GetXpubsTestCase(
        name='Null',
        params=None,
        **common_params
    ),
    GetXpubsTestCase(
        name='Undefined', 
        params=None,
        **common_params
    ),
    GetXpubsTestCase(
        name='Empty Object',
        params={},
        **common_params
    ),
    GetXpubsTestCase(
        name='No derivation paths',
        params={'wallet_id': bytes([])},
        **common_params
    ),
    GetXpubsTestCase(
        name='No wallet id',
        params={
            'derivation_paths': [
                {
                    'path': [0x80000000 + 44, 0x80000000, 0x80000000],
                },
            ],
        },
        **common_params
    ),
    GetXpubsTestCase(
        name='Empty derivation path',
        params={
            'wallet_id': bytes([10]),
            'derivation_paths': [],
        },
        **common_params
    ),
    GetXpubsTestCase(
        name='invalid derivation path in array (depth:2)',
        params={
            'wallet_id': bytes([10]),
            'derivation_paths': [
                {
                    'path': [0x80000000 + 44, 0x80000000],
                },
            ],
        },
        **common_params
    ),
    GetXpubsTestCase(
        name='invalid derivation path in array (depth:4)',
        params={
            'wallet_id': bytes([10]),
            'derivation_paths': [
                {
                    'path': [0x80000000 + 44, 0x80000000, 0x80000000, 0x80000000],
                },
            ],
        },
        **common_params
    ),
]

__all__ = ['invalid_args_fixtures']

