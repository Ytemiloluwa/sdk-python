from packages.core.src.types import ISDK
from packages.util.utils import create_status_listener, create_logger_with_prefix
from packages.util.utils.assert_utils import assert_condition
from packages.interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType
from packages.app_btc.src.proto.generated.btc import GetPublicKeyStatus
from packages.app_btc.src.proto.generated.common import SeedGenerationStatus
from packages.app_btc.src.utils import (
    assert_or_throw_invalid_result,
    OperationHelper,
    logger as root_logger,
    configure_app_id,
    assert_derivation_path,
)
from .types import (
    GetPublicKeyEvent,
    GetPublicKeyParams,
    GetPublicKeyResult,
)
from .publicKeyToAddress import get_address_from_public_key

__all__ = ['get_public_key', 'GetPublicKeyEvent', 'GetPublicKeyParams', 'GetPublicKeyResult']

logger = create_logger_with_prefix(root_logger, 'GetPublicKey')


async def get_public_key(
    sdk: ISDK,
    params: GetPublicKeyParams,
) -> GetPublicKeyResult:
    """
    Get public key and address from device.
    Direct port of TypeScript getPublicKey function.
    
    Args:
        sdk: SDK instance
        params: Parameters including wallet_id, derivation_path, and optional on_event handler
        
    Returns:
        Result containing public_key and address
        
    Raises:
        AssertionError: If parameters are invalid
    """
    assert_condition(params, 'Params should be defined')
    assert_condition(params.derivation_path, 'DerivationPath should be defined')
    assert_condition(params.wallet_id, 'WalletId should be defined')
    assert_condition(
        len(params.derivation_path) == 5,
        'DerivationPath should be of depth 5',
    )
    assert_derivation_path(params.derivation_path)

    await configure_app_id(sdk, [params.derivation_path])

    status_listener = create_status_listener({
        'enums': GetPublicKeyEvent,
        'operationEnums': GetPublicKeyStatus,
        'seedGenerationEnums': SeedGenerationStatus,
        'onEvent': params.on_event,
        'logger': logger,
    })
    on_status = status_listener['onStatus']
    force_status_update = status_listener['forceStatusUpdate']

    helper = OperationHelper(
        sdk=sdk,
        query_key='getPublicKey',
        result_key='get_public_key',
        on_status=on_status,
    )

    await helper.send_query({
        'initiate': {
            'wallet_id': params.wallet_id,
            'derivation_path': params.derivation_path,
        }
    })

    result = await helper.wait_for_result()
    assert_or_throw_invalid_result(result.result)

    force_status_update(GetPublicKeyEvent.VERIFY)
    
    if not result.result.public_key or len(result.result.public_key) == 0:
        raise DeviceAppError(DeviceAppErrorType.INVALID_MSG_FROM_DEVICE)

    address = get_address_from_public_key(
        result.result.public_key,
        params.derivation_path,
    )

    return {
        'public_key': result.result.public_key,
        'address': address,
    }
