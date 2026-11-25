"""Generate the simulated data for the pricing test project.

All data here is simulated, so the true effect of the price increase is known.
That lets you check which analysis methods get close to the truth.

Outputs
-------
data/locations_before_after.csv
    Part A: 12 locations, average weekly revenue 8 weeks before and after a 3% price increase.
data/location_periods.csv
    Part B: 60 locations with a 2-year trailing average, a summer and a fall period. The 12
    locations whose summer was weakest compared with their own trailing average get the price
    increase in the fall.

Run:  python generate_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
DATA_DIR = Path(__file__).parent / "data"

# Part A settings
N_LOCATIONS_A = 12
TRUE_LIFT_A = 0.025        # average revenue lift from the price increase (2.5%)
LIFT_NOISE_A = 0.012       # location-to-location variation in that lift

# Part B settings
N_LOCATIONS_B = 60
N_TREATED_B = 12
PERIOD_NOISE_B = 0.06      # random period-to-period swing in revenue (6%)
TRUE_PRICE_EFFECT_B = 0.0  # the price increase does NOTHING in Part B. Try changing this.


def make_part_a(rng: np.random.Generator) -> pd.DataFrame:
    before = rng.uniform(20_000, 200_000, N_LOCATIONS_A)
    lift = rng.normal(TRUE_LIFT_A, LIFT_NOISE_A, N_LOCATIONS_A)
    after = before * (1 + lift)
    return pd.DataFrame({
        "location_id": [f"L{i:02d}" for i in range(1, N_LOCATIONS_A + 1)],
        "revenue_before": before.round(-1),
        "revenue_after": after.round(-1),
    })


def make_part_b(rng: np.random.Generator) -> pd.DataFrame:
    true_level = rng.uniform(30_000, 180_000, N_LOCATIONS_B)
    # A 2-year average smooths out most of the noise, so it sits close to each location's true level.
    trailing_avg = true_level * (1 + rng.normal(0, PERIOD_NOISE_B / 4, N_LOCATIONS_B))
    summer = true_level * (1 + rng.normal(0, PERIOD_NOISE_B, N_LOCATIONS_B))

    # The client picks the locations whose summer was weakest compared with their own trailing average.
    summer_vs_normal = summer / trailing_avg
    treated_idx = np.argsort(summer_vs_normal)[:N_TREATED_B]
    treated = np.zeros(N_LOCATIONS_B, dtype=bool)
    treated[treated_idx] = True

    fall = true_level * (1 + rng.normal(0, PERIOD_NOISE_B, N_LOCATIONS_B))
    fall = np.where(treated, fall * (1 + TRUE_PRICE_EFFECT_B), fall)

    return pd.DataFrame({
        "location_id": [f"S{i:02d}" for i in range(1, N_LOCATIONS_B + 1)],
        "price_increase": treated,
        "revenue_trailing_2yr_avg": trailing_avg.round(-1),
        "revenue_summer": summer.round(-1),
        "revenue_fall": fall.round(-1),
    })


def main() -> None:
    rng = np.random.default_rng(SEED)
    DATA_DIR.mkdir(exist_ok=True)
    part_a = make_part_a(rng)
    part_b = make_part_b(rng)
    part_a.to_csv(DATA_DIR / "locations_before_after.csv", index=False)
    part_b.to_csv(DATA_DIR / "location_periods.csv", index=False)
    print(f"Wrote {len(part_a)} rows to data/locations_before_after.csv")
    print(f"Wrote {len(part_b)} rows to data/location_periods.csv "
          f"({part_b['price_increase'].sum()} with the price increase)")


if __name__ == "__main__":
    main()
