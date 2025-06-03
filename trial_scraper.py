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

        # Eligibility based on keyword search
        eligibility = ""
        eligibility_heading = soup.find(string=lambda s: s and "Eligibility Criteria" in s)
        if eligibility_heading:
            parent = eligibility_heading.find_parent()
            content_div = parent.find_next_sibling()
            if content_div:
                eligibility = clean_text(content_div.get_text(separator=" "))

        # Contact info via text label proximity
        contact_name, contact_email = "", ""
        all_text = soup.get_text(separator="\n")
        lines = [line.strip() for line in all_text.split("\n") if line.strip()]
        for i, line in enumerate(lines):
            if "contact name" in line.lower() and i + 1 < len(lines):
                contact_name = lines[i + 1]
            elif "contact email" in line.lower() and i + 1 < len(lines):
                contact_email = lines[i + 1]

        # Locations via visible country/city block
        locations = []
        location_candidates = soup.find_all("div", string=lambda s: s and ("Taiwan" in s or "United States" in s))
        for loc in location_candidates:
            locations.append(clean_text(loc.get_text()))

        return contact_name, contact_email, eligibility, locations
    except Exception as e:
        print(f"Scraper error: {e}")
        return "", "", "", []
