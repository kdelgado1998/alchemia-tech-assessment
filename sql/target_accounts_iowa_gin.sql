-- Ranked list of target accounts in Iowa for Thameswood Distillers' gin expansion.
--
-- Logic:
--   1. Filter bigquery-public-data.iowa_liquor_sales.sales to gin-related categories only.
--      Categories were identified manually via INFORMATION_SCHEMA + DISTINCT category_name
--      exploration (see assumptions.md for the full list and the "VIRGIN" false-positive
--      caught while filtering with LIKE '%gin%').
--   2. Aggregate by store_number (not store_name/city/county), because store_name has been
--      observed to change over time for the same store_number (e.g. Costco #788 renamed
--      mid-history), which would otherwise split one store's totals across multiple rows.
--      ARRAY_AGG(... ORDER BY date DESC LIMIT 1)[OFFSET(0)] is used to pick the most recent
--      name/city/county for display purposes.
--   3. Exclude any store_number that already exists in raw.crm_accounts (i.e., already a
--      Thameswood customer). store_number is CAST to STRING because pandas inferred it as
--      FLOAT64 when the CRM CSV was loaded, while the public dataset stores it as STRING.
--   4. Rank by total historical gin sale_dollars, descending, and take the top 25.
--
-- Known limitation: this ranking does not currently weight recency of purchase separately
-- from total volume. A store with high historical volume but no recent activity (e.g.
-- LOT-A-SPIRITS, last purchase 2022-10-10) ranks alongside stores active as of 2026-04-30.
-- See assumptions.md for discussion.

CREATE OR REPLACE TABLE `alchemialabs-tech-assessment.analytics.target_accounts_iowa_gin` AS
SELECT
  s.store_number,
  ARRAY_AGG(s.store_name ORDER BY s.date DESC LIMIT 1)[OFFSET(0)] AS store_name,
  ARRAY_AGG(s.city ORDER BY s.date DESC LIMIT 1)[OFFSET(0)] AS city,
  ARRAY_AGG(s.county ORDER BY s.date DESC LIMIT 1)[OFFSET(0)] AS county,
  COUNT(DISTINCT s.invoice_and_item_number) AS num_transactions,
  SUM(s.bottles_sold) AS total_bottles,
  SUM(s.sale_dollars) AS total_sale_dollars,
  MAX(s.date) AS last_purchase_date
FROM `bigquery-public-data.iowa_liquor_sales.sales` s
WHERE s.category_name IN (
  'FLAVORED GINS', 'IMPORTED GINS', 'IMPORTED DRY GINS',
  'AMERICAN SLOE GINS', 'AMERICAN DRY GINS', 'FLAVORED GIN'
)
AND s.store_number NOT IN (
  SELECT CAST(store_number AS STRING)
  FROM `alchemialabs-tech-assessment.raw.crm_accounts`
  WHERE store_number IS NOT NULL
)
GROUP BY s.store_number
ORDER BY total_sale_dollars DESC
LIMIT 25;