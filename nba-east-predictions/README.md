# NBA East Standings Predictions Tracker

## The problem

Before the 2026–27 season, a group of friends each ranked the top 10 teams in the Eastern Conference.
This project pulls the live standings from the NBA's stats API, scores every prediction, compares two
scoring rules, and tracks the leaderboard as the season goes on.

## What it does

| Piece | File |
|---|---|
| Pull live East standings (and save a dated snapshot) | `fetch_standings.py` |
| Score picks: total error, exact hits, alternative full-table rule | `score.py` |
| Analysis: leaderboard, rank correlation, most-mispredicted teams, scoring-rule comparison, leaderboard over time | `analysis.ipynb` |

Standings come from stats.nba.com through the [`nba_api`](https://github.com/swar/nba_api) package.

## Scoring

**Official rule:** each pick's error is the distance between where you ranked a team and where it actually stands. Lowest total across your 10 picks wins.

> Pick the Celtics 1st, they're actually 3rd → 2 points of error.

**Alternative rule (full table):** every team counts. Teams you didn't pick count as if you ranked them 11th, and teams actually outside the top 10 count as 11th. This punishes leaving out a team that's really good, which the official rule never does directly. The trade-off is that a badly wrong pick (10th predicted, 15th actual) costs only 1 point.

## Walk-through (how to explain it)

- **Data pipeline:** `fetch_standings.py` calls the NBA stats API, keeps the 15 East teams, builds full team names, and saves both the latest table and a dated snapshot. If the API is slow or blocks the request, it fails with a clear message and a manual fallback.
- **Validation before scoring:** `score.py` checks every pick against the real team names and flags typos or duplicate picks, so a misspelled team can't silently score zero.
- **Two measures of "close":** total error (how many spots off) and Spearman rank correlation (was the *order* right). On the sample data they disagree for 2nd place, which is exactly why it's worth showing both.
- **Most-mispredicted teams:** the average of *predicted minus actual* rank shows which teams the group overrated or underrated, not just which ones they missed.
- **Over time:** scoring every saved snapshot turns a one-off check into a season-long leaderboard chart.

## Data

| File | What's in it |
|---|---|
| `data/east_standings.csv` | Latest real standings (created by `fetch_standings.py`) |
| `data/snapshots/` | A dated copy from every fetch |
| `data/predictions.csv` | The group's real picks (copy `predictions_template.csv` and fill it in) |
| `data/sample_*.csv`, `data/sample_snapshots/` | **Made-up** data from `make_sample_data.py`, used only until real data exists |

Real names stay out of this public repo unless everyone's OK with it; initials or nicknames work fine.

## Results

The committed notebook shows the **sample** data. With the group's real picks and live standings, rerunning the notebook updates every table and chart.

## How to run

```bash
python fetch_standings.py                                   # pull the latest standings
cp data/predictions_template.csv data/predictions.csv       # fill in the group's picks
python score.py --predictions data/predictions.csv --standings data/east_standings.csv
jupyter notebook analysis.ipynb
```

Run `fetch_standings.py` once a week to build up the season history.
