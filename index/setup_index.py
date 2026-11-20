# index/setup_index.py

# WHAT: one-time setup - creates the Vector Search endpoint and the
#       Delta Sync index, if they don't already exist.
# WHY:  this is NOT part of the daily job - run it once, manually, after
#       the chunks table has at least one row in it.
# NEXT: once this exists, index/sync.py (next workflow step) just keeps
#       it updated - it never creates anything itself.

from databricks.vector_search.client import VectorSearchClient

VS_ENDPOINT_NAME = "news-app-endpoint"
VS_INDEX_NAME = "main.news_app.chunks_index"
CHUNKS_TABLE = "main.news_app.article_chunks"
EMBEDDING_DIMENSION = 1024  # check your actual embedding model's output size


def ensure_endpoint(client: VectorSearchClient) -> None:
    existing = [e["name"] for e in client.list_endpoints().get("endpoints", [])]
    if VS_ENDPOINT_NAME not in existing:
        client.create_endpoint(name=VS_ENDPOINT_NAME, endpoint_type="STANDARD")


def ensure_index(client: VectorSearchClient) -> None:
    existing = [i["name"] for i in client.list_indexes(VS_ENDPOINT_NAME).get("vector_indexes", [])]
    if VS_INDEX_NAME in existing:
        return

    client.create_delta_sync_index(
        endpoint_name=VS_ENDPOINT_NAME,
        index_name=VS_INDEX_NAME,
        source_table_name=CHUNKS_TABLE,
        pipeline_type="TRIGGERED",
        primary_key="chunk_id",
        embedding_dimension=EMBEDDING_DIMENSION,
        embedding_vector_column="embedding",
    )

if __name__ == "__main__":
    vs_client = VectorSearchClient()
    ensure_endpoint(vs_client)
    ensure_index(vs_client)
    print(f"Index ready: {VS_INDEX_NAME} on endpoint {VS_ENDPOINT_NAME}")