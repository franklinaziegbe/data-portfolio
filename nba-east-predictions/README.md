# NBA East Standings Predictions Tracker

## The problem

Before the 2026–27 season, a group of friends each ranked the top 10 teams in the Eastern Conference.
This project pulls the live standings from the NBA's stats API, scores every prediction, and tracks
the leaderboard as the season goes on.

## Scoring

Each pick's error is the distance between where you ranked a team and where it actually stands.
Lowest total error across your 10 picks wins.

> Pick the Celtics 1st, they're actually 3rd → 2 points of error.

## Data

| File | What's in it |
|---|---|
| `data/east_standings.csv` | Latest real standings, created by `fetch_standings.py` |
| `data/snapshots/` | A dated copy every time you fetch, for tracking over the season |
| `data/predictions.csv` | Your group's real picks (copy `predictions_template.csv` and fill it in) |
| `data/sample_standings.csv`, `data/sample_predictions.csv` | **Made-up** examples so the code runs before you add real data |

Standings come from stats.nba.com through the [`nba_api`](https://github.com/swar/nba_api) package.

<!-- TODO (Frank): Ask your friends before putting their real names in a public repo.
     Initials or nicknames work fine. -->

## Approach

<!-- TODO (Frank): 2–3 sentences on how you scored it and what you added (Spearman correlation,
     most-mispredicted teams, leaderboard over time, a different scoring rule). -->

## Findings

<!-- TODO (Frank): Who's winning, which teams everyone got wrong, and anything surprising. -->

## How to run

```bash
python fetch_standings.py                                   # pull the latest standings
cp data/predictions_template.csv data/predictions.csv       # then fill in your group's picks
python score.py --predictions data/predictions.csv --standings data/east_standings.csv
jupyter notebook analysis.ipynb
```
