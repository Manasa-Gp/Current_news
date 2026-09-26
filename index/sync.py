"""
Triggers a sync on the (already-created) Delta Sync index so it picks up
whatever rows the daily pipeline just wrote. Called from pipeline.py right
after write_chunks() - not meant to be run standalone on a schedule of
its own.
"""

from databricks.vector_search.client import VectorSearchClient

from . import config as index_config
from ingestion import config


def trigger_sync() -> None:
    client = VectorSearchClient()
    index = client.get_index(
        endpoint_name=config.VS_ENDPOINT_NAME,
        index_name=config.VS_INDEX_NAME,
    )
    index.sync()
