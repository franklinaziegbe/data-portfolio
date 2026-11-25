# Data Portfolio: Franklin Aziegbe

Data analyst in Richmond, VA, working in Python and SQL. These projects focus on the part of analysis
that matters most to me: picking the right method and checking whether a conclusion actually holds up.

## Projects

| Project | What it shows | Tools |
|---|---|---|
| [Pricing test: paired vs. independent](pricing-test-analysis/) | Choosing the right statistical test, and how selecting on a bad period fakes an "effect" (regression to the mean) | Python, pandas, SciPy |
| [Customer cohort retention + PVM](cohort-retention-pvm/) | Cleaning 1M+ real transactions, cohort retention, and a price-volume-mix revenue bridge | Python, pandas, matplotlib |
| [NBA East standings predictions](nba-east-predictions/) | Pulling live data from an API, scoring ranked predictions two ways, tracking a leaderboard over a season | Python, nba_api, pandas, SciPy |

## Headline findings

- **Pricing test:** an independent t-test missed a real +2.6% lift (p = 0.89) that the paired test found clearly (p < 0.0001). In a second simulation with no real effect, picking locations for a bad summer produced a "significant" +7.4% lift, and difference-in-differences made it worse (+10.7 points). Only a baseline that wasn't used for selection came close to the truth.
- **Cohort retention + PVM:** revenue looked flat year over year (+1.7%), but units of existing products fell 16.7%, and new products covered the gap. Two cancelled orders worth £245k would have been the biggest "sales" in the data if cancellations were handled the usual way.
- **NBA predictions:** a working tracker for a friends' prediction contest, with a comparison of two scoring rules that can change who wins.

## How to run

```bash
pip install -r requirements.txt
jupyter notebook
```

Each project folder has its own README with the data source, findings, a plain-English walk-through, and setup steps.

## Contact

[LinkedIn](https://www.linkedin.com/in/franklin-aziegbe)
