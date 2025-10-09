from typing import List, Optional, Dict, Any
from unittest.mock import Mock
from .__mocks__ import sdk as sdk_mocks

on_event = Mock()

class ITestCase:
    def __init__(self):
        self.queries: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []
        self.mocks: Optional[Dict[str, Any]] = None

def setup_mocks(test_case: ITestCase):
    for _ in test_case.queries:
        sdk_mocks.send_query.return_value = None

    for result in test_case.results:
        def mock_wait_for_result(params=None):
            if params and params.get('on_status') and result.get('statuses'):
                on_event_calls = 0
                
                for status in result['statuses']:
                    params['on_status']({'flowStatus': status['flowStatus']})
                    
                    if 'expectEventCalls' in status:
                        for i, expected_call in enumerate(status['expectEventCalls']):
                            mock_index = len(on_event.call_args_list) - len(status['expectEventCalls']) + i
                            assert on_event.call_args_list[mock_index][0][0] == expected_call
                        
                        on_event_calls += len(status['expectEventCalls'])
                        assert on_event.call_count == on_event_calls
                    else:
                        assert on_event.call_count == on_event_calls
                
            return result['data']
        
        sdk_mocks.wait_for_result.side_effect = mock_wait_for_result

    return on_event

def clear_mocks():
    on_event.reset_mock()
    sdk_mocks.create.reset_mock()
    sdk_mocks.send_query.reset_mock()
    sdk_mocks.wait_for_result.reset_mock()
    sdk_mocks.run_operation.reset_mock()

def expect_mock_calls(test_case: ITestCase):
    assert sdk_mocks.run_operation.call_count == 1
    
    actual_calls = [call[0][0] for call in sdk_mocks.send_query.call_args_list]
    expected_calls = [query['data'] for query in test_case.queries]
    assert actual_calls == expected_calls
    
    if not test_case.mocks:
        return
    
    if 'eventCalls' in test_case.mocks:
        assert on_event.call_args_list == test_case.mocks['eventCalls']

