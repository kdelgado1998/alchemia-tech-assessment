# Alchemia Labs — Technical Assessment

Revenue-ops data pipeline integrating third-party Iowa liquor sales data with Thameswood
Distillers' CRM exports to identify and rank the top 25 target accounts for their Iowa gin
expansion.

## Overview

Thameswood Distillers (a London gin producer) has ~100 existing accounts across Iowa liquor
retailers. This project answers: **which Iowa retailers should they approach next?**

The pipeline:
1. Extracts CRM data (accounts, contacts, opportunities) and a product catalogue from a GCS
   bucket.
2. Loads them, cleaned, into BigQuery as raw tables.
3. Queries the public `bigquery-public-data.iowa_liquor_sales.sales` dataset, filters to
   gin-related categories, aggregates by retailer, excludes existing customers, and ranks the
   remaining retailers by historical gin sale volume.
4. Persists the result as a modelled table: `analytics.target_accounts_iowa_gin`.

## Architecture

```
extract/
  extract_crm.py         # CRM: accounts, contacts, opportunities (CSV, GCS)
  extract_catalogue.py   # Product catalogue (Parquet, GCS)
load/
  load_to_bigquery.py    # Loads cleaned DataFrames into BigQuery (raw dataset)
sql/
  target_accounts_iowa_gin.sql   # Final ranking query (creates analytics table)
tests/
  test_clean_dataframe.py    # Unit tests for cleaning logic (no network required)
  test_target_accounts.py    # Integration tests against the live BigQuery result
```

BigQuery datasets:
- `raw` — CRM and catalogue data, loaded as-is after basic cleaning (encoding fix, whitespace
  trim, deduplication).
- `analytics` — modelled output. Currently one table: `target_accounts_iowa_gin`, the final
  ranked list of 25 accounts.

## Why Python instead of dbt

The brief recommends dbt for the transformation layer. I used a Python-based pipeline instead,
due to time constraints and limited prior SQL/dbt experience — I prioritized a correct,
well-tested pipeline over learning a new tool under deadline pressure. Happy to discuss how I'd
migrate this to dbt with more time; the SQL in `sql/` is already written as a standalone,
version-controlled query, which would map fairly directly onto a dbt model.

## How to run

**Requirements:** Python 3.13, a GCP project with BigQuery + Cloud Storage APIs enabled, and a
service account key with `roles/bigquery.dataEditor` and `roles/bigquery.jobUser`.

```bash
pip install -r requirements.txt   # pandas, google-cloud-storage, google-cloud-bigquery, pytest

# Set credentials (Windows PowerShell example)
$env:GOOGLE_APPLICATION_CREDENTIALS = "path\to\your-key.json"

# Load raw CRM + catalogue data into BigQuery
python load/load_to_bigquery.py

# Run the final ranking query (in BigQuery Studio, or via bq CLI)
# -> sql/target_accounts_iowa_gin.sql

# Run tests
python -m pytest tests/ -v
```

## Pipeline design notes

- **Extraction is re-runnable, not a one-off copy.** `get_latest_file()` finds the most recent
  CRM export by listing the bucket and taking the max filename (dates are `YYYY-MM-DD`, so
  alphabetical order matches chronological order) — no hardcoded filenames. Re-running the
  pipeline picks up new exports automatically.
- **CRM exports are full daily snapshots, not deltas.** Confirmed by comparing row counts and a
  tracked record (`ACC-0001`) across three dates roughly a month apart: row counts stayed
  constant (~103) while `last_activity_date` advanced. This means only the latest file per
  entity is needed to reconstruct current state — the ~180 historical files per entity were not
  ingested.
- **Loads use `WRITE_TRUNCATE`.** Each run replaces the raw tables entirely, consistent with the
  snapshot nature of the source data (there's no append/merge logic, since "yesterday's" file is
  superseded by "today's" full snapshot, not additive to it).

## Data quality issues found and how they were handled

| Issue | Where | Fix |
|---|---|---|
| Mojibake encoding (`Â£` instead of `£`) | CRM CSVs | Forced `encoding="utf-8"` in `pd.read_csv` |
| 3 duplicate accounts (trailing whitespace in name, e.g. `"Keokuk Spirits "`) | `crm_accounts` (`ACC-0001`, `ACC-0035`, `ACC-0060`) | `.str.strip()` on all text columns, then `drop_duplicates(subset=id_column, keep="first")` |
| Mixed date formats (`DD/MM/YYYY` vs ISO `YYYY-MM-DD`) in the same table | `crm_opportunities` | Not yet normalized — out of scope for the current ranking query, which doesn't consume `expected_close_date`. Would normalize explicitly before any date-based analysis. |
| `store_number` type mismatch: `STRING` in the public dataset vs. `FLOAT64` after pandas auto-inferred it from the CRM CSV | Join between `sales` and `raw.crm_accounts` | `CAST(store_number AS STRING)` in the exclusion subquery. Root-cause fix (not yet applied): specify an explicit BigQuery load schema instead of relying on pandas type inference. |
| `store_name`/`city`/`county` inconsistent over time for the same `store_number` (e.g. Costco #788 renamed mid-history) | Public Iowa dataset | Aggregated by `store_number` only (not by name/city/county); used `ARRAY_AGG(... ORDER BY date DESC LIMIT 1)[OFFSET(0)]` to pick the most recent display name per store |
| Inconsistent category naming: `FLAVORED GINS` vs `FLAVORED GIN` (plural/singular); `LIKE '%gin%'` false-positives on `PUERTO RICO & VIRGIN ISLANDS RUM` | Public Iowa dataset, `category_name` | Explicit `IN (...)` list of the 6 confirmed gin categories, found via `SELECT DISTINCT category_name` inspection rather than a wildcard match |

## Known limitations / what I'd do with more time

- The ranking currently orders strictly by total historical `sale_dollars`. It doesn't separately
  weight purchase recency — a store with high historical volume but no recent activity (e.g. one
  store's last gin purchase was in Oct 2022) ranks alongside stores active as of Apr 2026. I'd
  add a recency-weighted or decayed score, or at minimum a secondary sort/filter on
  `last_purchase_date`.
- `expected_close_date` in `crm_opportunities` is not normalized to a single date format — not
  needed for the current query, but would need addressing before any downstream use of that
  field.
- Migrate the transform layer to dbt for lineage, testing, and documentation generation, per the
  brief's recommendation.
- Add an explicit BigQuery load schema (rather than pandas-inferred types) to avoid the
  `store_number` type mismatch at the source.
- Only the most recent snapshot per CRM entity is ingested. If historical trend analysis becomes
  a requirement (e.g. "when did this account go inactive"), the pipeline would need to ingest and
  version the full history instead of just the latest file.

## AI use

This project was built with extensive use of Claude (Anthropic) as a pairing/tutoring partner.
See `AI_USAGE.md` for the full breakdown of how it was used, prompts, and specific instances
where it made mistakes and how those were caught and corrected.