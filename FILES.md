# What's in this repo

A quick guide to every file and folder here — what it's for, in plain terms.

## Top level

- **README.md** — the quick-start: what this repo does and how to get it running.
- **.gitignore** — tells git to skip files that shouldn't be committed (secrets, caches, local junk).
- **requirements.txt** — the Python packages this project needs installed.

## Folders

- **ingestion/** — the daily pipeline logic: fetch articles from Currents, chunk them, tag them, embed them, and write the results to a Delta table.
- **index/** — setup and config for the Vector Search index that Delta-syncs off the ingestion table.
- **jobs/** — the Databricks Job/Workflow definition that runs the ingestion pipeline on a schedule.

## Note on secrets

`news_trail.py` in this folder is an earlier test script and has a real API key hardcoded in it — it's kept out of this repo's first commit on purpose. Move that key into a Databricks secret (or a local `.env` that's gitignored) before this file goes anywhere near git, and rotate that key since it's been shared in chat already.
