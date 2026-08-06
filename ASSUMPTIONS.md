# Assumptions

## Data interpretation

- **CRM exports are full daily snapshots, not deltas.** Confirmed by comparing row counts for
  `crm_accounts` across three dates roughly a month apart (constant at ~103 rows) while
  `last_activity_date` for a tracked record (`ACC-0001`) advanced between snapshots. Only the
  most recent file per entity was ingested — the ~180 historical files per entity were not
  needed to reconstruct current state, and weren't ingested.
- **`store_number` is the correct join key between the CRM and the public Iowa dataset.**
  Verified manually: `ACC-0001` / "Keokuk Spirits" in the CRM matches `store_number = '2191'` /
  "KEOKUK SPIRITS" in `bigquery-public-data.iowa_liquor_sales.sales`.
- **"Gin" category matching uses an explicit list, not a wildcard.** `category_name` values
  relevant to gin were found by inspecting `SELECT DISTINCT category_name ... WHERE
  category_name LIKE '%gin%'`, which also surfaced a false positive
  (`PUERTO RICO & VIRGIN ISLANDS RUM`, matching on "vir-GIN"). The final query uses an explicit
  `IN (...)` list of the 6 confirmed categories instead of a pattern match, to avoid silently
  including or excluding categories in the future.
- **Ranking is based on total historical gin `sale_dollars`,** not bottle count, transaction
  count, or a recency-weighted score. This was a judgment call — dollar value seemed like the
  most direct proxy for "attractiveness as a target account" for a premium gin producer, but
  transaction frequency or recency could reasonably be weighted instead or in addition.
- **All 100 CRM accounts (post-dedup) were treated as existing customers to exclude,**
  regardless of their `status` field value. The CRM data showed `status = Active` for the
  records inspected; I did not check whether any accounts have a different status (e.g.
  "Churned") that might mean they're actually re-approachable. Would confirm with the client.

## Data quality decisions

- 3 duplicate `crm_accounts` records (differing only by trailing whitespace in `account_name`)
  were deduplicated, keeping the first occurrence. Assumed this was a source-system export
  artifact, not intentional.
- CSV encoding was forced to UTF-8 on read to fix a mojibake issue (`Â£` instead of `£`).
  Assumed UTF-8 was the intended encoding, based on it resolving the visual issue correctly.
- `store_number` was `CAST` to `STRING` when joining against the public dataset, because pandas
  inferred it as `FLOAT64` from the CRM CSV while the public dataset stores it as `STRING`.
  Assumed the CAST doesn't introduce mismatches (e.g. `2191.0` → `"2191.0"` vs `"2191"`) —
  verified via the final `NOT IN` exclusion producing zero overlap with the CRM, and via the
  standalone verification query in `tests/test_target_accounts.py`.

## What I'd ask the client / Alchemia Labs

- Is dollar value the right primary ranking signal, or should recency/frequency of purchase be
  weighted more heavily? (See the "Known limitations" note in the README — one store's last gin
  purchase was in Oct 2022 but still ranks in the current top 25 by total value.)
- Should any non-`Active` CRM accounts be treated as open targets rather than excluded?
- Is there a target account count constraint beyond the store level (e.g. should multi-location
  chains like HY-VEE, which account for many of the top 25 rows, be treated as one relationship
  or negotiated per-location)?

## What I'd do differently with more time

- Migrate the transform layer to dbt, per the brief's recommendation, for lineage and built-in
  testing.
- Add an explicit BigQuery load schema instead of relying on pandas type inference, to avoid the
  `store_number` type mismatch at the source rather than patching it with a `CAST` downstream.
- Normalize the mixed date formats in `crm_opportunities` (`DD/MM/YYYY` vs ISO), even though the
  current ranking query doesn't consume that field.
- Add a recency-weighted or decayed ranking score instead of ranking by raw total value alone.
- Ingest full CRM history (not just the latest snapshot) if trend analysis (e.g. "when did this
  account's activity drop off") becomes a requirement.