# ingestion/currents_client.py

# WHAT: this file will talk to the Currents API and return a list of
#       articles — nothing else in the pipeline makes HTTP calls to it.
# WHY:  keeping the API call in its own file means if Currents changes
#       their API later, this is the only file that needs editing.
# NEXT: pipeline.py will import and call the function below; it doesn't
#       care how the fetching happens, just that it gets back articles.

import os
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

load_dotenv()  # reads .env into environment variables, once, at import time

CURRENTS_API_URL = "https://api.currentsapi.services/v1/search"
API_KEY = os.environ.get("CURRENTS_API_KEY")

def _rfc3339(dt: datetime) -> str:
    # Currents rejects plain dates like "2026-09-01" - it wants this exact
    # strict format, so this helper exists just to avoid repeating it everywhere.
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch_articles(since: datetime, page_size: int = 20):
    # WHAT: adds start_date so Currents only returns articles published
    #       after `since`.
    # WHY:  without this, every run re-fetches the same recent articles -
    #       wasted requests, and we'd re-process ones we already have.
    #       This is the piece that makes the pipeline "incremental."
    # NEXT: `since` has to come from somewhere real - next microstep is a
    #       tiny stand-in for "when did we last run successfully," before
    #       we wire it to the actual Delta table later.
    articles = []
    page_number = 1

    while True:
        response = requests.get(
            CURRENTS_API_URL,
            params={
                "category": "technology",
                "language": "en",
                "start_date": _rfc3339(since),
                "page_number": page_number,
                "page_size": page_size,
            },
            headers={"Authorization": API_KEY},
        )
        batch = response.json().get("news", [])
        articles.extend(batch)

        if len(batch) < page_size:  # short page = last page
            break
        page_number += 1

    return articles

if __name__ == "__main__":
    from datetime import timedelta
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    results = fetch_articles(since=yesterday)
    print(f"Got {len(results)} articles")
    for a in results[:3]:
        print("-", a["title"], "|", a["category"])