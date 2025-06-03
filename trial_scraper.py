import requests
from bs4 import BeautifulSoup
from utils import clean_text
import os

def get_raw_trials(term):
    rss_url = f"https://clinicaltrials.gov/ct2/results/rss.xml?cond={term}"
    try:
        rss_response = requests.get(rss_url, timeout=10)
        rss_response.raise_for_status()
        soup = BeautifulSoup(rss_response.content, "xml")
        items = soup.find_all("item")

        results = []
        for item in items:
            title = clean_text(item.title.text) if item.title else "N/A"
            link = item.link.text if item.link else "N/A"
            if "/study/" in link:
                nct_id = link.split("/")[-1].split("?")[0]
                link = f"https://clinicaltrials.gov/ct2/show/{nct_id}"
            else:
                nct_id = link.split("/")[-1].split("?")[0]

            page_text = fetch_page_text(link)

            results.append({
                "title": title,
                "nct_id": nct_id,
                "link": link,
                "raw_page_text": page_text
            })

        return results
    except Exception as e:
        return [{"error": f"Failed to fetch trials: {str(e)}"}]

def fetch_page_text(url):
    try:
        api_key = os.getenv("SCRAPER_API_KEY")
        if not api_key:
            return "[Error: SCRAPER_API_KEY not found in environment variables]"

        proxy_url = f"https://api.scraperapi.com/?api_key={api_key}&url={url}"
        print(f"🔍 Fetching through ScraperAPI: {url}")

        response = requests.get(proxy_url, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n")
        return clean_text(text)
    except Exception as e:
        return f"[Error retrieving page: {str(e)}]"

