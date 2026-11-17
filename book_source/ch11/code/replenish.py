"""Ordering perishables from a probabilistic forecast, and where compute goes (Chapter 11)."""
import numpy as np

rng = np.random.default_rng(11)

# --- 1. Newsvendor: order a quantile, not the mean -----------------------
PRICE, COST, SALVAGE = 4.00, 2.60, 0.20      # per unit of a fresh item
under = PRICE - COST                          # margin lost per unit short
over = COST - SALVAGE                         # loss per unit wasted
critical = under / (under + over)             # optimal service level
days = 20_000
mean = rng.gamma(9.0, 4.0, days)              # true expected demand varies by day
demand = rng.negative_binomial(n=6, p=6 / (6 + mean))   # overdispersed sales

def profit(order):
    sold = np.minimum(order, demand)
    return (PRICE * sold - COST * order + SALVAGE * (order - sold)).mean()

# A probabilistic forecast gives quantiles; here, the true predictive distribution
samples = rng.negative_binomial(n=6, p=(6 / (6 + mean))[:, None], size=(days, 400))
q_order = np.quantile(samples, critical, axis=1)
print(f"critical ratio {critical:.2f}  (order the {critical:.0%} quantile)")
print(f"order = forecast mean      profit/day ${profit(np.round(mean)):6.2f}")
print(f"order = {critical:.0%} quantile      profit/day ${profit(np.round(q_order)):6.2f}")
print(f"order = 90% quantile       profit/day ${profit(np.round(np.quantile(samples, 0.9, axis=1))):6.2f}")

# --- 2. Where the compute goes -------------------------------------------
SERIES = 80 * 6_000                          # store-SKU series forecast nightly
TSFM_SERIES_PER_GPU_SEC = 250                # batched inference throughput (assumed)
GPU_HOUR = 2.50                              # $ per accelerator hour (assumed)
gpu_hours = SERIES / TSFM_SERIES_PER_GPU_SEC / 3600
print(f"\nnightly batch: {SERIES:,} series, {gpu_hours:.2f} GPU-hours, ${gpu_hours * GPU_HOUR:.2f}/night")
AGENT_PER_SERIES = 0.012                     # $ per agent review of one series (assumed)
for share in (1.00, 0.02):
    nightly = SERIES * share * AGENT_PER_SERIES
    print(f"agent reviews {share:4.0%} of series: ${nightly:>9,.0f}/night, ${nightly * 365:>12,.0f}/year")
