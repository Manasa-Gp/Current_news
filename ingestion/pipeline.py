# ingestion/pipeline.py

# WHAT: the entry point - chains everything from workflows 1-5 together
#       in order: fetch -> chunk -> tag -> embed -> write.
# WHY:  every other file is a standalone piece so each could be built
#       and tested on its own; this file is just the glue, no new logic
#       of its own.
# NEXT: this is what the daily Databricks Job (workflow 7) actually runs.

from .currents_client import fetch_articles
from .chunking import chunk_article
from .tagging import tag_chunk
from .embeddings import embed_texts
from .delta_writer import write_chunks, get_last_run, record_run


import uuid
from datetime import datetime, timezone


def run(spark):
    run_started_at = datetime.now(timezone.utc)
    since = get_last_run(spark)

    articles = fetch_articles(since=since)

    chunk_meta = []  # one dict per chunk, everything except the embedding
    for article in articles:
        body = article.get("description") or article.get("title") or ""
        source_categories = article.get("category", [])

        for chunk_text in chunk_article(body):
            chunk_meta.append({
                "chunk_id": str(uuid.uuid4()),
                "article_url": article["url"],
                "chunk_text": chunk_text,
                "keywords": tag_chunk(chunk_text, source_categories),
                "published_date": article.get("published"),
                "category": source_categories,
            })
    all_texts = [meta["chunk_text"] for meta in chunk_meta]
    vectors = embed_texts(all_texts)

    rows = [{**meta, "embedding": vector} for meta, vector in zip(chunk_meta, vectors)]

    write_chunks(spark, rows)
    record_run(spark, run_at=run_started_at, articles_fetched=len(articles), chunks_written=len(rows))

    print(f"Fetched {len(articles)} articles, wrote {len(rows)} chunks.")


if __name__ == "__main__":
    from pyspark.sql import SparkSession
    spark_session = SparkSession.builder.getOrCreate()
    run(spark_session)