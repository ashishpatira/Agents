import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_ycombinator_startups(batch="W24", output_file="ycombinator_startups.json"):
    base_api_url = f"https://api.ycombinator.com/v0.1/companies?batch={batch}"
    startups_data = []
    page = 1

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Fetching startups for batch {batch}...")

    while True:
        url = f"{base_api_url}&page={page}"
        print(f"Fetching page {page}...")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

        companies = data.get("companies", [])
        if not companies:
            print("No more companies found.")
            break

        for comp in companies:
            startup_info = {
                "Company Name": comp.get("name"),
                "YC Batch": comp.get("batch"),
                "Short Description": comp.get("oneLiner"),
                "Website URL": comp.get("website"),
                "Industry": ", ".join(comp.get("industries", [])),
                "slug": comp.get("slug")
            }
            startups_data.append(startup_info)

        page += 1
        time.sleep(0.5) # Be nice to the API

    print(f"Found {len(startups_data)} startups. Fetching founder details...")

    for i, startup in enumerate(startups_data):
        slug = startup.get("slug")
        if not slug:
            startup["Founders"] = "Unknown"
            continue

        company_url = f"https://www.ycombinator.com/companies/{slug}"
        print(f"[{i+1}/{len(startups_data)}] Fetching details for {startup['Company Name']}...")

        founders_list = []
        try:
            response = requests.get(company_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Using BeautifulSoup to parse HTML as preferred by the user
            soup = BeautifulSoup(response.text, 'html.parser')

            # The founder data is inside a div with data-page attribute
            data_page_div = soup.find('div', {'data-page': True})

            if data_page_div:
                data_page_str = data_page_div['data-page']
                try:
                    page_data = json.loads(data_page_str)
                    company_data = page_data.get('props', {}).get('company', {})
                    founders = company_data.get('founders', [])
                    for founder in founders:
                        founders_list.append(founder.get('full_name'))
                except json.JSONDecodeError:
                    print(f"Error parsing JSON for {startup['Company Name']}")
            else:
                print(f"No data-page attribute found for {startup['Company Name']}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for {startup['Company Name']}: {e}")

        startup["Founders"] = ", ".join(founders_list) if founders_list else "Unknown"

        # Remove the temporary slug key
        startup.pop("slug", None)

        time.sleep(0.5) # Be nice to the server

    # Save the data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(startups_data, f, indent=4, ensure_ascii=False)

    print(f"Successfully saved data to {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Scrape Y Combinator startups.')
    parser.add_argument('--batch', type=str, default='W24', help='YC Batch to scrape (e.g., W24, S24)')
    parser.add_argument('--output', type=str, default='ycombinator_startups.json', help='Output JSON file')
    args = parser.parse_args()

    scrape_ycombinator_startups(batch=args.batch, output_file=args.output)
