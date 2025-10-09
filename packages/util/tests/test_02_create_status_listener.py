from unittest.mock import MagicMock
from util.utils.create_status_listener import create_status_listener
from tests.__fixtures__.create_status_listener import fixtures


class TestCreateStatusListener:
    def test_trigger_events(self):
        for test_case in fixtures["valid"]:
            on_event_for_this_subtest = MagicMock()
            logger = test_case.get("logger")
            operation_enum_from_fixture = test_case.get("operationEnum")
            seed_generation_enum_from_fixture = test_case.get("seedGenerationEnum")

            status_listener_components = create_status_listener(
                {
                    "enums": test_case["enum"],
                    "operationEnums": operation_enum_from_fixture,
                    "seedGenerationEnums": seed_generation_enum_from_fixture,
                    "onEvent": on_event_for_this_subtest,
                    "logger": logger,
                }
            )

            on_status_func = status_listener_components["onStatus"]
            force_status_update_func = status_listener_components["forceStatusUpdate"]

            assert on_status_func is not None, "onStatus function should be defined"
            assert (
                force_status_update_func is not None
            ), "forceStatusUpdate function should be defined"

            for status_call_dict in test_case.get("statusCalls", []):
                on_status_func(status_call_dict)

            for flow_status_value in test_case.get("forceStatusUpdateCalls", []):
                force_status_update_func(flow_status_value)

            expected_event_calls_from_fixture = test_case.get("eventCalls", [])

            test_name = test_case["name"]
            assert on_event_for_this_subtest.call_count == len(
                expected_event_calls_from_fixture
            ), f"Mock call count mismatch for subtest: {test_name}"

            for i, expected_single_call_args_list in enumerate(
                expected_event_calls_from_fixture
            ):
                actual_call_obj = on_event_for_this_subtest.call_args_list[i]
                actual_args_as_tuple = actual_call_obj.args

                assert len(actual_args_as_tuple) == len(
                    expected_single_call_args_list
                ), f"Argument count mismatch for call {i} in subtest: {test_name}"
                assert (
                    actual_args_as_tuple[0] == expected_single_call_args_list[0]
                ), f"Argument value mismatch for call {i}, argument 0 in subtest: {test_name}"

                assert (
                    actual_call_obj.kwargs == {}
                ), f"Keyword arguments were not expected for call {i} in subtest: {test_name}"
