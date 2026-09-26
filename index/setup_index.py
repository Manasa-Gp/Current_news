"""
One-time setup for the Vector Search endpoint + Delta Sync index.

Run this once (manually, from a notebook) after the chunks table exists
with at least one row - not part of the daily job. It's idempotent: safe
to re-run, it skips creation if the endpoint/index already exist.

Self-managed embeddings mode is used here because pipeline.py already
computes embeddings itself and stores them in the `embedding` column -
Databricks just indexes what's already there, it doesn't compute anything.

TRIGGERED sync (not CONTINUOUS) matches a once-daily pipeline: the index
only updates when explicitly told to via sync.py, right after the daily
job writes new rows. No need to pay for a continuously-running sync.
"""

from databricks.vector_search.client import VectorSearchClient

from ingestion import config


def ensure_endpoint(client: VectorSearchClient) -> None:
    existing = [e["name"] for e in client.list_endpoints().get("endpoints", [])]
    if config.VS_ENDPOINT_NAME not in existing:
        client.create_endpoint(name=config.VS_ENDPOINT_NAME, endpoint_type="STANDARD")


def ensure_index(client: VectorSearchClient) -> None:
    existing = [i["name"] for i in client.list_indexes(config.VS_ENDPOINT_NAME).get("vector_indexes", [])]
    if config.VS_INDEX_NAME in existing:
        return

    client.create_delta_sync_index(
        endpoint_name=config.VS_ENDPOINT_NAME,
        index_name=config.VS_INDEX_NAME,
        source_table_name=config.CHUNKS_TABLE,
        pipeline_type="TRIGGERED",
        primary_key="chunk_id",
        embedding_dimension=config.EMBEDDING_DIMENSION,
        embedding_vector_column="embedding",
    )


if __name__ == "__main__":
    vs_client = VectorSearchClient()
    ensure_endpoint(vs_client)
    ensure_index(vs_client)
    print(f"Index ready: {config.VS_INDEX_NAME} on endpoint {config.VS_ENDPOINT_NAME}")
