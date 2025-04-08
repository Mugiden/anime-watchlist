from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, requests, os
from urllib.parse import quote_plus

app = Flask(__name__)

with open("data/pages.json", "r", encoding="utf-8") as f:
    mal_sync_db = json.load(f)

def get_malsync_links(mal_id):
    str_id = str(mal_id)
    links = {}
    if str_id in mal_sync_db:
        for provider, data in mal_sync_db[str_id].get("sites", {}).items():
            links[provider] = data["url"]
    return links

def get_google_links(title):
    base = "https://www.google.com/search?q=site:"
    providers = {
        "Crunchyroll": "crunchyroll.com",
        "Netflix": "netflix.com",
        "ADN": "animationdigitalnetwork.fr",
        "Prime Video": "primevideo.com"
    }
    return {
        name: f"{base}{domain}+{quote_plus(title)}" for name, domain in providers.items()
    }

def search_anime_jikan(query):
    url = f"https://api.jikan.moe/v4/anime?q={quote_plus(query)}&limit=5"
    r = requests.get(url)
    return r.json().get("data", [])

def get_anime_details(mal_id):
    url = f"https://api.jikan.moe/v4/anime/{mal_id}"
    r = requests.get(url)
    return r.json().get("data")

@app.route("/")
def index():
    try:
        with open("data/watchlist.json", "r") as f:
            watchlist = json.load(f)
    except:
        watchlist = []
    return render_template("index.html", watchlist=watchlist)

@app.route("/search")
def search():
    query = request.args.get("q")
    results = search_anime_jikan(query) if query else []
    return render_template("search.html", results=results, query=query)

@app.route("/anime/<int:mal_id>")
def anime_detail(mal_id):
    anime = get_anime_details(mal_id)
    malsync_links = get_malsync_links(mal_id)
    google_links = get_google_links(anime['title'])
    return render_template("anime.html", anime=anime, malsync=malsync_links, google=google_links)

@app.route("/add", methods=["POST"])
def add_to_watchlist():
    data = request.form.to_dict()
    try:
        with open("data/watchlist.json", "r") as f:
            watchlist = json.load(f)
    except:
        watchlist = []
    watchlist.append(data)
    with open("data/watchlist.json", "w") as f:
        json.dump(watchlist, f, indent=2)
    return redirect(url_for("index"))

@app.route("/delete/<int:index>")
def delete_from_watchlist(index):
    try:
        with open("data/watchlist.json", "r") as f:
            watchlist = json.load(f)
        if 0 <= index < len(watchlist):
            watchlist.pop(index)
            with open("data/watchlist.json", "w") as f:
                json.dump(watchlist, f, indent=2)
    except:
        pass
    return redirect(url_for("index"))

@app.route("/update/<int:index>", methods=["POST"])
def update_watchlist(index):
    try:
        with open("data/watchlist.json", "r") as f:
            watchlist = json.load(f)
        if 0 <= index < len(watchlist):
            for key in request.form:
                watchlist[index][key] = request.form[key]
            with open("data/watchlist.json", "w") as f:
                json.dump(watchlist, f, indent=2)
    except:
        pass
    return redirect(url_for("index"))

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    if not os.path.exists("data/watchlist.json"):
        with open("data/watchlist.json", "w") as f:
            json.dump([], f)
    app.run(debug=True)