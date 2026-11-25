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
    missing = set(RAW_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing expected columns: {sorted(missing)}")
    df = df.rename(columns=RAW_COLUMNS)[list(RAW_COLUMNS.values())]
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["customer_id"] = df["customer_id"].astype("Int64").astype("string")
    return df


def clean_transactions(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the cleaning rules one at a time and log how many rows each rule removes.

    Rules (each one is a judgment call worth reviewing):
      1. Exact duplicate rows
      2. Cancellations (invoice starts with "C")
      3. Quantity <= 0
      4. Price <= 0
      5. Missing customer ID (can't be assigned to a cohort)
      6. Non-product stock codes like POST, DOT, M, BANK CHARGES (kept: codes starting with 5 digits)

    Returns the cleaned data (with a revenue column) and a log of rows removed per rule.
    """
    steps = [
        ("Exact duplicate rows", lambda d: d.duplicated()),
        ("Cancellations (invoice starts with C)", lambda d: d["invoice"].str.upper().str.startswith("C", na=False)),
        ("Quantity <= 0", lambda d: d["quantity"] <= 0),
        ("Price <= 0", lambda d: d["price"] <= 0),
        ("Missing customer ID", lambda d: d["customer_id"].isna()),
        ("Non-product stock codes", lambda d: ~d["stock_code"].str.match(r"^\d{5}", na=False)),
    ]
    log = [{"step": "Raw rows", "rows_removed": 0, "rows_left": len(df)}]
    out = df
    for name, rule in steps:
        mask = rule(out).fillna(False)
        out = out[~mask]
        log.append({"step": name, "rows_removed": int(mask.sum()), "rows_left": len(out)})
    out = out.assign(revenue=out["quantity"] * out["price"]).reset_index(drop=True)
    return out, pd.DataFrame(log)


def add_cohorts(df: pd.DataFrame) -> pd.DataFrame:
    """Add order_month, cohort_month (first purchase month) and months_since_first."""
    out = df.copy()
    out["order_month"] = out["invoice_date"].dt.to_period("M")
    out["cohort_month"] = out.groupby("customer_id")["order_month"].transform("min")
    out["months_since_first"] = (out["order_month"] - out["cohort_month"]).apply(lambda x: x.n)
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
    """TODO (Frank): Build a price-volume-mix bridge from the base period to the current period.

    Parameters
    ----------
    df : cleaned transactions with a column that labels each row's period (period_col)
    period_col : name of that column, e.g. "period"
    base, current : the two period labels to compare, e.g. "2010" and "2011"
    by : the product level for price and mix (stock_code is the natural choice)

    Returns
    -------
    A Series with these components, in order:
        base_revenue, price, volume, mix, new_products, lost_products, current_revenue

    One common convention (pick one, document it, and stick to it).
    P is each product's average realized price in a period (revenue / quantity), Q its quantity.
        For products sold in BOTH periods ("continuing" products):
            avg_base_price = base revenue / base quantity, both over continuing products only
            price  = sum over products of (P1 - P0) * Q1
            volume = (total Q1 - total Q0) * avg_base_price
            mix    = (sum of Q1 * P0) - (total Q1 * avg_base_price)
        new_products  = current-period revenue from products not sold in the base period
        lost_products = minus the base-period revenue from products not sold in the current period

    The bridge must reconcile:
        base_revenue + price + volume + mix + new_products + lost_products == current_revenue
    """
    raise NotImplementedError("TODO (Frank): implement the PVM bridge. See the docstring for the method.")
