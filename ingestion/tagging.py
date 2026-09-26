"""
Tagging = the source's own category (free, comes with every Currents
article) plus a light, rule-based pass for specific entities Currents
doesn't tag (company/product names) - no LLM call, no heavy NER model.

This is intentionally simple: a capitalized-phrase heuristic, filtered
against common words. It won't catch everything, but it's zero-cost and
catches the entities that matter most for filtering (proper nouns).
Swap in spaCy's small model later if this proves too coarse.
"""

import re

_STOPWORDS = {
    "The", "A", "An", "This", "That", "These", "Those", "It", "Its",
    "In", "On", "At", "For", "With", "By", "From", "As", "Is", "Are",
    "Was", "Were", "Be", "Been", "Being", "And", "Or", "But", "If",
    "Because", "While", "After", "Before", "During", "According",
}

_CAP_PHRASE = re.compile(r"\b([A-Z][a-zA-Z0-9&]*(?:\s+[A-Z][a-zA-Z0-9&]*){0,3})\b")


def extract_entities(text: str) -> list[str]:
    """Pull out likely company/product/proper-noun phrases from a chunk."""
    seen: dict[str, None] = {}
    for match in _CAP_PHRASE.finditer(text):
        phrase = match.group(1).strip()
        first_word = phrase.split()[0]
        if first_word in _STOPWORDS:
            continue
        if len(phrase) < 3:
            continue
        seen[phrase] = None
    return list(seen.keys())


def tag_chunk(chunk_text: str, source_categories: list[str]) -> list[str]:
    """
    Combine the source's own category tags (baseline, zero-cost) with
    entities pulled from this specific chunk (companies/products the
    source didn't tag).
    """
    tags = list(dict.fromkeys(source_categories))  # de-dupe, keep order
    tags.extend(extract_entities(chunk_text))
    return tags
