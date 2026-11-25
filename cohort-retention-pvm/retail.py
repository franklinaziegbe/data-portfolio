"""Helpers for the Online Retail II cohort and PVM analysis."""
from pathlib import Path

import pandas as pd

RAW_COLUMNS = {
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
}


def load_transactions(path: Path) -> pd.DataFrame:
    """Load raw transactions and standardize column names and types."""
    df = pd.read_csv(path, dtype={"Invoice": str, "StockCode": str})
    df = df.rename(columns={"CustomerID": "Customer ID"})  # some copies of the dataset drop the space
    missing = set(RAW_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing expected columns: {sorted(missing)}")
    df = df.rename(columns=RAW_COLUMNS)[list(RAW_COLUMNS.values())]
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["customer_id"] = df["customer_id"].astype("Int64").astype("string")
    return df


def find_reversed_sales(df: pd.DataFrame) -> pd.Index:
    """Index labels of sales that a later cancellation fully reverses.

    A cancellation matches the most recent earlier sale with the same customer, product and quantity.
    Partial cancellations (a different quantity) aren't matched; that's a known limitation.
    """
    is_cancel = df["invoice"].str.upper().str.startswith("C", na=False)
    has_id = df["customer_id"].notna()
    keys = ["customer_id", "stock_code", "units"]

    cancels = (df[is_cancel & has_id & (df["quantity"] < 0)]
               .assign(units=lambda d: -d["quantity"])[keys + ["invoice_date"]]
               .sort_values("invoice_date"))
    sales = (df[~is_cancel & has_id & (df["quantity"] > 0)]
             .assign(units=lambda d: d["quantity"])[keys + ["invoice_date"]]
             .reset_index(names="sale_idx")
             .sort_values("invoice_date"))
    for frame in (cancels, sales):
        frame["customer_id"] = frame["customer_id"].astype(str)

    matched = pd.merge_asof(cancels, sales, on="invoice_date", by=keys, direction="backward")
    return pd.Index(matched["sale_idx"].dropna().astype(int).unique())


def clean_transactions(df: pd.DataFrame, require_customer: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the cleaning rules one at a time and log how many rows each rule removes.

    Rules (each one is a judgment call):
      1. Exact duplicate rows
      2. Sales fully reversed by a later cancellation (same customer, product and quantity).
         Without this, dropping the cancellation rows alone leaves the original sale in the data.
      3. Cancellations (invoice starts with "C")
      4. Quantity <= 0
      5. Price <= 0
      6. Missing customer ID (only when require_customer=True: needed for cohorts, not for product-level revenue)
      7. Non-product stock codes like POST, DOT, M, BANK CHARGES (kept: codes starting with 5 digits)

    Returns the cleaned data (with a revenue column) and a log of rows removed per rule.
    """
    log = [{"step": "Raw rows", "rows_removed": 0, "rows_left": len(df)}]

    def record(name: str, before: int, after: pd.DataFrame) -> None:
        log.append({"step": name, "rows_removed": before - len(after), "rows_left": len(after)})

    out = df.drop_duplicates()
    record("Exact duplicate rows", len(df), out)

    before = len(out)
    out = out.drop(index=find_reversed_sales(out))
    record("Sales reversed by a later cancellation", before, out)

    steps = [
        ("Cancellations (invoice starts with C)", lambda d: d["invoice"].str.upper().str.startswith("C", na=False)),
        ("Quantity <= 0", lambda d: d["quantity"] <= 0),
        ("Price <= 0", lambda d: d["price"] <= 0),
    ]
    if require_customer:
        steps.append(("Missing customer ID", lambda d: d["customer_id"].isna()))
    steps.append(("Non-product stock codes", lambda d: ~d["stock_code"].str.match(r"^\d{5}", na=False)))

    for name, rule in steps:
        before = len(out)
        out = out[~rule(out).fillna(False)]
        record(name, before, out)

    out = out.assign(revenue=out["quantity"] * out["price"]).reset_index(drop=True)
    return out, pd.DataFrame(log)


def add_cohorts(df: pd.DataFrame) -> pd.DataFrame:
    """Add order_month, cohort_month (first purchase month) and months_since_first."""
    out = df.copy()
    out["order_month"] = out["invoice_date"].dt.to_period("M")
    out["cohort_month"] = out.groupby("customer_id")["order_month"].transform("min")
    order_idx = out["invoice_date"].dt.year * 12 + out["invoice_date"].dt.month
    out["months_since_first"] = order_idx - order_idx.groupby(out["customer_id"]).transform("min")
    return out


def retention_table(df: pd.DataFrame) -> pd.DataFrame:
    """Share of each cohort's customers who bought again N months after their first month.

    Rows: cohort_month. Columns: months_since_first. Values: 0-1.
    """
    counts = (
        df.groupby(["cohort_month", "months_since_first"])["customer_id"]
        .nunique()
        .unstack(fill_value=0)
    )
    cohort_size = counts[0]
    table = counts.div(cohort_size, axis=0)
    # Months that haven't happened yet for recent cohorts should be blank, not 0%.
    last_month = df["order_month"].max()
    for cohort in table.index:
        max_offset = (last_month - cohort).n
        table.loc[cohort, table.columns > max_offset] = float("nan")
    return table


def pvm_bridge(df: pd.DataFrame, period_col: str, base: str, current: str, by: str = "stock_code") -> pd.Series:
    """Price-volume-mix bridge from the base period to the current period.

    Convention used here (other conventions exist; this one is common in deal work):
    P is each product's average realized price in a period (revenue / quantity), Q its quantity.

    For products sold in BOTH periods ("continuing" products):
        avg_base_price = base revenue / base quantity, both over continuing products only
        price  = sum over products of (P1 - P0) * Q1
        volume = (total Q1 - total Q0) * avg_base_price
        mix    = (sum of Q1 * P0) - (total Q1 * avg_base_price)
    new_products  = current-period revenue from products not sold in the base period
    lost_products = minus the base-period revenue from products not sold in the current period

    Returns a Series in bridge order:
        base_revenue, price, volume, mix, new_products, lost_products, current_revenue
    and raises if the pieces don't add up.
    """
    sub = df[df[period_col].isin([base, current])]
    by_product = sub.groupby([period_col, by]).agg(revenue=("revenue", "sum"), quantity=("quantity", "sum"))
    b = by_product.loc[base]
    c = by_product.loc[current]

    both = b.index.intersection(c.index)
    p0 = b.loc[both, "revenue"] / b.loc[both, "quantity"]
    p1 = c.loc[both, "revenue"] / c.loc[both, "quantity"]
    q0 = b.loc[both, "quantity"]
    q1 = c.loc[both, "quantity"]
    avg_base_price = b.loc[both, "revenue"].sum() / q0.sum()

    bridge = pd.Series({
        "base_revenue": b["revenue"].sum(),
        "price": ((p1 - p0) * q1).sum(),
        "volume": (q1.sum() - q0.sum()) * avg_base_price,
        "mix": (q1 * p0).sum() - q1.sum() * avg_base_price,
        "new_products": c.loc[c.index.difference(b.index), "revenue"].sum(),
        "lost_products": -b.loc[b.index.difference(c.index), "revenue"].sum(),
        "current_revenue": c["revenue"].sum(),
    })
    gap = bridge.iloc[0] + bridge.iloc[1:-1].sum() - bridge.iloc[-1]
    if abs(gap) > 0.01:
        raise AssertionError(f"Bridge doesn't reconcile (off by {gap:,.2f})")
    return bridge
