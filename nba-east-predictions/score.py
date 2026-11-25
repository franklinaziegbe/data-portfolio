"""Score NBA East standings predictions against actual standings.

Scoring rule: each player picks the top 10 East teams in order. For each pick, the error is the
distance between where you ranked the team and where it actually is. Lowest total error wins.

    Pick Celtics 1st, they're actually 3rd  ->  2 points of error

Run:  python score.py
      python score.py --predictions data/predictions.csv --standings data/east_standings.csv
"""
import argparse
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"

EAST_TEAMS = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls",
    "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Miami Heat", "Milwaukee Bucks",
    "New York Knicks", "Orlando Magic", "Philadelphia 76ers", "Toronto Raptors", "Washington Wizards",
]


def _clean(name: str) -> str:
    return " ".join(str(name).split()).lower()


def load_predictions(path: Path) -> pd.DataFrame:
    """Read a wide predictions file (rank, Player 1, Player 2, ...) into long format.

    Returns columns: player, predicted_rank, team
    """
    wide = pd.read_csv(path)
    if "rank" not in wide.columns:
        raise ValueError(f"{path} needs a 'rank' column (1-10) plus one column per player.")
    long = wide.melt(id_vars="rank", var_name="player", value_name="team").dropna(subset=["team"])
    long = long.rename(columns={"rank": "predicted_rank"})
    long["predicted_rank"] = long["predicted_rank"].astype(int)
    return long[["player", "predicted_rank", "team"]]


def load_standings(path: Path) -> pd.DataFrame:
    standings = pd.read_csv(path)
    missing = {"rank", "team"} - set(standings.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {sorted(missing)}")
    return standings


def validate(predictions: pd.DataFrame, standings: pd.DataFrame) -> None:
    """Catch typos and duplicate picks before scoring."""
    known = {_clean(t) for t in standings["team"]}
    unknown = sorted({t for t in predictions["team"] if _clean(t) not in known})
    if unknown:
        raise ValueError(f"These picks don't match any team in the standings: {unknown}. "
                         f"Use full names like 'Boston Celtics'.")
    dupes = predictions.assign(key=predictions["team"].map(_clean)).duplicated(["player", "key"])
    if dupes.any():
        raise ValueError(f"Some players picked the same team twice: {predictions[dupes].to_dict('records')}")


def score_predictions(predictions: pd.DataFrame, standings: pd.DataFrame, top_n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Score each player's top-N picks.

    Returns
    -------
    detail : one row per pick with predicted_rank, actual_rank and error
    leaderboard : one row per player with total_error, exact_hits and place
    """
    validate(predictions, standings)
    picks = predictions[predictions["predicted_rank"] <= top_n].copy()
    picks["key"] = picks["team"].map(_clean)
    actual = standings.assign(key=standings["team"].map(_clean))[["key", "rank"]].rename(columns={"rank": "actual_rank"})

    detail = picks.merge(actual, on="key", how="left").drop(columns="key")
    detail["error"] = (detail["predicted_rank"] - detail["actual_rank"]).abs()

    leaderboard = (
        detail.groupby("player")
        .agg(total_error=("error", "sum"),
             exact_hits=("error", lambda e: int((e == 0).sum())),
             picks=("error", "size"))
        .sort_values(["total_error", "exact_hits"], ascending=[True, False])
        .reset_index()
    )
    leaderboard.insert(0, "place", leaderboard["total_error"].rank(method="min").astype(int))
    return detail, leaderboard


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--predictions", type=Path, default=DATA_DIR / "sample_predictions.csv")
    parser.add_argument("--standings", type=Path, default=DATA_DIR / "sample_standings.csv")
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()

    predictions = load_predictions(args.predictions)
    standings = load_standings(args.standings)
    _, leaderboard = score_predictions(predictions, standings, args.top_n)
    print(leaderboard.to_string(index=False))


if __name__ == "__main__":
    main()
