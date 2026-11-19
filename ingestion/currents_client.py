"""
WORKFLOW 1: Get new articles into the pipeline.

WHAT this file does:
    Talks to the Currents API, returns a plain list of article dicts.
    Nothing else lives here - no chunking, no saving, no tagging.
    One job: fetch.

WHY it's built this way:
    - category="technology" filters AT THE SOURCE, so you're not
      downloading irrelevant articles only to discard them later.
    - start_date is what makes the daily job incremental. Each run you
      pass in "the last time this pipeline succeeded", and Currents
      only returns articles published after that. Skip this and every
      run re-downloads AND re-embeds the same articles forever - wasted
      API calls, wasted embedding calls, wasted money on the embedding
      model.
    - This returns plain dicts, not a custom class. Keeps this file
      dumb and swappable: if you ever change news providers, only this
      file changes. chunking.py and tagging.py don't know or care
      where the dict came from.

HOW this fits into the big picture:
    pipeline.py calls fetch_articles() once per run - it's step 1 of 5
    (fetch -> chunk -> tag -> embed -> write). Whatever list comes back
    here is the ONLY thing chunking.py has to work with next. If this
    returns an empty list, nothing downstream has anything to do - this
    is the first domino in the whole daily job.

YOUR TODO:
    The structure and the tricky parts (date formatting, pagination
    logic) are explained below. Write the actual request code.
"""

import requests
from datetime import datetime, timezone

from . import config


def _rfc3339(dt: datetime) -> str:
    """
    Currents demands STRICT RFC 3339, e.g. "2026-09-26T00:00:00Z".
    A bare "2026-09-26" is valid ISO-8601 but gets you an HTTP 400 here -
    this bit the project when it was first tested, so it's worth its own
    function rather than inlining it and forgetting the gotcha later.

    TODO:
      1. Make sure `dt` is in UTC (dt.astimezone(timezone.utc))
      2. Format it as "YYYY-MM-DDTHH:MM:SSZ" (strftime)
      3. Return the string
    """
    raise NotImplementedError


def fetch_articles(since: datetime) -> list[dict]:
    """
    Return every technology-category article published after `since`.

    Before writing the loop below, it's worth hitting the API once by
    hand (curl, or a throwaway script) and printing the raw JSON - know
    what fields actually come back (title, description, url, category,
    published...) before you build logic that assumes a shape.

    TODO, in order:
      1. Start a `page_number = 1` and an empty `articles = []` list.
      2. Loop:
         a. Build the params dict: category, language,
            start_date=_rfc3339(since), page_number, page_size
            (config.CURRENTS_PAGE_SIZE).
         b. requests.get(config.CURRENTS_API_URL, params=..., headers=
            {"Authorization": config.CURRENTS_API_KEY}, timeout=30)
         c. resp.raise_for_status() - fail loudly on a bad request
            rather than silently continuing with no data.
         d. payload = resp.json(); check payload["status"] == "ok"
            before trusting payload.get("news", []) - Currents returns
            200 with an error status on some bad requests, not just a
            4xx, so raise_for_status() alone won't catch everything.
         e. Extend `articles` with this page's batch.
         f. Stop when the batch is shorter than page_size (that's the
            last page) or empty. Otherwise page_number += 1 and loop.
      3. Return `articles`.
    """
    raise NotImplementedError
