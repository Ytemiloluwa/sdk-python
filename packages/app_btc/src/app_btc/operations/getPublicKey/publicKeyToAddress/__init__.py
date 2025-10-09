from typing import List
from coincurve import PublicKey
from ....utils import get_bitcoin_py_lib, get_network_from_path, get_purpose_type


def get_address_from_public_key(uncompressed_public_key: bytes, path: List[int]) -> str:
    """
    1. Compress the uncompressed public key using secp256k1
    2. Get the appropriate payment function based on the path
    3. Generate the address using the payment function
    4. Assert that the address was generated successfully

    Args:
        uncompressed_public_key: Uncompressed public key as bytes (65 bytes)
        path: BIP32 derivation path as list of integers

    Returns:
        Bitcoin address as string

    Raises:
        AssertionError: If address could not be derived
    """
    if len(uncompressed_public_key) == 33:
        compressed_public_key = uncompressed_public_key
    elif len(uncompressed_public_key) == 65:
        compressed_public_key = PublicKey(uncompressed_public_key).format(
            compressed=True
        )
    else:
        raise ValueError(
            f"Invalid public key length: {len(uncompressed_public_key)} bytes. Expected 33 (compressed) or 65 (uncompressed)."
        )

    bitcoin_py_lib = get_bitcoin_py_lib()
    network_config = get_network_from_path(path)
    network = "bitcoin" if network_config.pub_key_hash == 0 else "testnet"

    purpose_type = get_purpose_type(path)

    if purpose_type == "segwit":
        result = bitcoin_py_lib.payments.p2wpkh(compressed_public_key, network)
    else:
        result = bitcoin_py_lib.payments.p2pkh(compressed_public_key, network)

    address = result["address"]
    assert address, "Could not derive address"
    return address
