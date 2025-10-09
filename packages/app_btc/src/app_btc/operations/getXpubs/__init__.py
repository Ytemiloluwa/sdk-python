from core.types import ISDK
from util.utils import create_status_listener, create_logger_with_prefix
from util.utils.assert_utils import assert_condition
from ...proto.generated.btc import GetXpubsStatus, GetXpubsResultResponse
from ...proto.generated.common import SeedGenerationStatus
from ...utils import (
    assert_or_throw_invalid_result,
    OperationHelper,
    logger as root_logger,
    configure_app_id,
    assert_derivation_path,
)
from .types import GetXpubsEvent, GetXpubsParams

__all__ = ["get_xpubs", "GetXpubsEvent", "GetXpubsParams"]

logger = create_logger_with_prefix(root_logger, "GetXpubs")


async def get_xpubs(
    sdk: ISDK,
    params: GetXpubsParams,
) -> GetXpubsResultResponse:
    """
    Get extended public keys from device.
    Direct port of TypeScript getXpubs function.

    Args:
        sdk: SDK instance
        params: Parameters including wallet_id, derivation_paths, and optional on_event handler

    Returns:
        Result containing list of xpubs

    Raises:
        AssertionError: If parameters are invalid
    """
    assert_condition(params, "Params should be defined")
    assert_condition(params.derivation_paths, "DerivationPaths should be defined")
    assert_condition(params.wallet_id, "WalletId should be defined")
    assert_condition(
        len(params.derivation_paths) > 0,
        "DerivationPaths should not be empty",
    )
    assert_condition(
        all(len(path["path"]) == 3 for path in params.derivation_paths),
        "DerivationPaths should be of depth 3",
    )

    for item in params.derivation_paths:
        assert_derivation_path(item["path"])

    await configure_app_id(
        sdk,
        [path["path"] for path in params.derivation_paths],
    )

    status_listener = create_status_listener(
        {
            "enums": GetXpubsEvent,
            "operationEnums": GetXpubsStatus,
            "seedGenerationEnums": SeedGenerationStatus,
            "onEvent": params.on_event,
            "logger": logger,
        }
    )
    on_status = status_listener["onStatus"]
    force_status_update = status_listener["forceStatusUpdate"]

    helper = OperationHelper(
        sdk=sdk,
        query_key="getXpubs",
        result_key="getXpubs",
        on_status=on_status,
    )

    await helper.send_query(
        {
            "initiate": {
                "wallet_id": params.wallet_id,
                "derivation_paths": params.derivation_paths,
            }
        }
    )

    result = await helper.wait_for_result()

    assert_or_throw_invalid_result(result.result)

    force_status_update(GetXpubsEvent.PIN_CARD)

    return GetXpubsResultResponse(xpubs=result.result.xpubs)
