
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

        # Eligibility
        eligibility = ""
        elig_section = soup.find("div", {"data-label": "Eligibility Criteria"})
        if elig_section:
            eligibility = clean_text(elig_section.get_text(separator=" "))

        # Contact
        contact_name, contact_email = "", ""
        contact_table = soup.find("table", class_="ct-contact-table")
        if contact_table:
            rows = contact_table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    label = cells[0].get_text().lower()
                    value = cells[1].get_text().strip()
                    if "name" in label and not contact_name:
                        contact_name = clean_text(value)
                    if "email" in label and "@" in value:
                        contact_email = clean_text(value)

        # Locations
        locations = []
        site_section = soup.find("div", {"data-label": "Locations"})
        if site_section:
            rows = site_section.find_all("div", class_="location-item")
            for row in rows:
                location_text = clean_text(row.get_text(separator=", "))
                if location_text:
                    locations.append(location_text)

        return contact_name, contact_email, eligibility, locations
    except Exception:
        return "", "", "", []
