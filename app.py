import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def fetch_trials(query):
    try:
        url = "https://clinicaltrials.gov/api/v2/studies"
        params = {
            "query.text": query,
            "filter.overallStatus": "recruiting",
            "filter.locations.locationCountry": "United States",
            "pageSize": 20
        }
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = []
        for study in data.get("studies", []):
            results.append({
                "title": study.get("protocolSection", {}).get("identificationModule", {}).get("officialTitle", "N/A"),
                "nct_id": study.get("protocolSection", {}).get("identificationModule", {}).get("nctId", "N/A"),
                "eligibility": study.get("protocolSection", {}).get("eligibilityModule", {}).get("eligibilityCriteria", "N/A"),
                "contact_name": study.get("protocolSection", {}).get("contactsLocationsModule", {}).get("centralContact", {}).get("name", ""),
                "contact_email": study.get("protocolSection", {}).get("contactsLocationsModule", {}).get("centralContact", {}).get("email", ""),
                "locations": study.get("protocolSection", {}).get("contactsLocationsModule", {}).get("locations", []),
                "link": f"https://clinicaltrials.gov/ct2/show/{study.get('protocolSection', {}).get('identificationModule', {}).get('nctId', '')}"
            })

        return results
    except Exception as e:
        return [{"error": str(e)}]

@app.route("/search", methods=["GET"])
def search_trials():
    query = request.args.get("term")
    if not query:
        return jsonify({"error": "Missing search term"}), 400

    trials = fetch_trials(query)
    return jsonify(trials)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
