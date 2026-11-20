# ingestion/delta_writer.py

# WHAT: writes finished chunk rows to the Unity Catalog Delta table, and
#       tracks when the pipeline last ran successfully.
# WHY:  this is the only file that touches Spark/Delta directly - must
#       run inside a Databricks notebook or job task where `spark` is
#       available, unlike the other files which work anywhere.
# NEXT: get_last_run feeds the `since` argument back into
#       currents_client.fetch_articles on the next run - this is what
#       actually makes the pipeline incremental.
from datetime import datetime, timedelta, timezone


CHUNKS_TABLE = "main.news_app.article_chunks"
LAST_RUN_TABLE = "main.news_app.pipeline_state"


def write_chunks(spark, rows: list[dict]) -> None:
    if not rows:
        return
    df = spark.createDataFrame(rows)
    df.write.format("delta").mode("append").saveAsTable(CHUNKS_TABLE)



def get_last_run(spark) -> datetime:
    try:
        row = (
            spark.table(LAST_RUN_TABLE)
            .orderBy("run_at", ascending=False)
            .limit(1)
            .collect()
        )
        if row:
            return row[0]["run_at"]
    except Exception:
        pass  # table doesn't exist yet - this is the very first run
    return datetime.now(timezone.utc) - timedelta(days=1)


def record_run(spark, run_at: datetime, articles_fetched: int, chunks_written: int) -> None:
    row = [{
        "run_at": run_at,
        "articles_fetched": articles_fetched,
        "chunks_written": chunks_written,
    }]
    spark.createDataFrame(row).write.format("delta").mode("append").saveAsTable(LAST_RUN_TABLE)