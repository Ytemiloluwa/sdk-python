from typing import List
from packages.core.src.sdk import ISDK
from packages.core.src.types import IFeatureSupport
from packages.util.utils.assert_utils import assert_condition
from packages.app_btc.src.constants.appId import APP_VERSION, coin_index_to_app_id_map


def get_app_id_from_derivation_paths(derivation_paths: List[List[int]]) -> int:
    """
    Get app ID from derivation paths by checking coin indexes.
    
    Args:
        derivation_paths: List of derivation paths
        
    Returns:
        The app ID for the coin
        
    Raises:
        AssertionError: If derivation paths are for different coins or unsupported
    """
    coin_indexes = [derivation_path[1] for derivation_path in derivation_paths]
    first_coin_index = coin_indexes[0]
    
    is_same = all(x == first_coin_index for x in coin_indexes)
    assert_condition(is_same, "Derivation paths must be for the same coin")
    
    app_id = coin_index_to_app_id_map.get(first_coin_index)
    assert_condition(app_id, f"Coin {hex(first_coin_index)} is not supported")
    
    return app_id


async def configure_app_id(sdk: ISDK, derivation_paths: List[List[int]]) -> None:
    """
    Configure app ID on SDK and check compatibility.
    
    Args:
        sdk: The SDK instance
        derivation_paths: List of derivation paths
    """
    app_id = get_app_id_from_derivation_paths(derivation_paths)
    sdk.configure_applet_id(app_id)
    await sdk.check_app_compatibility(APP_VERSION)


class AppFeatures:
    """
    Supported features in the BTC app.
    """
    INPUT_IN_CHUNKS: IFeatureSupport = {
        'name': 'INPUT_IN_CHUNKS',
        'from_version': '1.1.0',
    }





