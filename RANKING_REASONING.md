# Target Account Ranking — Methodology & Reasoning

This document explains how the 25 target accounts below were selected and ranked, and what
that ranking does and doesn't capture. The underlying query lives at
`sql/target_accounts_iowa_gin.sql` and its output is persisted as
`alchemialabs-tech-assessment.analytics.target_accounts_iowa_gin`.

## Methodology, in plain terms

1. **Start from every gin sale in Iowa.** `bigquery-public-data.iowa_liquor_sales.sales` covers
   all wholesale liquor purchases by Iowa retailers, filtered to the 6 confirmed gin categories
   (`FLAVORED GINS`, `IMPORTED GINS`, `IMPORTED DRY GINS`, `AMERICAN SLOE GINS`,
   `AMERICAN DRY GINS`, `FLAVORED GIN`).
2. **Roll up to one row per retailer.** Each retailer (`store_number`) is aggregated across its
   full sales history: total dollars spent on gin, total bottles, number of transactions, and
   the date of its most recent gin purchase.
3. **Remove existing Thameswood customers.** Any retailer already in Thameswood's CRM
   (`raw.crm_accounts`, ~100 accounts) is excluded — the point is to find *new* prospects, not
   re-list current customers.
4. **Rank by total historical gin spend, descending, and take the top 25.**

In short: **these are the 25 Iowa retailers with the largest gin-buying history who are not yet
Thameswood customers.** The ranking is a proxy for "which retailers already prove there's real
demand for gin at their location, at a scale worth pursuing."

## The ranked list

| # | Store # | Retailer | City | County | Total gin sales | Bottles sold | Transactions | Last purchase |
|---|---|---|---|---|---|---|---|---|
| 1 | 2633 | HY-VEE #3 / BDI / DES MOINES | Des Moines | Polk | $4,966,849.79 | 289,591 | 14,213 | 2026-04-30 |
| 2 | 4829 | CENTRAL CITY 2 | Des Moines | Polk | $4,721,806.14 | 259,088 | 12,574 | 2026-04-30 |
| 3 | 2512 | HY-VEE WINE AND SPIRITS #1 (1281) / IOWA CITY | Iowa City | Johnson | $3,029,599.82 | 207,947 | 10,321 | 2026-04-29 |
| 4 | 3814 | COSTCO WHOLESALE #788 / WDM | West Des Moines | Dallas | $2,655,171.12 | 93,026 | 1,131 | 2026-04-28 |
| 5 | 3420 | SAM'S CLUB 6344 / WINDSOR HEIGHTS | Windsor Heights | Polk | $1,602,485.79 | 81,522 | 2,822 | 2026-04-29 |
| 6 | 3385 | SAM'S CLUB 8162 / CEDAR RAPIDS | Cedar Rapids | Linn | $1,579,703.09 | 77,992 | 3,055 | 2026-04-28 |
| 7 | 3773 | BENZ DISTRIBUTING | Cedar Rapids | Linn | $1,486,909.66 | 77,845 | 7,785 | 2026-04-29 |
| 8 | 4677 | COSTCO WHOLESALE #1111 / CORALVILLE | Coralville | Johnson | $1,441,578.64 | 50,486 | 622 | 2026-04-27 |
| 9 | 2670 | HY-VEE FOOD STORE / CORALVILLE | Coralville | Johnson | $1,198,591.30 | 68,747 | 7,189 | 2026-04-29 |
| 10 | 2663 | HY-VEE FOOD STORE / URBANDALE | Urbandale | Polk | $1,144,146.92 | 60,040 | 4,344 | 2026-04-30 |
| 11 | 2619 | HY-VEE FOOD & DRUGSTORE #3 / WDM | West Des Moines | Polk | $1,137,237.26 | 54,907 | 5,674 | 2026-04-29 |
| 12 | 2648 | HY-VEE #4 / WDM | West Des Moines | Polk | $1,044,529.41 | 53,790 | 7,066 | 2026-04-29 |
| 13 | 3354 | SAM'S CLUB 8238 / DAVENPORT | Davenport | Scott | $1,011,953.32 | 56,019 | 2,514 | 2026-04-28 |
| 14 | 2501 | HY-VEE #2 (1018) / AMES | Ames | Story | $958,731.51 | 58,089 | 6,298 | 2026-04-29 |
| 15 | 2614 | HY-VEE #3 FOOD & DRUGSTORE / DAVENPORT | Davenport | Scott | $937,627.34 | 58,035 | 7,662 | 2026-04-29 |
| 16 | 2190 | CENTRAL CITY LIQUOR, INC. | Des Moines | Polk | $931,657.40 | 92,699 | 10,310 | 2026-04-30 |
| 17 | 2603 | HY-VEE WINE AND SPIRITS / BETTENDORF | Bettendorf | Scott | $903,094.99 | 51,965 | 7,602 | 2026-04-28 |
| 18 | 3524 | SAM'S CLUB 6568 / AMES | Ames | Story | $890,095.22 | 43,582 | 1,813 | 2026-04-29 |
| 19 | 3952 | LOT-A-SPIRITS | Bettendorf | Scott | $844,459.06 | 49,146 | 3,967 | **2022-10-10** |
| 20 | 2665 | HY-VEE / WAUKEE | Waukee | Dallas | $840,255.24 | 42,915 | 4,449 | 2026-04-30 |
| 21 | 2622 | HY-VEE FOOD STORE / IOWA CITY | Iowa City | Johnson | $826,416.14 | 46,292 | 5,777 | 2026-04-29 |
| 22 | 2647 | HY-VEE #7 / CEDAR RAPIDS | Cedar Rapids | Linn | $819,916.41 | 43,781 | 7,981 | 2026-04-29 |
| 23 | 3494 | SAM'S CLUB 6514 / WATERLOO | Waterloo | Black Hawk | $787,316.32 | 39,778 | 2,001 | 2026-04-09 |
| 24 | 2502 | HY-VEE WINE AND SPIRITS (1022) / ANKENY | Ankeny | Polk | $778,998.99 | 46,801 | 5,861 | 2026-04-29 |
| 25 | 6242 | WALL TO WALL WINE AND SPIRITS / WDM | West Des Moines | Dallas | $756,237.93 | 28,880 | 1,868 | 2026-01-26 |

## Reading the list: three patterns worth acting on

**1. This is overwhelmingly a retail-chain opportunity, not an independent-shop opportunity.**
15 of the 25 rows are HY-VEE locations, and another 5 are Sam's Club or Costco. Only 5 rows
(Central City 2, Benz Distributing, Central City Liquor, Lot-A-Spirits, Wall to Wall) are
independent retailers. This means the highest-leverage next step is likely a small number of
**chain-level conversations** (HY-VEE corporate, Sam's Club/Costco procurement) rather than 25
separate door-to-door pitches — see the open question on this in `ASSUMPTIONS.md`.

**2. Geographic clustering.** The list concentrates around a handful of metro areas: Des
Moines/West Des Moines/Windsor Heights/Urbandale/Ankeny/Waukee (Polk/Dallas counties — 11 of 25
rows), Iowa City/Coralville (Johnson county — 5 rows), Cedar Rapids (Linn county — 4 rows), and
the Quad Cities/Davenport/Bettendorf area (Scott county — 5 rows). A sales approach organized by
region, rather than store-by-store, would likely be more efficient than the flat ranking implies.

**3. One clear outlier on recency.** Row 19, Lot-A-Spirits, last sold gin in **October 2022** —
over 3.5 years before every other store on this list, all of which sold gin as recently as
January–April 2026. Its $844K in historical value earned it a top-25 spot on total volume alone,
but it may no longer be an active liquor retailer, or may have exited the gin category
altogether. This is flagged explicitly rather than silently ranked as equivalent to the other 24
rows — see the ranking-signal question in `ASSUMPTIONS.md`.

## What this ranking does not capture

- **No recency weighting in the score itself.** As shown above, one row (Lot-A-Spirits) ranks
  by historical volume despite years of inactivity. The ranking is total value only; recency is
  reported as a column but doesn't affect the rank.
- **No purchasing-decision structure.** The list ranks individual store locations, not the
  companies that may own several of them (HY-VEE, Sam's Club, Costco).
- **No fit signal beyond volume.** The ranking doesn't account for whether a retailer's existing
  gin assortment (categories, price points) matches Thameswood's product line
  (`raw.product_catalogue` — London Dry Gin and Contemporary Gin, £32.50–£44.00 list price), only
  that the retailer sells a meaningful volume of gin generally.

These are documented as open questions and future improvements in `ASSUMPTIONS.md`, rather than
resolved unilaterally, since the right answer depends on Thameswood's go-to-market strategy.