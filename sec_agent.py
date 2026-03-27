import os
import asyncio
import aiohttp
import requests

# A list of companies and their CIKs
COMPANIES = {
    "Microsoft": "0000789019",
    "Amazon": "0001018724",
    "Alphabet": "0001652044",
    "Meta": "0001326801",
    "Tesla": "0001318605",
    "Berkshire Hathaway": "0001067983",
    "Johnson & Johnson": "0000200406",
    "Procter & Gamble": "0000080424",
    "JPMorgan Chase": "0000019617",
    "Visa": "0001403161",
}

def get_10k_filing_urls():
    """
    Fetches the 10-K filings for the companies in the COMPANIES list and returns a dictionary of company names to filing URLs.
    Synchronous version using requests.
    """
    headers = {"User-Agent": "test@test.com"}
    filing_urls = {}

    for company, cik in COMPANIES.items():
        # Zero-pad the CIK to 10 digits
        padded_cik = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Find the latest 10-K filing
            filings = response.json()
            found = False
            for i in range(len(filings['filings']['recent']['accessionNumber'])):
                if filings['filings']['recent']['form'][i] == '10-K':
                    accession_number = filings['filings']['recent']['accessionNumber'][i]

                    # Construct the URL for the filing
                    accession_number_no_dashes = accession_number.replace('-', '')
                    filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number_no_dashes}/{accession_number}.txt"
                    filing_urls[company] = filing_url
                    found = True
                    break
            if not found:
                 print(f"No 10-K found for {company}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {company}: {e}")

    return filing_urls

async def fetch_filing_url(session, company, cik, headers):
    """
    Helper function to fetch a single company's filing URL asynchronously.
    """
    padded_cik = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            filings = await response.json()

            for i in range(len(filings['filings']['recent']['accessionNumber'])):
                if filings['filings']['recent']['form'][i] == '10-K':
                    accession_number = filings['filings']['recent']['accessionNumber'][i]
                    accession_number_no_dashes = accession_number.replace('-', '')
                    filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number_no_dashes}/{accession_number}.txt"
                    return company, filing_url
            print(f"No 10-K found for {company}")
            return company, None
    except Exception as e:
        print(f"Failed to fetch data for {company}: {e}")
        return company, None

async def get_10k_filing_urls_async():
    """
    Fetches the 10-K filings for the companies in the COMPANIES list asynchronously.
    Returns a dictionary of company names to filing URLs.
    """
    headers = {"User-Agent": "test@test.com"}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_filing_url(session, company, cik, headers) for company, cik in COMPANIES.items()]
        results = await asyncio.gather(*tasks)

    return {company: url for company, url in results if url}

if __name__ == "__main__":
    # Test sync version
    print("Testing synchronous version...")
    urls = get_10k_filing_urls()
    for company, url in urls.items():
        print(f"Filing URL for {company}: {url}")

    # Test async version
    print("\nTesting asynchronous version...")
    try:
        urls_async = asyncio.run(get_10k_filing_urls_async())
        for company, url in urls_async.items():
            print(f"Filing URL for {company} (async): {url}")
    except Exception as e:
        print(f"Async version failed (likely due to missing aiohttp in this environment): {e}")
