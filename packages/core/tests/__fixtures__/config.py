from types import SimpleNamespace


def dict_to_namespace(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in d.items()})
    return d


# Mimic the production config structure
v1 = dict_to_namespace(
    {
        "constants": {
            "CHUNK_SIZE": 64,
            "START_OF_FRAME": "AA",
        },
        "radix": {
            "current_packet_number": 8,
            "total_packet": 8,
            "command_type": 8,
            "data_size": 8,
            "crc": 16,
        },
    }
)
v2 = dict_to_namespace(
    {
        "constants": {
            "CHUNK_SIZE": 64,
            "START_OF_FRAME": "5A5A",
        },
        "radix": {
            "current_packet_number": 8,
            "total_packet": 8,
            "command_type": 8,
            "data_size": 8,
            "crc": 16,
        },
    }
)
v3 = dict_to_namespace(
    {
        "constants": {
            "CHUNK_SIZE": 96,
            "START_OF_FRAME": "5555",
        },
        "radix": {
            "current_packet_number": 8,
            "total_packet": 8,
            "command_type": 8,
            "data_size": 8,
            "crc": 16,
        },
    }
)

# Provide both dict and attribute access at the top level
config = dict_to_namespace(
    {
        "defaultTimeout": 400,
        "v1": v1,
        "v2": v2,
        "v3": v3,
    }
)
