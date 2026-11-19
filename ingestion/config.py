"""
WORKFLOW 0: Settings, not secrets.

WHAT this file is:
    Every constant the pipeline needs, in one place. No logic, no API
    calls - just values other files import.

WHY it exists separately:
    Without this, "technology" and "1200" and table names would be
    scattered across 6 files as magic strings/numbers. Change one value
    here instead of grepping every file when something needs to move
    (e.g. you switch Unity Catalog schemas, or decide chunks should be
    shorter).

WHY secrets are NOT here:
    CURRENTS_API_KEY, DATABRICKS_TOKEN etc. are read from os.environ,
    not hardcoded. This file gets committed to git - anything typed
    directly into it is permanently in your git history, even if you
    delete it later. Secrets live in env vars (locally) or Databricks
    secrets (in the job).

HOW this fits into the big picture:
    Every other file in ingestion/ starts with `from . import config`.
    This is the one file every workflow step depends on.
"""

import os

# --- Currents API (workflow 1: fetch) ---
CURRENTS_API_URL = "https://api.currentsapi.services/v1/search"
CURRENTS_API_KEY = os.environ.get("CURRENTS_API_KEY", "")
CURRENTS_CATEGORY = "technology"
CURRENTS_LANGUAGE = "en"
CURRENTS_PAGE_SIZE = 200  # Currents' own max per page

# --- Unity Catalog (workflow 4: write) ---
UC_CATALOG = os.environ.get("UC_CATALOG", "main")
UC_SCHEMA = os.environ.get("UC_SCHEMA", "news_app")
ARTICLES_TABLE = f"{UC_CATALOG}.{UC_SCHEMA}.articles"
CHUNKS_TABLE = f"{UC_CATALOG}.{UC_SCHEMA}.article_chunks"
LAST_RUN_TABLE = f"{UC_CATALOG}.{UC_SCHEMA}.pipeline_state"

# --- Embedding model (workflow 2 & 3: chunk + embed) ---
DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
EMBEDDING_ENDPOINT = os.environ.get("EMBEDDING_ENDPOINT", "databricks-bge-large-en")
# Check your actual embedding model's output size before trusting this -
# a mismatch here fails Vector Search index creation later, not now,
# which makes it a confusing error to debug if you forget you set it.
EMBEDDING_DIMENSION = int(os.environ.get("EMBEDDING_DIMENSION", "1024"))

# --- Chunking (workflow 2) ---
MAX_CHUNK_CHARS = 1200           # paragraphs longer than this get split further
SEMANTIC_SPLIT_THRESHOLD = 0.55  # cosine similarity below this = topic shift

# --- Vector Search (workflow 5) ---
VS_ENDPOINT_NAME = os.environ.get("VS_ENDPOINT_NAME", "news-app-endpoint")
VS_INDEX_NAME = f"{UC_CATALOG}.{UC_SCHEMA}.chunks_index"
