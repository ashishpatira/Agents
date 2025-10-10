import os
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

def get_10k_filings():
    """
    Fetches the 10-K filings for the companies in the COMPANIES list and prints the URLs.
    """
    headers = {"User-Agent": "test@test.com"}

    for company, cik in COMPANIES.items():
        # Zero-pad the CIK to 10 digits
        padded_cik = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Find the latest 10-K filing
            filings = response.json()
            for i in range(len(filings['filings']['recent']['accessionNumber'])):
                if filings['filings']['recent']['form'][i] == '10-K':
                    accession_number = filings['filings']['recent']['accessionNumber'][i]
                    filing_date = filings['filings']['recent']['filingDate'][i]
                    print(f"Found 10-K for {company} filed on {filing_date}")

                    # Construct the URL for the filing
                    accession_number_no_dashes = accession_number.replace('-', '')
                    filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number_no_dashes}/{accession_number}.txt"
                    print(f"Filing URL for {company}: {filing_url}")
                    break
        else:
            print(f"Failed to fetch data for {company}")

if __name__ == "__main__":
    get_10k_filings()
