# Customer Cohort Retention + Price-Volume-Mix Bridge

## The problem

An online gift retailer wants to know two things:

1. **Do customers come back?** How retention looks by the month customers first bought, and whether newer cohorts retain better or worse.
2. **Why did revenue change year over year?** How much came from charging more (price), selling more (volume), and selling a different product mix (mix), plus new and discontinued products.

## Data

[Online Retail II](https://doi.org/10.24432/C5CG6D) from the UCI Machine Learning Repository: about 1.07 million transactions
from a UK online retailer, December 2009 to December 2011 (CC BY 4.0). Many customers are wholesalers.

Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

The real data isn't stored in this repo. `python download_data.py` downloads and converts it.
Until then, the notebook runs on `data/sample_transactions.csv`, a small **synthetic** file with the same columns (made by `make_sample_data.py`).

## Approach

- **Cleaning** (`retail.py`): duplicates, cancellations, returns, zero prices, missing customer IDs and non-product codes, with a log of rows removed at each step
- **Cohorts:** group customers by first purchase month and track the share who buy again in each later month
- **PVM bridge:** split the revenue change between two periods into price, volume, mix, new products and lost products

<!-- TODO (Frank): Note any cleaning rules you changed and why, and the PVM convention you used. -->

## Findings

<!-- TODO (Frank): 3–5 bullets with real numbers from the full dataset. -->

## How to run

```bash
python download_data.py          # about 45 MB download, then a few minutes to convert
jupyter notebook analysis.ipynb
```
