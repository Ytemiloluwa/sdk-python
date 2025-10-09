import pytest
from unittest.mock import patch, AsyncMock
from app_manager.services.__fixtures__.auth_verification import fixtures
from app_manager.services.authverification import (
    verify_serial_signature,
    verify_challenge_signature,
)


class TestDeviceAuthService:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch("app_manager.services.authverification.http") as mock_http:
            mock_http.post = AsyncMock()
            yield mock_http

    class TestVerifySerialSignature:
        @pytest.mark.asyncio
        async def test_should_be_able_to_return_valid_responses(self, setup):
            mock_http = setup
            for test_case in fixtures["verifySerialSignature"]["valid"]:
                for result in test_case["httpPostMocks"]["results"]:
                    mock_http.post.return_value = result
                challenge = await verify_serial_signature(test_case["params"])
                assert challenge == test_case["result"]
                expected_calls = test_case["httpPostMocks"]["calls"]
                actual_calls = []
                for call in mock_http.post.call_args_list:
                    args, kwargs = call
                    if len(args) >= 2:
                        actual_calls.append([args[0], args[1]])
                    elif len(args) == 1:
                        actual_calls.append([args[0], kwargs])
                    else:
                        actual_calls.append([None, kwargs])

                assert actual_calls == expected_calls

                mock_http.post.reset_mock()

    class TestVerifyChallengeSignature:
        @pytest.mark.asyncio
        async def test_should_be_able_to_return_valid_responses(self, setup):
            mock_http = setup
            for test_case in fixtures["verifyChallengeSignature"]["valid"]:
                for result in test_case["httpPostMocks"]["results"]:
                    mock_http.post.return_value = result
                result = await verify_challenge_signature(test_case["params"])
                assert result["isVerified"] == test_case["result"]
                expected_calls = test_case["httpPostMocks"]["calls"]
                actual_calls = []
                for call in mock_http.post.call_args_list:
                    args, kwargs = call
                    if len(args) >= 2:
                        actual_calls.append([args[0], args[1]])
                    elif len(args) == 1:
                        actual_calls.append([args[0], kwargs])
                    else:
                        actual_calls.append([None, kwargs])
                assert actual_calls == expected_calls
                mock_http.post.reset_mock()
