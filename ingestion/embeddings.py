"""
Wrapper around the Databricks-managed embedding model, reached through a
Foundation Model API serving endpoint. Used both for the final chunk
embeddings (indexed into Vector Search) and for the handful of sentence
embeddings chunking.py needs to decide where to split a long paragraph -
same model everywhere, no second model to maintain.
"""

import requests

from . import config


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return one embedding vector per input string, same order in/out."""
    if not texts:
        return []

    resp = requests.post(
        f"{config.DATABRICKS_HOST}/serving-endpoints/{config.EMBEDDING_ENDPOINT}/invocations",
        headers={"Authorization": f"Bearer {config.DATABRICKS_TOKEN}"},
        json={"input": texts},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    # Foundation Model API embedding responses follow the OpenAI-style shape:
    # {"data": [{"embedding": [...], "index": 0}, ...]}
    ordered = sorted(data["data"], key=lambda row: row["index"])
    return [row["embedding"] for row in ordered]
