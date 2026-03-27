# Agents
Agentic Workflows to find investible companies

## Y Combinator Scraper

This repository includes a script to scrape the newest startups listed on Y Combinator, specifically from recent batches (e.g., W24), and extract their details into a JSON file.

### Prerequisites

Ensure you have Python 3 installed. The script relies on the `requests` and `beautifulsoup4` libraries.

You can install the required dependencies using pip:

```bash
pip install requests beautifulsoup4
```

### Usage

Run the scraper script directly from the terminal:

```bash
python ycombinator_scraper.py
```

By default, the script scrapes the **W24** batch and saves the data to `ycombinator_startups.json`.

**Command Line Arguments:**
You can optionally customize the batch and the output filename:

```bash
python ycombinator_scraper.py --batch S24 --output s24_startups.json
```

**Extracted Data:**
The resulting JSON file will contain a list of startups with the following fields:
* `Company Name`
* `YC Batch`
* `Short Description`
* `Website URL`
* `Industry`
* `Founders`
