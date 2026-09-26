"""
Thin client for the Currents API.

Fetches only tech-category articles published after the last successful
run, using Currents' own start_date filter - this keeps daily requests
small and avoids reprocessing articles we've already chunked/embedded.
"""

import requests
from datetime import datetime, timezone

from . import config


def _rfc3339(dt: datetime) -> str:
    """Currents requires strict RFC 3339, e.g. 2026-09-26T00:00:00Z."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_articles(since: datetime, page_size: int = None) -> list[dict]:
    """
    Fetch every technology-category article published since `since`.

    Handles pagination itself and returns a flat list of raw article dicts
    exactly as Currents returns them (title, description, url, category,
    published, ...).
    """
    page_size = page_size or config.CURRENTS_PAGE_SIZE
    articles: list[dict] = []
    page_number = 1

    while True:
        resp = requests.get(
            config.CURRENTS_API_URL,
            params={
                "category": config.CURRENTS_CATEGORY,
                "language": config.CURRENTS_LANGUAGE,
                "start_date": _rfc3339(since),
                "page_number": page_number,
                "page_size": page_size,
            },
            headers={"Authorization": config.CURRENTS_API_KEY},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()

        if payload.get("status") != "ok":
            raise RuntimeError(f"Currents API error: {payload}")

        batch = payload.get("news", [])
        articles.extend(batch)

        # Stop once a page comes back short (last page) or empty.
        if len(batch) < page_size:
            break
        page_number += 1

    return articles
