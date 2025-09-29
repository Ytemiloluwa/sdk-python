import pytest
from packages.util.utils.assert_utils import assert_condition

class TestAssert:
    def test_assert_fails(self):
        test_cases = [
            {
                "name": "undefined",
                "condition": None,
                "error": "Invalid argument",
                "error_message": "Invalid argument"
            },
            {
                "name": "null",
                "condition": None,
                "error": "Invalid argument",
                "error_message": "Invalid argument"
            },
            {
                "name": "false",
                "condition": False,
                "error": "Invalid argument",
                "error_message": "Invalid argument"
            },
            {
                "name": "false with custom error",
                "condition": False,
                "error": Exception("Custom error"),
                "error_message": "Custom error"
            }
        ]

        for test_case in test_cases:
            with pytest.raises(Exception) as context:
                assert_condition(test_case["condition"], test_case["error"])

            assert str(context.value) == test_case["error_message"]

    def test_assert_passes(self):
        test_cases = [
            {
                "name": "string",
                "condition": "aksjdh"
            },
            {
                "name": "empty string",
                "condition": ""
            },
            {
                "name": "object",
                "condition": {}
            },
            {
                "name": "array",
                "condition": []
            },
            {
                "name": "number",
                "condition": 1
            },
            {
                "name": "number zero",
                "condition": 0
            },
            {
                "name": "negative number",
                "condition": -12
            }
        ]

        for test_case in test_cases:
            assert_condition(test_case["condition"], "Should not have failed")


