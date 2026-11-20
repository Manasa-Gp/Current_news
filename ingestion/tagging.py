# ingestion/tagging.py

# WHAT: produces the list of tags/keywords attached to one chunk.
# WHY:  this is how filtering works later - a user's question gets
#       matched against these tags, not just raw vector similarity.
# NEXT: pipeline.py calls this once per chunk, right before writing it
#       to the Delta table. The tags it returns go straight into the
#       `keywords` column.

import re

_STOPWORDS = {
    "The", "A", "An", "This", "That", "It", "In", "On", "At", "For",
    "With", "By", "From", "As", "Is", "Are", "Was", "Were", "And", "Or",
}

_CAP_PHRASE = re.compile(r"\b([A-Z][a-zA-Z0-9&]*(?:\s+[A-Z][a-zA-Z0-9&]*){0,3})\b")


def extract_entities(text: str) -> list[str]:
    seen = {}
    for match in _CAP_PHRASE.finditer(text):
        phrase = match.group(1).strip()
        if phrase.split()[0] in _STOPWORDS or len(phrase) < 3:
            continue
        seen[phrase] = None
    return list(seen.keys())


def tag_chunk(chunk_text: str, source_categories: list[str]) -> list[str]:
    tags = list(dict.fromkeys(source_categories))
    tags.extend(extract_entities(chunk_text))
    return tags