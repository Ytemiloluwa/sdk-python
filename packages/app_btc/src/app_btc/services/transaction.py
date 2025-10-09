from typing import Dict
from ..utils.http import http

base_url = '/v2/transaction'

async def get_raw_txn_hash(params: Dict[str, str]) -> str:
    """
    Get raw transaction hash from the API.
    
    Args:
        params: Dictionary containing coinType and hash
        
    Returns:
        Raw transaction hex string

    """
    response = await http.post(f"{base_url}/hex", json=params)
    return response.json()['data']['data']
