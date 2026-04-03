import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# Mock dependencies to allow importing sec_agent in a restricted environment
mock_aiohttp = MagicMock()
mock_requests = MagicMock()
sys.modules['aiohttp'] = mock_aiohttp
sys.modules['requests'] = mock_requests

import sec_agent

def test_construct_filing_url():
    cik = "0000789019"
    accession_number = "0001564590-23-011854"
    expected_url = "https://www.sec.gov/Archives/edgar/data/0000789019/000156459023011854/0001564590-23-011854.txt"
    assert sec_agent.construct_filing_url(cik, accession_number) == expected_url

@patch('sec_agent.requests.get')
def test_get_10k_filing_urls(mock_get):
    # Mocking the SEC API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'filings': {
            'recent': {
                'accessionNumber': ['0001564590-23-011854'],
                'form': ['10-K']
            }
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Temporarily limit COMPANIES to simplify test
    original_companies = sec_agent.COMPANIES
    sec_agent.COMPANIES = {"Microsoft": "0000789019"}

    try:
        urls = sec_agent.get_10k_filing_urls()
        assert "Microsoft" in urls
        assert "0001564590-23-011854" in urls["Microsoft"]
    finally:
        sec_agent.COMPANIES = original_companies

def test_fetch_filing_url():
    import asyncio
    mock_session = MagicMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        'filings': {
            'recent': {
                'accessionNumber': ['0001564590-23-011854'],
                'form': ['10-K']
            }
        }
    }
    mock_response.raise_for_status = MagicMock()

    # Mock the async context manager
    mock_session.get.return_value.__aenter__.return_value = mock_response

    company, url = asyncio.run(sec_agent.fetch_filing_url(mock_session, "Microsoft", "0000789019", {}))

    assert company == "Microsoft"
    assert "0001564590-23-011854" in url
