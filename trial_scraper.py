print("🔍 CliniContact scraper is LIVE and using updated logic")
import requests
from bs4 import BeautifulSoup
from utils import clean_text

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
            if "/study/" in link:
                nct_id = link.split("/")[-1].split("?")[0]
                link = f"https://clinicaltrials.gov/ct2/show/{nct_id}"
            else:
                nct_id = link.split("/")[-1].split("?")[0]

            contact_name, contact_email, eligibility, locations = scrape_ct2_page(link)

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

def scrape_ct2_page(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # Eligibility Section
        eligibility = ""
        elig_heading = soup.find("div", class_="tr-study-details__section", id="eligibility")
        if elig_heading:
            elig_text_block = elig_heading.find("div", class_="tr-study-details__content")
            if elig_text_block:
                eligibility = clean_text(elig_text_block.get_text(separator=" "))

        # Contact Info
        contact_name, contact_email = "", ""
        contact_labels = soup.find_all("dt")
        for label in contact_labels:
            label_text = label.get_text().strip().lower()
            if "contact name" in label_text:
                val = label.find_next_sibling("dd")
                if val:
                    contact_name = clean_text(val.get_text())
            elif "contact email" in label_text:
                val = label.find_next_sibling("dd")
                if val:
                    contact_email = clean_text(val.get_text())

        # Locations
        locations = []
        location_blocks = soup.find_all("div", class_="location-item")
        for loc in location_blocks:
            loc_text = clean_text(loc.get_text(separator=", "))
            if loc_text:
                locations.append(loc_text)

        return contact_name, contact_email, eligibility, locations
    except Exception:
        return "", "", "", []
