
import requests
from bs4 import BeautifulSoup
from utils import clean_text

def get_matching_trials(term):
    url = "https://clinicaltrials.gov/ct2/results/rss.xml?cond=" + term
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")

    results = []
    for item in items:
        title = clean_text(item.title.text)
        link = item.link.text
        nct_id = link.split("/")[-1]
        results.append({
            "title": title,
            "nct_id": nct_id,
            "link": link,
            "contact_name": "",
            "contact_email": ""
        })
    return results
