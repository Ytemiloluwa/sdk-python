from typing import Optional, Any
import bitcoinlib
from bitcoinlib.keys import HDKey

bitcoin_py_lib: Optional[Any] = None


def get_bitcoin_py_lib() -> Any:
    if not bitcoin_py_lib:
        raise RuntimeError("bitcoinpy-lib has not been set yet")
    return bitcoin_py_lib


def set_bitcoin_py_lib(bitcoin_py_library: Any) -> None:
    global bitcoin_py_lib
    bitcoin_py_lib = bitcoin_py_library


class BitcoinJSLibWrapper:
    class payments:
        @staticmethod
        def p2pkh(pubkey: bytes, network: str = "bitcoin") -> dict:
            hd_key = HDKey(pubkey, network=network)
            address = hd_key.address(encoding="base58")
            return {"address": address}

        @staticmethod
        def p2wpkh(pubkey: bytes, network: str = "bitcoin") -> dict:
            hd_key = HDKey(pubkey, network=network)
            address = hd_key.address(encoding="bech32")
            return {"address": address}

    keys = bitcoinlib.keys
    networks = bitcoinlib


def initialize_default_bitcoin_lib() -> None:
    set_bitcoin_py_lib(BitcoinJSLibWrapper())
