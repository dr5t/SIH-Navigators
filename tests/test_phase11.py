import unittest
from unittest.mock import patch, MagicMock
from integration import run_integration

class TestPhase11(unittest.TestCase):
    @patch('integration.httpx.post')
    def test_run_integration(self, mock_post):
        # Mock successful backend response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        
        # Run integration script
        run_integration()
        
        # Verify it attempted to sync to backend
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        
        self.assertEqual(args[0], "http://localhost:8000/api/v1/sync")
        payload = kwargs['json']
        
        self.assertEqual(payload['session_id'], "sim_session_001")
        self.assertEqual(len(payload['trajectory']), 100)

if __name__ == '__main__':
    unittest.main()
