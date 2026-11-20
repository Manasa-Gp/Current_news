# ingestion/chunking.py

# WHAT: splits one article's text into a list of smaller chunk strings.
# WHY:  we don't embed/index a whole article as one block - chunks let
#       retrieval point at the specific paragraph that answers a question,
#       not the whole article.
# NEXT: tagging.py and embeddings.py will each work on these chunks one
#       at a time, after this function hands them off.

import re
from .embeddings import embed_texts

SEMANTIC_SPLIT_THRESHOLD = 0.55

MAX_CHUNK_CHARS = 1200

def chunk_article(text: str) -> list[str]:
    chunks = []
    for paragraph in [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]:
        if len(paragraph) <= MAX_CHUNK_CHARS:
            chunks.append(paragraph)
        else:
            chunks.extend(_semantic_split(paragraph))
    return chunks


def _split_sentences(paragraph: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", paragraph.strip())
    return [s for s in sentences if s]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def _semantic_split(paragraph: str) -> list[str]:
    sentences = _split_sentences(paragraph)
    if len(sentences) <= 1:
        return [paragraph]

    vectors = embed_texts(sentences)
    chunks, current = [], [sentences[0]]
    for i in range(1, len(sentences)):
        if _cosine(vectors[i - 1], vectors[i]) < SEMANTIC_SPLIT_THRESHOLD:
            chunks.append(" ".join(current))
            current = [sentences[i]]
        else:
            current.append(sentences[i])
    chunks.append(" ".join(current))
    return chunks