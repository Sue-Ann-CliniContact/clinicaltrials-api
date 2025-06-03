
import requests
from bs4 import BeautifulSoup
from utils import clean_text
import re
import json

def get_matching_trials(term):
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
            nct_id = link.split("/")[-1].split("?")[0] if "clinicaltrials.gov" in link else "N/A"

            contact_name, contact_email, eligibility, locations = get_structured_info(link)

            results.append({
                "title": title,
                "nct_id": nct_id,
                "link": link,
                "contact_name": contact_name,
                "contact_email": contact_email,
                "eligibility": eligibility,
                "locations": locations
            })

        return results
    except Exception as e:
        return [{"error": f"Failed to fetch trials: {str(e)}"}]

def get_structured_info(url):
    try:
        html = requests.get(url, timeout=10).text
        json_data = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        if not json_data:
            return "", "", "", []

        data = json.loads(json_data.group(1))

        contact_name = data.get("contact", {}).get("name", "")
        contact_email = data.get("contact", {}).get("email", "")

        eligibility = data.get("eligibilityCriteria", "")

        locations = []
        if isinstance(data.get("location"), list):
            for loc in data["location"]:
                address = loc.get("address", {})
                loc_str = ", ".join(filter(None, [
                    address.get("addressLocality", ""),
                    address.get("addressRegion", ""),
                    address.get("addressCountry", "")
                ]))
                if loc_str:
                    locations.append(loc_str)

        return clean_text(contact_name), contact_email, clean_text(eligibility), locations
    except Exception:
        return "", "", "", []
