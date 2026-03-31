import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from router_v3 import route_task
from pipeline_controls import execute_pipeline
from connectors.calendar_connector import send as calendar_send
from connectors.email_connector import send as email_send
from connectors.crm_connector import send as crm_send

class TestOrchestratorV3(unittest.TestCase):

    @patch('router_v3.requests.post')
    @patch('router_v3.sqlite3.connect')
    def test_route_task_proceed(self, mock_connect, mock_post):
        mock_post.return_value.json.return_value = {'data': {'decision': 'task_response', 'final_score': 0.8, 'top_agent': 'agent1'}}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        task_json = {'task_id': '123', 'task_type': 'calendar'}
        result = route_task(task_json)

        self.assertEqual(result['routed_to'], 'calendar')
        self.assertEqual(result['status'], 'sent')
        self.assertIn('trace_id', result)
        self.assertIn('timestamp', result)
        mock_conn.cursor().execute.assert_called()
        mock_conn.commit.assert_called()

    @patch('router_v3.requests.post')
    @patch('router_v3.sqlite3.connect')
    def test_route_task_defer(self, mock_connect, mock_post):
        mock_post.return_value.json.return_value = {'data': {'decision': 'defer', 'final_score': 0.5, 'top_agent': 'agent2'}}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        task_json = {'task_id': '124', 'task_type': 'email'}
        result = route_task(task_json)

        self.assertEqual(result['routed_to'], 'queue')
        self.assertEqual(result['status'], 'queued')

    @patch('router_v3.requests.post')
    @patch('router_v3.sqlite3.connect')
    def test_route_task_fallback_target(self, mock_connect, mock_post):
        mock_post.return_value.json.return_value = {'data': {'decision': 'task_response', 'final_score': 0.9, 'top_agent': 'agent3'}}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        task_json = {'task_id': '125', 'task_type': 'unknown', 'external_target': 'invalid'}
        result = route_task(task_json)

        self.assertEqual(result['routed_to'], 'fallback')
        self.assertEqual(result['status'], 'sent')

    @patch('connectors.calendar_connector.random.choice')
    def test_calendar_connector_success(self, mock_choice):
        mock_choice.return_value = True
        result = calendar_send({'test': 'data'})
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['info'], 'Event added to calendar')

    @patch('connectors.email_connector.random.choice')
    def test_email_connector_failure(self, mock_choice):
        mock_choice.return_value = False
        result = email_send({'test': 'data'})
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['info'], 'Failed to send email')

    @patch('pipeline_controls.calendar_send')
    @patch('pipeline_controls.sqlite3.connect')
    def test_execute_pipeline_success_first_try(self, mock_connect, mock_send):
        mock_send.return_value = {'status': 'success', 'info': 'ok'}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        result = execute_pipeline({'task_id': '123'}, 'calendar', 'trace123')

        self.assertEqual(result['final_status'], 'success')
        self.assertEqual(result['attempts'], 1)
        self.assertFalse(result['fallback_used'])

    @patch('pipeline_controls.time.sleep')
    @patch('pipeline_controls.calendar_send')
    @patch('pipeline_controls.sqlite3.connect')
    def test_execute_pipeline_retry_success(self, mock_connect, mock_send, mock_sleep):
        mock_send.side_effect = [{'status': 'failed'}, {'status': 'success'}]
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        result = execute_pipeline({'task_id': '123'}, 'calendar', 'trace123')

        self.assertEqual(result['final_status'], 'success')
        self.assertEqual(result['attempts'], 2)
        self.assertFalse(result['fallback_used'])
        self.assertEqual(mock_send.call_count, 2)
        mock_sleep.assert_called_once_with(1)

    @patch('pipeline_controls.time.sleep')
    @patch('pipeline_controls.calendar_send')
    @patch('pipeline_controls.email_send')
    @patch('pipeline_controls.sqlite3.connect')
    def test_execute_pipeline_fallback_success(self, mock_connect, mock_email, mock_calendar, mock_sleep):
        mock_calendar.return_value = {'status': 'failed'}
        mock_email.return_value = {'status': 'success', 'info': 'ok'}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        result = execute_pipeline({'task_id': '123'}, 'calendar', 'trace123')

        self.assertEqual(result['final_status'], 'success')
        self.assertEqual(result['attempts'], 3)  # max retries
        self.assertTrue(result['fallback_used'])

    @patch('pipeline_controls.time.sleep')
    @patch('pipeline_controls.calendar_send')
    @patch('pipeline_controls.email_send')
    @patch('pipeline_controls.sqlite3.connect')
    def test_execute_pipeline_complete_failure(self, mock_connect, mock_email, mock_calendar, mock_sleep):
        mock_calendar.return_value = {'status': 'failed'}
        mock_email.return_value = {'status': 'failed'}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        result = execute_pipeline({'task_id': '123'}, 'calendar', 'trace123')

        self.assertEqual(result['final_status'], 'failed')
        self.assertEqual(result['attempts'], 3)
        self.assertTrue(result['fallback_used'])

if __name__ == '__main__':
    unittest.main()