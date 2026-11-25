# Customer Cohort Retention + Price-Volume-Mix Bridge

## The problem

An online gift retailer wants to know two things:

1. **Do customers come back?** How retention looks by the month customers first bought, and whether newer cohorts retain better or worse.
2. **Why did revenue change year over year?** How much came from price, volume and product mix, and how much from new and discontinued products.

## Data

[Online Retail II](https://doi.org/10.24432/C5CG6D) from the UCI Machine Learning Repository: 1,067,371 transaction lines
from a UK online gift retailer, 1 Dec 2009 to 9 Dec 2011 (CC BY 4.0). Many customers are wholesalers.

Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

The raw data isn't stored in this repo; `python download_data.py` downloads and converts it. If the UCI download
doesn't work, `python download_data.py --mirror` pulls the same 1,067,371 rows from the copy bundled in the
[onlineretail2](https://github.com/allanvc/onlineretail2) R package (the results here were produced from that copy).
Without either, the notebook falls back to `data/sample_transactions.csv`, a small **synthetic** file with the same columns.

## Findings

**Cleaning**
- Dropping cancellation lines alone (the usual approach) leaves the original sales in the data. The two biggest "sales" in the dataset, orders worth **£168k and £77k**, were both cancelled within about 15 minutes.
- Matching each cancellation to the sale it reverses (same customer, product and quantity) removes **6,332 sales lines worth £673k**.
- Revenue is concentrated: the **top 1% of customers bring in 31%** of revenue and the top 10% bring in 63%.

**Retention** (cohorts through November 2011; the partial December 2011 is excluded)
- About **20 to 24% of new customers buy again the next month**, and roughly 13 to 25% are still buying a year later.
- The **December 2009 "cohort" looks twice as loyal (38% at month 12 vs. 18%)** only because the data starts that month, so existing customers show up as "new."
- 2011 cohorts did a bit better than 2010 in month 1 (24% vs. 20%); by months 3 and 6 the gap is about a point or less.
- By revenue, the median 2010 cohort keeps **21% of its first-month revenue** after a year vs. 15% of its customers, so the customers who stay spend more.

**Revenue bridge** (Dec 2009–Nov 2010 → Dec 2010–Nov 2011)

| Component | £ | % of base |
|---|---|---|
| Base revenue | 9,218,123 | 100.0% |
| Price | −146,306 | −1.6% |
| Volume | −1,424,039 | −15.4% |
| Mix | +474,655 | +5.1% |
| New products (675) | +1,962,224 | +21.3% |
| Discontinued products (976) | −706,727 | −7.7% |
| **Current revenue** | **9,377,931** | **101.7%** |

Revenue looks flat (+1.7%), but units of continuing products fell **16.7%**. New products covered the gap. Comparing calendar years instead would show a **−1.5% decline that isn't real**, because 2011 is missing most of December.

## Walk-through (how to explain it)

- **Cleaning is logged step by step** (`clean_transactions` in `retail.py`), so every removed row is accounted for. The key judgment call is cancellations: a cancellation line is a refund, not a deletion of the original sale, so I match refunds to the sales they reverse with `merge_asof` (most recent earlier sale with the same customer, product and quantity). Partial cancellations aren't matched, a known limitation.
- **Missing customer IDs (about 23% of rows)** are dropped for cohorts, because a sale with no customer can't be assigned to one. They're kept for the revenue bridge, because the bridge works at the product level.
- **Cohorts** group customers by first-purchase month. The retention table divides the number of customers active N months later by the cohort's size. I cut the data at 30 Nov 2011, because December 2011 only has 9 days and would make every cohort look worse in that column.
- **Two censoring traps:** the first cohort is inflated by customers who started before the data does (left-censoring), and recent cohorts have blank columns because those months haven't happened yet (right-censoring).
- **PVM convention:** for products sold in both periods, price = Σ(P1 − P0)·Q1, volume = (ΣQ1 − ΣQ0) × average base price, mix = ΣQ1·P0 − ΣQ1 × average base price. New and discontinued products are separate lines. The function checks that the bridge adds up exactly.
- **Caveat on price:** P is average realized price per unit, so it also moves with quantity discounts, not just list prices.

## How to run

```bash
python download_data.py          # about 45 MB download, then a few minutes to convert
# or: pip install pyreadr && python download_data.py --mirror
jupyter notebook analysis.ipynb
```
