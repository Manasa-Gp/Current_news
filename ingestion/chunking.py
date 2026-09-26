"""
Paragraph-first chunking with a cheap semantic fallback.

Most articles are already well-segmented by paragraph, so that's the
default chunk boundary - free, no extra embedding calls. Only when a
paragraph is too long (or a run of short paragraphs looks like it should
be merged) do we fall back to embedding sentences and deciding the split
point by similarity. Same embedding model as the final index (embeddings.py).
"""

import re

from . import config
from .embeddings import embed_texts


def _split_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paragraphs


def _split_sentences(paragraph: str) -> list[str]:
    # Simple sentence splitter - good enough for news prose.
    sentences = re.split(r"(?<=[.!?])\s+", paragraph.strip())
    return [s for s in sentences if s]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _semantic_split(paragraph: str) -> list[str]:
    """
    Only called for an over-long paragraph: embed its sentences and cut
    where consecutive-sentence similarity drops below the threshold,
    instead of splitting on an arbitrary character count.
    """
    sentences = _split_sentences(paragraph)
    if len(sentences) <= 1:
        return [paragraph]

    vectors = embed_texts(sentences)

    chunks, current = [], [sentences[0]]
    for i in range(1, len(sentences)):
        similarity = _cosine(vectors[i - 1], vectors[i])
        if similarity < config.SEMANTIC_SPLIT_THRESHOLD:
            chunks.append(" ".join(current))
            current = [sentences[i]]
        else:
            current.append(sentences[i])
    if current:
        chunks.append(" ".join(current))

    return chunks


def chunk_article(text: str) -> list[str]:
    """
    Return a list of chunk strings for one article's body text.
    Paragraph boundaries are the default split; only paragraphs longer
    than MAX_CHUNK_CHARS get the semantic-split treatment.
    """
    chunks: list[str] = []
    for paragraph in _split_paragraphs(text):
        if len(paragraph) <= config.MAX_CHUNK_CHARS:
            chunks.append(paragraph)
        else:
            chunks.extend(_semantic_split(paragraph))
    return chunks
