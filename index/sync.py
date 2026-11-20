# index/sync.py

# WHAT: tells the (already-created) index to pull in new rows.
# WHY:  the index uses TRIGGERED sync, not CONTINUOUS - it only updates
#       when told to, so something has to actually call this.
# NEXT: pipeline.py calls this once, right after write_chunks() succeeds.

from databricks.vector_search.client import VectorSearchClient

VS_ENDPOINT_NAME = "news-app-endpoint"
VS_INDEX_NAME = "main.news_app.chunks_index"


def trigger_sync() -> None:
    client = VectorSearchClient()
    index = client.get_index(endpoint_name=VS_ENDPOINT_NAME, index_name=VS_INDEX_NAME)
    index.sync()