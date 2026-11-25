"""Fetch the current NBA Eastern Conference standings and save them.

Run:  python fetch_standings.py
      python fetch_standings.py --season 2026-27

Writes:
  data/east_standings.csv                    latest standings (used by score.py and the notebook)
  data/snapshots/east_standings_<date>.csv   a dated copy, so you can track the leaderboard over the season

Needs internet access. stats.nba.com can be slow or block requests now and then; if it fails,
wait a minute and try again, or fill in data/east_standings.csv by hand (same columns).
"""
import argparse
from datetime import date
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguestandingsv3

DATA_DIR = Path(__file__).parent / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"


def fetch_east_standings(season: str | None = None, timeout: int = 60) -> pd.DataFrame:
    """Return East standings as a DataFrame with columns rank, team, wins, losses, win_pct."""
    kwargs = {"timeout": timeout}
    if season:
        kwargs["season"] = season
    response = leaguestandingsv3.LeagueStandingsV3(**kwargs)
    df = response.standings.get_data_frame()

    east = df[df["Conference"] == "East"].copy()
    east["team"] = east["TeamCity"].str.strip() + " " + east["TeamName"].str.strip()
    east = east.rename(columns={"PlayoffRank": "rank", "WINS": "wins", "LOSSES": "losses", "WinPCT": "win_pct"})
    east = east[["rank", "team", "wins", "losses", "win_pct"]].sort_values("rank").reset_index(drop=True)
    return east


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", help="Season like 2026-27. Defaults to the current season.")
    args = parser.parse_args()

    try:
        east = fetch_east_standings(args.season)
    except Exception as exc:  # network errors, timeouts, blocked requests
        raise SystemExit(
            f"Couldn't fetch standings ({exc.__class__.__name__}: {exc}).\n"
            "stats.nba.com is sometimes slow or blocks requests. Try again in a minute, "
            "or fill in data/east_standings.csv by hand with columns: rank, team, wins, losses, win_pct."
        )

    if len(east) != 15:
        print(f"Warning: expected 15 East teams, got {len(east)}.")

    DATA_DIR.mkdir(exist_ok=True)
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    east.to_csv(DATA_DIR / "east_standings.csv", index=False)
    snapshot_path = SNAPSHOT_DIR / f"east_standings_{date.today().isoformat()}.csv"
    east.to_csv(snapshot_path, index=False)

    print(east.to_string(index=False))
    print(f"\nSaved data/east_standings.csv and {snapshot_path.relative_to(Path(__file__).parent)}")


if __name__ == "__main__":
    main()
