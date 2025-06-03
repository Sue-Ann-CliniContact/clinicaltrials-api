from flask import Flask, request, jsonify
from trial_scraper import get_matching_trials

app = Flask(__name__)

@app.route("/search")
def search():
    term = request.args.get("term")
    if not term:
        return jsonify({"error": "Missing 'term' parameter"}), 400
    results = get_matching_trials(term)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
