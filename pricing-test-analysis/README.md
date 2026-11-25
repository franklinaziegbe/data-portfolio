# Pricing Test: Paired vs. Independent, and the Regression-to-the-Mean Trap

## The problem

A business raised prices 3% at a set of locations and wants to know if revenue went up.
This looks like a simple before/after question, but two common mistakes can flip the answer:

1. **Using the wrong test.** The same locations are measured twice, so the data is paired.
   An independent two-sample t-test ignores that and can miss a real effect.
2. **Selection on a bad period.** If the client picked the locations *because* they had a weak
   stretch, those locations would bounce back on their own. A before/after comparison
   (and even a comparison against other locations) can show a "lift" that the price increase didn't cause.

## Data

All data is **simulated** with [`generate_data.py`](generate_data.py), so the true effect is known
and each method can be checked against it.

| File | What's in it |
|---|---|
| `data/locations_before_after.csv` | Part A: 12 locations, average weekly revenue 8 weeks before and after the change |
| `data/location_periods.csv` | Part B: 60 locations, a 2-year trailing average, summer, and fall revenue. The 12 with the weakest summer got the price increase. |

## Approach

- **Part A:** independent t-test vs. paired t-test vs. Wilcoxon signed-rank, plus a 95% confidence interval for the average change
- **Part B:** naive before/after vs. difference-in-differences vs. comparing against each location's own long-run baseline

## Findings

<!-- TODO (Frank): Fill this in after finishing the notebook. 3–5 bullets, in your own words.
     Include the actual numbers (p-values, % changes) and which method got closest to the true effect. -->

## How to run

```bash
python generate_data.py      # re-creates the CSVs
jupyter notebook analysis.ipynb
```
