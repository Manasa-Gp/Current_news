# Tech News App — Backend

This is the Databricks half of the tech news app. It runs daily, pulls fresh tech articles, and builds the search index the frontend queries.

## What it does, in order

1. Fetches new tech articles from the Currents API (only ones published since the last run)
2. Splits each article into chunks and tags them by category
3. Embeds the chunks and writes everything to a Delta table
4. Keeps a Vector Search index in sync with that table, so the frontend can search it

## Getting started

1. Connect this repo to your Databricks workspace using Databricks Repos
2. Add your Currents API key as a Databricks secret — never commit it to a file here
3. Fill in the ingestion logic under `ingestion/`
4. Set up the Delta Sync Vector Search index (see `index/`)
5. Schedule the pipeline as a daily Databricks Job (see `jobs/`)

Not sure what a file is for? Check `FILES.md` — it walks through every file and folder in this repo.
