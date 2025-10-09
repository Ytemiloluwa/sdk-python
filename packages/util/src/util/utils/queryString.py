from typing import Dict, Any
from urllib.parse import parse_qs, urlencode


def create_query_string(params: Dict[str, Any]) -> str:
    filtered_params = {k: v for k, v in params.items() if v is not None}
    return urlencode(filtered_params, doseq=True)


def parse_query_string(query: str) -> Dict[str, Any]:
    parsed = parse_qs(query)
    result = {}
    for key, value in parsed.items():
        result[key] = value[0] if len(value) == 1 else value
    return result
