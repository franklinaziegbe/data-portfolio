# Pricing Test: Paired vs. Independent, and the Regression-to-the-Mean Trap

## The problem

A business raised prices 3% at a set of locations and wants to know if revenue went up.
This looks like a simple before/after question, but two common mistakes can flip the answer:

1. **Using the wrong test.** The same locations are measured twice, so the data is paired.
   An independent two-sample t-test ignores that and can miss a real effect.
2. **Selection on a bad period.** If the client picked the locations *because* they had a weak
   stretch, those locations would bounce back on their own. A before/after comparison
   (and even a comparison against other locations) can show a "lift" the price increase didn't cause.

## Data

All data is **simulated** with [`generate_data.py`](generate_data.py), so the true effect is known
and each method can be checked against it.

| File | What's in it |
|---|---|
| `data/locations_before_after.csv` | Part A: 12 locations, average weekly revenue 8 weeks before and after the change. True effect: about +2.5%. |
| `data/location_periods.csv` | Part B: 60 locations with a 2-year trailing average, summer, and fall revenue. The 12 with the weakest summer got the price increase. True effect: 0. |

## Findings

**Part A: the right test finds a real effect the wrong test misses.**
- Independent t-test: p = 0.89 ("no effect").
- Paired t-test: p < 0.0001. Wilcoxon signed-rank: p = 0.0005. All 12 locations went up.
- Estimated lift: **+2.6% per location (95% CI 2.1% to 3.2%)**, or about $3,260 per location per week. The true simulated effect is 2.5%.

**Part B: picking locations for a bad summer creates a fake "effect."** The true effect is 0.

| Method | Estimated effect |
|---|---|
| Naive before/after (summer → fall) | **+7.4%** (p = 0.015, looks "significant") |
| Difference-in-differences vs. the other 48 locations | **+10.7 points** (worse) |
| Fall vs. each location's own 2-year average, compared across groups | **+1.2 points** (p = 0.59, close to the truth) |

When I rebuilt Part B with a real +3% effect, the baseline method estimated about +4 points, while the other two overshot by 7 to 11 points.

## Walk-through (how to explain it)

**Part A.** Locations range from about $37k to $196k a week, so the "before" and "after" groups each have a huge spread (SD about $54k). The independent test compares the two group averages, and a $3k shift is invisible inside that spread. The paired test looks at each location's own change instead. Those changes are small but very consistent (SD about $1.5k, all positive), so the effect is obvious. The rule: if the same units are measured twice, use a paired test.

**Part B.** The 12 locations were picked because their summer was about 7% below their normal level. Part of any bad stretch is random, so it tends to reverse. That's regression to the mean. The fall "lift" is just those locations returning to normal.

Difference-in-differences doesn't fix it. The other 48 locations were *left out* because their summers weren't bad (about 2% above normal on average), so they drifted down in the fall (−3.3%). Subtracting that drift from the rebound makes the fake effect bigger. Difference-in-differences assumes both groups would have moved the same way without the change, and selecting on the outcome breaks that.

What works is a baseline that wasn't used to pick the locations: each location's 2-year average. Against that, the price-increase locations ended the fall right at normal (+0.0%), about the same as everyone else.

**The business takeaway:** before trusting a before/after number, ask how the units were chosen. If they were chosen *because* of the "before" period, the comparison is biased.

## How to run

```bash
python generate_data.py      # re-creates the CSVs (fixed seed, same numbers every time)
jupyter notebook analysis.ipynb
```

Change `TRUE_PRICE_EFFECT_B` in `generate_data.py` to test the methods against a different true effect.
