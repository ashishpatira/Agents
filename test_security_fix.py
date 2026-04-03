import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import asyncio

# Mocking modules that might not be available in the environment
mock_requests = MagicMock()
mock_aiohttp = MagicMock()
mock_bs4 = MagicMock()

sys.modules['requests'] = mock_requests
sys.modules['aiohttp'] = mock_aiohttp
sys.modules['bs4'] = mock_bs4

# Now import the modules to test
from sec_agent import get_10k_filing_urls, get_10k_filing_urls_async, SEC_USER_AGENT

class TestSecurityFix(unittest.TestCase):

    def test_sec_user_agent_format(self):
        # SEC requirements: <Company Name> <Admin Contact Email>
        # Our constant: "SEC Filing Agent admin@example.com"
        self.assertIn(" ", SEC_USER_AGENT)
        self.assertIn("@", SEC_USER_AGENT)
        self.assertNotEqual(SEC_USER_AGENT, "test@test.com")

    def test_sync_get_10k_filing_urls_uses_correct_ua(self):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'filings': {
                'recent': {
                    'accessionNumber': ['0000000000-00-000000'],
                    'form': ['10-K']
                }
            }
        }
        mock_requests.get.return_value = mock_response

        # Execute
        with patch('sec_agent.COMPANIES', {"TestCo": "12345"}):
            get_10k_filing_urls()

        # Verify
        args, kwargs = mock_requests.get.call_args
        headers = kwargs.get('headers', {})
        self.assertEqual(headers.get('User-Agent'), SEC_USER_AGENT)

    def test_async_get_10k_filing_urls_uses_correct_ua(self):
        # Setup mock aiohttp session
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'filings': {
                'recent': {
                    'accessionNumber': ['0000000000-00-000000'],
                    'form': ['10-K']
                }
            }
        }

        # This is a bit tricky with nested async contexts, but we can mock the session.get
        mock_session.get.return_value.__aenter__.return_value = mock_response

        # We need to run the async function
        async def run_test():
            from sec_agent import fetch_filing_url
            headers = {"User-Agent": SEC_USER_AGENT}
            await fetch_filing_url(mock_session, "TestCo", "12345", headers)

        asyncio.run(run_test())

        # Verify
        args, kwargs = mock_session.get.call_args
        headers = kwargs.get('headers', {})
        self.assertEqual(headers.get('User-Agent'), SEC_USER_AGENT)

if __name__ == '__main__':
    unittest.main()
