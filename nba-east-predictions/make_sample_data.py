"""Create MADE-UP sample standings, predictions and snapshots so the notebook runs before real data exists.

None of this is real NBA data. Replace it by running fetch_standings.py and filling in data/predictions.csv.

Run:  python make_sample_data.py
"""
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from score import EAST_TEAMS

DATA_DIR = Path(__file__).parent / "data"
SNAPSHOT_DIR = DATA_DIR / "sample_snapshots"


def main() -> None:
    rng = np.random.default_rng(7)
    order = list(rng.permutation(EAST_TEAMS))
    games = 18
    wins = sorted(rng.integers(3, 16, 15), reverse=True)
    standings = pd.DataFrame({"rank": range(1, 16), "team": order, "wins": wins})
    standings["losses"] = games - standings["wins"]
    standings["win_pct"] = (standings["wins"] / games).round(3)
    standings.to_csv(DATA_DIR / "sample_standings.csv", index=False)

    picks = {"rank": range(1, 11)}
    for name in ["Frank", "Friend A", "Friend B"]:
        noisy = sorted(order, key=lambda t: order.index(t) + rng.normal(0, 3))
        picks[name] = noisy[:10]
    pd.DataFrame(picks).to_csv(DATA_DIR / "sample_predictions.csv", index=False)

    # Four weekly snapshots that drift toward the final sample standings.
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    final_day = date(2026, 11, 23)
    for weeks_back, noise in [(3, 4.0), (2, 3.0), (1, 1.5), (0, 0.0)]:
        snap_order = sorted(order, key=lambda t: order.index(t) + rng.normal(0, noise)) if noise else order
        snap = pd.DataFrame({"rank": range(1, 16), "team": snap_order})
        day = final_day - timedelta(weeks=weeks_back)
        snap.to_csv(SNAPSHOT_DIR / f"east_standings_{day.isoformat()}.csv", index=False)

    print("Wrote sample_standings.csv, sample_predictions.csv and 4 files in data/sample_snapshots/ (all made up)")


if __name__ == "__main__":
    main()
