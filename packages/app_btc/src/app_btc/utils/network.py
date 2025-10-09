from typing import Dict, List, Optional, Literal
from util.utils.assert_utils import assert_condition

try:
    from bdkpython import Network
    BDK_AVAILABLE = True
except ImportError:
    Network = None
    BDK_AVAILABLE = False

HARDENED_BASE = 0x80000000

LEGACY_PURPOSE = HARDENED_BASE + 44
SEGWIT_PURPOSE = HARDENED_BASE + 84

BITCOIN_COIN_INDEX = HARDENED_BASE + 0
TESTNET_COIN_INDEX = HARDENED_BASE + 1
LITECOIN_COIN_INDEX = HARDENED_BASE + 2
DOGECOIN_COIN_INDEX = HARDENED_BASE + 3
DASH_COIN_INDEX = HARDENED_BASE + 5


class NetworkConfig:
    def __init__(self, message_prefix: str, bech32: str,
                 bip32_public: int, bip32_private: int,
                 pub_key_hash: int, script_hash: int, wif: int):
        self.message_prefix = message_prefix
        self.bech32 = bech32
        self.bip32 = {'public': bip32_public, 'private': bip32_private}
        self.pub_key_hash = pub_key_hash
        self.script_hash = script_hash
        self.wif = wif


bitcoin = NetworkConfig(
    message_prefix='\x18Bitcoin Signed Message:\n',
    bech32='bc',
    bip32_public=76067358,
    bip32_private=76066276,
    pub_key_hash=0,
    script_hash=5,
    wif=128,
)

testnet = NetworkConfig(
    message_prefix='\x18Bitcoin Signed Message:\n',
    bech32='tb',
    bip32_public=70617039,
    bip32_private=70615956,
    pub_key_hash=111,
    script_hash=196,
    wif=239,
)

litecoin = NetworkConfig(
    message_prefix='\x19Litecoin Signed Message:\n',
    bech32='ltc',
    bip32_public=0x0488b21e,
    bip32_private=0x0488ade4,
    pub_key_hash=0x30,
    script_hash=0x32,
    wif=0xb0,
)

dash = NetworkConfig(
    message_prefix='\x19Dashcoin Signed Message:\n',
    bech32='',
    bip32_public=0x0488b21e,
    bip32_private=0x0488ade4,
    pub_key_hash=0x4c,
    script_hash=0x10,
    wif=0xcc,
)

dogecoin = NetworkConfig(
    message_prefix='\x19Dogecoin Signed Message:\n',
    bech32='',
    bip32_public=0x02facafd,
    bip32_private=0x02fac398,
    pub_key_hash=0x1e,
    script_hash=0x16,
    wif=0x9e,
)

coin_index_to_network_map: Dict[int, Optional[NetworkConfig]] = {
    BITCOIN_COIN_INDEX: bitcoin,
    TESTNET_COIN_INDEX: testnet,
    LITECOIN_COIN_INDEX: litecoin,
    DOGECOIN_COIN_INDEX: dogecoin,
    DASH_COIN_INDEX: dash,
}

PurposeType = Literal['segwit', 'legacy']

purpose_map: Dict[int, Optional[PurposeType]] = {
    SEGWIT_PURPOSE: 'segwit',
    LEGACY_PURPOSE: 'legacy',
}

coin_index_to_coin_type_map: Dict[int, Optional[str]] = {
    BITCOIN_COIN_INDEX: 'btc',
    TESTNET_COIN_INDEX: 'btct',
    LITECOIN_COIN_INDEX: 'ltc',
    DOGECOIN_COIN_INDEX: 'doge',
    DASH_COIN_INDEX: 'dash',
}


# --- Core API ---
def get_network_from_path(path: List[int]) -> NetworkConfig:
    coin_index = path[1]
    network = coin_index_to_network_map.get(coin_index)
    assert_condition(network, f"Coin index: {hex(coin_index)} not supported")
    return network


def get_purpose_type(path: List[int]) -> PurposeType:
    purpose = path[0]
    purpose_type = purpose_map.get(purpose)
    assert_condition(purpose_type, f"Purpose index: {hex(purpose)} not supported")
    return purpose_type


def get_coin_type_from_path(path: List[int]) -> str:
    coin_index = path[1]
    network = coin_index_to_coin_type_map.get(coin_index)
    assert_condition(network, f"Coin index: {hex(coin_index)} not supported")
    return network


supported_purpose_map: Dict[int, Optional[List[PurposeType]]] = {
    BITCOIN_COIN_INDEX: ['legacy', 'segwit'],
    LITECOIN_COIN_INDEX: ['legacy', 'segwit'],
    DOGECOIN_COIN_INDEX: ['legacy'],
    DASH_COIN_INDEX: ['legacy'],
}


def assert_derivation_path(path: List[int]) -> None:
    supported_purposes = supported_purpose_map.get(path[1])
    assert_condition(supported_purposes, f"Coin index: 0x{path[1]:x} not supported")
    purpose_type = get_purpose_type(path)
    assert_condition(
        purpose_type in supported_purposes,
        f"Purpose: 0x{path[0]:x} not supported for given coin index: 0x{path[1]:x}",
    )

def to_bdk_network(config: NetworkConfig):
    """Convert NetworkConfig to BDK Network (if BDK is available)."""
    if not BDK_AVAILABLE:
        raise ImportError("bdkpython is not installed. Install with: pip install bdkpython")
    
    if config is bitcoin:
        return Network.BITCOIN
    elif config is testnet:
        return Network.TESTNET
    else:
        raise ValueError(
            "Unsupported network for BDK: only Bitcoin mainnet and testnet supported"
        )


