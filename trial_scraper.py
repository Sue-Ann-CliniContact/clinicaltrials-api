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

        # Contact info
        contact_name = ""
        contact_email = ""
        contact_section = soup.find("div", id="tab-body")
        if contact_section:
            text = contact_section.get_text()
            if "Contact:" in text:
                contact_block = text.split("Contact:")[1].split("\n")[0:2]
                contact_name = contact_block[0].strip()
                if "@" in contact_block[1]:
                    contact_email = contact_block[1].strip()

        # Eligibility
        eligibility = ""
        eligibility_section = soup.find("div", id="eligibility")
        if eligibility_section:
            eligibility = clean_text(eligibility_section.get_text(separator=" "))

        # Locations
        locations = []
        loc_section = soup.find("div", id="contacts")
        if loc_section:
            rows = loc_section.find_all("div", class_="loc-contact")
            for row in rows:
                location = clean_text(row.get_text(separator=", "))
                if location:
                    locations.append(location)

        return contact_name, contact_email, eligibility, locations
    except Exception:
        return "", "", "", []
