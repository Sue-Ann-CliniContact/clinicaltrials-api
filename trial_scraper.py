
import requests
from bs4 import BeautifulSoup
from utils import clean_text

def get_matching_trials(term):
    url = f"https://clinicaltrials.gov/ct2/results/rss.xml?cond={term}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        results = []
        for item in items:
            title = clean_text(item.title.text) if item.title else "N/A"
            link = item.link.text if item.link else "N/A"
            nct_id = link.split("/")[-1] if "ct2/show/" in link else "N/A"
            results.append({
                "title": title,
                "nct_id": nct_id,
                "link": link,
                "contact_name": "",
                "contact_email": ""
            })

        return results
    except Exception as e:
        return [{"error": f"Failed to fetch trials: {str(e)}"}]

