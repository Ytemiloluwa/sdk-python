import pytest

from packages.core.src.encoders.raw import decode_raw_data, decode_status, encode_raw_data
from packages.core.src.utils.packetversion import PacketVersionMap
from packages.core.src.encoders.raw.__fixtures__ import (
    decode_raw_data_test_cases,
    decode_status_test_cases,
    encode_raw_data_test_cases,
    raw_data_test_cases,
)

class TestRawEncoder:
    class TestEncodeRawData:
        def test_should_return_valid_packets(self):
            for test_case in raw_data_test_cases["valid_encodings"]:
                result = encode_raw_data(test_case["raw_data"], PacketVersionMap.v3)
                assert result == test_case["encoded"]

        def test_should_throw_error_with_invalid_data(self):
            for test_case in encode_raw_data_test_cases["invalid"]:
                with pytest.raises(Exception):
                    encode_raw_data(test_case["raw_data"], test_case["version"])

    class TestDecodeRawData:
        def test_should_return_valid_packets(self):
            for test_case in raw_data_test_cases["valid_encodings"]:
                result = decode_raw_data(test_case["encoded"], PacketVersionMap.v3)
                assert result is not None
                assert result == test_case["raw_data"]

        def test_should_throw_error_with_invalid_data(self):
            for test_case in decode_raw_data_test_cases["invalid"]:
                with pytest.raises(Exception):
                    decode_raw_data(test_case["payload"], test_case["version"])

    class TestDecodeStatus:
        def test_should_return_valid_packets(self):
            for test_case in decode_status_test_cases["valid_encodings"]:
                result = decode_status(test_case["encoded"], PacketVersionMap.v3)
                assert result is not None
                assert result == test_case["status"]

        def test_should_throw_error_with_invalid_data(self):
            for test_case in decode_status_test_cases["invalid"]:
                with pytest.raises(Exception):
                    decode_status(test_case["payload"], test_case["version"])


if __name__ == "__main__":
    pytest.main([__file__])
