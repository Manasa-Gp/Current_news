"""
Writes chunk records to the Unity Catalog Delta table that the Vector
Search Delta Sync index stays in sync with. Must run inside a Databricks
notebook/job task where `spark` is already available.
"""

from datetime import datetime, timezone

from . import config


def write_chunks(spark, rows: list[dict]) -> None:
    """
    rows: list of dicts, one per chunk, matching CHUNKS_TABLE's schema:
        chunk_id, article_url, chunk_text, embedding, keywords,
        published_date, category
    """
    if not rows:
        return

    df = spark.createDataFrame(rows)
    (
        df.write
        .format("delta")
        .mode("append")
        .saveAsTable(config.CHUNKS_TABLE)
    )


def get_last_run(spark) -> datetime:
    """Read the timestamp of the last successful pipeline run."""
    try:
        row = (
            spark.table(config.LAST_RUN_TABLE)
            .orderBy("run_at", ascending=False)
            .limit(1)
            .collect()
        )
        if row:
            return row[0]["run_at"]
    except Exception:
        pass  # table doesn't exist yet - first ever run
    # Default: look back 1 day on a fresh setup.
    from datetime import timedelta
    return datetime.now(timezone.utc) - timedelta(days=1)


def record_run(spark, run_at: datetime, articles_fetched: int, chunks_written: int) -> None:
    row = [{
        "run_at": run_at,
        "articles_fetched": articles_fetched,
        "chunks_written": chunks_written,
    }]
    spark.createDataFrame(row).write.format("delta").mode("append").saveAsTable(
        config.LAST_RUN_TABLE
    )
