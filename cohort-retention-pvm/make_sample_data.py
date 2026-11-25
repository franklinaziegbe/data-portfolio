"""Create a small SYNTHETIC sample with the same columns as Online Retail II.

This only exists so the notebook runs before you download the real dataset.
The numbers are made up. Don't report findings from it.

Run:  python make_sample_data.py   ->  data/sample_transactions.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 11
N_CUSTOMERS = 300
N_PRODUCTS = 60
START, END = pd.Timestamp("2009-12-01"), pd.Timestamp("2011-12-09")
OUTPUT = Path(__file__).parent / "data" / "sample_transactions.csv"


def main() -> None:
    rng = np.random.default_rng(SEED)
    months = pd.period_range(START, END, freq="M")

    products = pd.DataFrame({
        "StockCode": [f"{20000 + i * 37}" + ("A" if i % 7 == 0 else "") for i in range(N_PRODUCTS)],
        "Description": [f"SAMPLE PRODUCT {i:02d}" for i in range(N_PRODUCTS)],
        "base_price": rng.uniform(0.5, 12, N_PRODUCTS).round(2),
        "launch_month": rng.choice(len(months), N_PRODUCTS, p=None) * (rng.random(N_PRODUCTS) < 0.2),
        "retire_month": np.where(rng.random(N_PRODUCTS) < 0.15, rng.integers(8, len(months), N_PRODUCTS), len(months)),
    })
    countries = ["United Kingdom"] * 8 + ["Germany", "France", "EIRE", "Netherlands"]

    rows, invoice_no = [], 489000
    for cust in range(N_CUSTOMERS):
        customer_id = 12000 + cust
        country = rng.choice(countries)
        first = int(min(rng.exponential(7), len(months) - 1))
        for m in range(first, len(months)):
            age = m - first
            p_buy = 1.0 if age == 0 else 0.45 * np.exp(-age / 10) + 0.08
            if months[m].month in (11, 12):
                p_buy *= 1.4
            if rng.random() > p_buy:
                continue
            invoice_no += 1
            day = pd.Timestamp(months[m].start_time) + pd.Timedelta(days=int(rng.integers(0, 28)), hours=int(rng.integers(8, 18)))
            if day > END:
                continue
            live = products[(products["launch_month"] <= m) & (products["retire_month"] > m)]
            for _, prod in live.sample(int(rng.integers(1, 9)), random_state=int(rng.integers(1e9))).iterrows():
                price = prod["base_price"] * (1.06 if day.year == 2011 else 1.0) * rng.choice([1.0, 0.85], p=[0.8, 0.2])
                rows.append([str(invoice_no), prod["StockCode"], prod["Description"], int(rng.integers(1, 25)),
                             day, round(price, 2), float(customer_id), country])

    df = pd.DataFrame(rows, columns=["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate",
                                     "Price", "Customer ID", "Country"])

    # Add the kinds of messiness the real data has.
    n = len(df)
    cancels = df.sample(frac=0.02, random_state=1).assign(Invoice=lambda d: "C" + d["Invoice"],
                                                           Quantity=lambda d: -d["Quantity"])
    no_id = df.sample(frac=0.03, random_state=2).assign(**{"Customer ID": np.nan})
    postage = df.sample(frac=0.01, random_state=3).assign(StockCode="POST", Description="POSTAGE", Quantity=1, Price=18.0)
    zero_price = df.sample(n=10, random_state=4).assign(Price=0.0)
    dupes = df.sample(n=15, random_state=5)
    df = pd.concat([df, cancels, no_id, postage, zero_price, dupes], ignore_index=True).sort_values("InvoiceDate")

    OUTPUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(df):,} synthetic rows ({n:,} clean + messy extras) to {OUTPUT.name}")


if __name__ == "__main__":
    main()
