import unittest.mock as mock
import sys

# Create a mock for requests and its exceptions if it's not installed
try:
    import requests
except ImportError:
    mock_requests = mock.MagicMock()
    mock_requests.exceptions = mock.MagicMock()
    # Mocking RequestException as a real exception class for catch blocks
    class MockRequestException(Exception):
        pass
    mock_requests.exceptions.RequestException = MockRequestException
    sys.modules["requests"] = mock_requests
    import requests

# We also need to mock bs4 to avoid errors if other files are imported or tested
try:
    import bs4
except ImportError:
    sys.modules["bs4"] = mock.MagicMock()

from sec_agent import get_10k_filing_urls

def test_get_10k_filing_urls_success():
    """Test that the function correctly parses a successful response and returns the expected 10-K URL."""
    # Define a sample response for the SEC API
    mock_filings = {
        'filings': {
            'recent': {
                'accessionNumber': ['0000789019-23-000001', '0000789019-23-000002'],
                'form': ['10-Q', '10-K']
            }
        }
    }

    with mock.patch('requests.get') as mock_get:
        # Create a mock response object
        mock_response = mock.Mock()
        mock_response.json.return_value = mock_filings
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Use only one company from COMPANIES to keep the test focused
        with mock.patch('sec_agent.COMPANIES', {'Microsoft': '0000789019'}):
            urls = get_10k_filing_urls()

        # Check if the URL was correctly constructed
        assert 'Microsoft' in urls
        assert urls['Microsoft'] == 'https://www.sec.gov/Archives/edgar/data/0000789019/000078901923000002/0000789019-23-000002.txt'

def test_get_10k_filing_urls_no_10k():
    """Test that the function handles cases where no 10-K filing is present."""
    mock_filings = {
        'filings': {
            'recent': {
                'accessionNumber': ['0000789019-23-000001'],
                'form': ['10-Q']
            }
        }
    }

    with mock.patch('requests.get') as mock_get:
        mock_response = mock.Mock()
        mock_response.json.return_value = mock_filings
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with mock.patch('sec_agent.COMPANIES', {'Microsoft': '0000789019'}):
            urls = get_10k_filing_urls()

        # Microsoft should not be in the result since no 10-K was found
        assert 'Microsoft' not in urls

def test_get_10k_filing_urls_request_error():
    """Test that the function handles requests.exceptions.RequestException gracefully."""
    with mock.patch('requests.get') as mock_get:
        # Simulate a RequestException
        mock_get.side_effect = requests.exceptions.RequestException("API connection error")

        with mock.patch('sec_agent.COMPANIES', {'Microsoft': '0000789019'}):
            urls = get_10k_filing_urls()

        # The function should catch the error and continue, returning an empty dict
        assert 'Microsoft' not in urls
        assert urls == {}
