
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
            nct_id = link.split("/")[-1].split("?")[0] if "clinicaltrials.gov" in link else "N/A"

            contact_name, contact_email, eligibility, locations = get_additional_info(link)

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

def get_additional_info(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        contact_name = ""
        contact_email = ""
        eligibility = ""
        locations = []

        contact_section = soup.find("div", id="contacts")
        if contact_section:
            name_el = contact_section.find("span", class_="ct-contact-name")
            email_el = contact_section.find("a", href=lambda h: h and "mailto:" in h)
            if name_el:
                contact_name = clean_text(name_el.text)
            if email_el:
                contact_email = email_el["href"].replace("mailto:", "").strip()

        eligibility_section = soup.find("div", id="eligibility")
        if eligibility_section:
            eligibility = clean_text(eligibility_section.get_text(separator=" "))

        loc_section = soup.find("div", id="locations")
        if loc_section:
            rows = loc_section.find_all("div", class_="ct-loc-list-row")
            for row in rows:
                loc = clean_text(row.get_text(separator=", "))
                if loc:
                    locations.append(loc)

        return contact_name, contact_email, eligibility, locations
    except Exception:
        return "", "", "", []
