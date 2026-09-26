"""
Central config for the ingestion pipeline.

Nothing secret lives here. Values are read from Databricks widgets/env vars
at runtime, which in turn should be backed by Databricks secrets
(see: databricks secrets create-scope / put-secret) - never hardcode keys.
"""

import os

# --- Currents API ---
CURRENTS_API_URL = "https://api.currentsapi.services/v1/search"
CURRENTS_API_KEY = os.environ.get("CURRENTS_API_KEY", "")
CURRENTS_CATEGORY = "technology"
CURRENTS_LANGUAGE = "en"
CURRENTS_PAGE_SIZE = 200  # max articles per page Currents allows

# --- Databricks / Unity Catalog ---
UC_CATALOG = os.environ.get("UC_CATALOG", "main")
UC_SCHEMA = os.environ.get("UC_SCHEMA", "news_app")
ARTICLES_TABLE = f"{UC_CATALOG}.{UC_SCHEMA}.articles"
CHUNKS_TABLE = f"{UC_CATALOG}.{UC_SCHEMA}.article_chunks"

# --- Embedding model (Databricks Foundation Model API serving endpoint) ---
DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
EMBEDDING_ENDPOINT = os.environ.get("EMBEDDING_ENDPOINT", "databricks-bge-large-en")

# --- Chunking ---
MAX_CHUNK_CHARS = 1200       # paragraphs longer than this get split further
SEMANTIC_SPLIT_THRESHOLD = 0.55  # cosine similarity below this = topic shift

# --- Job bookkeeping ---
# Where the pipeline stores "last successful run" so the next run only
# asks Currents for articles published after this point (avoids re-fetching
# and re-embedding the same articles).
LAST_RUN_TABLE = f"{UC_CATALOG}.{UC_SCHEMA}.pipeline_state"
