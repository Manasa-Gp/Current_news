"""
Entry point for the daily job: fetch -> chunk -> tag -> embed -> write.

Run as a Databricks Job task (Python script task, or called from a thin
notebook) where `spark` is provided by the runtime.
"""

import uuid
from datetime import datetime, timezone

from pyspark.sql import SparkSession

from . import config
from .currents_client import fetch_articles
from .chunking import chunk_article
from .tagging import tag_chunk
from .embeddings import embed_texts
from .delta_writer import write_chunks, get_last_run, record_run
from index.sync import trigger_sync


def run(spark) -> None:
    run_started_at = datetime.now(timezone.utc)
    since = get_last_run(spark)

    articles = fetch_articles(since=since)

    all_chunk_texts: list[str] = []
    chunk_meta: list[dict] = []  # everything except the embedding, same order as all_chunk_texts

    for article in articles:
        body = article.get("description") or article.get("title") or ""
        source_categories = article.get("category", [])

        for chunk_text in chunk_article(body):
            all_chunk_texts.append(chunk_text)
            chunk_meta.append({
                "chunk_id": str(uuid.uuid4()),
                "article_url": article["url"],
                "chunk_text": chunk_text,
                "keywords": tag_chunk(chunk_text, source_categories),
                "published_date": article.get("published"),
                "category": source_categories,
            })

    # One batch embedding call for every chunk from this run, rather than
    # one call per chunk.
    vectors = embed_texts(all_chunk_texts)

    rows = []
    for meta, vector in zip(chunk_meta, vectors):
        rows.append({**meta, "embedding": vector})

    write_chunks(spark, rows)
    if rows:
        trigger_sync()
    record_run(
        spark,
        run_at=run_started_at,
        articles_fetched=len(articles),
        chunks_written=len(rows),
    )

    print(f"Fetched {len(articles)} articles, wrote {len(rows)} chunks.")


if __name__ == "__main__":
    # Works whether this runs as a notebook cell (where `spark` already
    # exists) or as a plain script job task (where it doesn't yet).
    spark_session = SparkSession.builder.getOrCreate()
    run(spark_session)
