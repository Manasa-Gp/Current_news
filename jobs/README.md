# Deploying the daily job

`daily_pipeline_job.json` is a Databricks Jobs API job definition — it runs
`ingestion/pipeline.py` once a day at 6am America/New_York, on serverless
compute (no cluster config needed, `environment_key` handles dependencies).

## Before deploying

Replace both `<your-username>/<this-repo-name>` placeholders with this
repo's actual path once it's connected via Databricks Repos (Workspace ->
Repos -> your repo -> right-click a file -> Copy path).

## Deploy it

Either paste the JSON into the Databricks UI (Workflows -> Create Job ->
JSON view), or from a terminal with the Databricks CLI configured:

    databricks jobs create --json @jobs/daily_pipeline_job.json

## Before the first real run

Run `index/setup_index.py` once, manually, from a notebook — the job
above assumes the Vector Search endpoint and index already exist; it only
keeps them in sync, it doesn't create them.
