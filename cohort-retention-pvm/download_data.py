"""Download the UCI Online Retail II dataset and convert it to a compressed CSV.

Run:  python download_data.py
      python download_data.py --skip-download   (if you downloaded the file by hand)

Source: Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository.
        https://doi.org/10.24432/C5CG6D  (license: CC BY 4.0)

About 1.07 million transactions from a UK online gift retailer, Dec 2009 to Dec 2011.
The original file is an Excel workbook with one sheet per year; reading it takes a few minutes,
so this script does it once and saves data/online_retail_ii.csv.gz for the notebook.
"""
import argparse
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT = DATA_DIR / "online_retail_ii.csv.gz"
ZIP_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
DATASET_PAGE = "https://archive.ics.uci.edu/dataset/502/online+retail+ii"


def download_zip() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "online_retail_ii.zip"
    print(f"Downloading {ZIP_URL} ...")
    urllib.request.urlretrieve(ZIP_URL, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(RAW_DIR)
    return zip_path


def find_workbook() -> Path:
    matches = sorted(RAW_DIR.rglob("*.xlsx"))
    if not matches:
        raise SystemExit(
            f"No .xlsx file found in {RAW_DIR}.\n"
            f"Download the dataset by hand from {DATASET_PAGE}, unzip it, "
            f"put online_retail_II.xlsx in {RAW_DIR}, then run: python download_data.py --skip-download"
        )
    return matches[0]


def convert(xlsx_path: Path, output: Path = OUTPUT) -> pd.DataFrame:
    print(f"Reading {xlsx_path.name} (all sheets). This can take a few minutes...")
    sheets = pd.read_excel(xlsx_path, sheet_name=None, dtype={"Invoice": str, "StockCode": str})
    df = pd.concat(sheets.values(), ignore_index=True)
    df.to_csv(output, index=False, compression="gzip")
    print(f"Saved {len(df):,} rows from {len(sheets)} sheets to {output}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-download", action="store_true", help="Use an .xlsx already in data/raw/")
    args = parser.parse_args()

    if not args.skip_download:
        try:
            download_zip()
        except Exception as exc:
            raise SystemExit(
                f"Download failed ({exc.__class__.__name__}: {exc}).\n"
                f"Download it by hand from {DATASET_PAGE}, unzip it, put online_retail_II.xlsx in {RAW_DIR}, "
                "then run: python download_data.py --skip-download"
            )
    convert(find_workbook())


if __name__ == "__main__":
    main()
