# ingestion/embeddings.py

# WHAT: turns a list of text strings into a list of embedding vectors,
#       using the Databricks-managed model via the Foundation Model API.
# WHY:  one function, used everywhere embeddings are needed - the
#       semantic-split fallback in chunking.py AND the final chunk
#       vectors written to Delta. Same model both places, one place to
#       change if the endpoint ever changes.
# NEXT: chunking.py's _semantic_split stub gets filled in using this,
#       and pipeline.py calls it once per batch of chunks before writing
#       to Delta.

import os
import requests

DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")
EMBEDDING_ENDPOINT = os.environ.get("EMBEDDING_ENDPOINT", "databricks-bge-large-en")


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    response = requests.post(
        f"{DATABRICKS_HOST}/serving-endpoints/{EMBEDDING_ENDPOINT}/invocations",
        headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}"},
        json={"input": texts},
    )
    data = response.json()
    ordered = sorted(data["data"], key=lambda row: row["index"])
    return [row["embedding"] for row in ordered]