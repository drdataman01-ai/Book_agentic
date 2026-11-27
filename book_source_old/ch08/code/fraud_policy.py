"""Block / review / pass thresholds for card fraud under analyst capacity (Chapter 8).

One simulated day of card-not-present transactions with an anomaly score.
Costs are illustrative; replace them with your own loss and friction data.
"""
import numpy as np

rng = np.random.default_rng(8)
N = 600_000                                  # card-not-present transactions per day
fraud = rng.random(N) < 0.0012
amount = rng.lognormal(3.9, 1.0, N)
amount[fraud] = rng.lognormal(4.6, 0.9, fraud.sum())       # fraud skews larger
score = np.where(fraud, rng.beta(3.0, 2.2, N), rng.beta(1.3, 9.0, N))

LOSS_SHARE = 1.0          # issuer bears the loss on missed card-not-present fraud
CHARGEBACK_OPS = 25.0     # handling cost per missed fraud
DECLINE_FRICTION = 6.0    # cost of wrongly blocking a good customer (calls, churn)
REVIEW_MIN_COST = 0.70    # analyst cost per minute

def day_cost(t_review, t_block, review_minutes, capacity_minutes):
    block = score >= t_block
    review = (score >= t_review) & ~block
    # analysts work the review queue from the highest score down, until capacity runs out
    order = np.argsort(-score[review])
    can_review = min(review.sum(), int(capacity_minutes // review_minutes))
    idx = np.flatnonzero(review)[order][:can_review]
    reviewed = np.zeros(N, bool); reviewed[idx] = True
    caught = (block | reviewed) & fraud
    missed = fraud & ~caught
    false_blocks = block & ~fraud
    cost = (missed * (amount * LOSS_SHARE + CHARGEBACK_OPS)).sum() \
         + false_blocks.sum() * DECLINE_FRICTION \
         + can_review * review_minutes * REVIEW_MIN_COST
    return cost, can_review, caught.sum(), false_blocks.sum()

CAPACITY = 14 * 7.5 * 60            # 14 analysts on shift, 7.5 productive hours
print(f"fraud cases {fraud.sum()}, fraud value ${(amount * fraud).sum():,.0f}")
for label, minutes in [("analyst alone (6 min/alert)", 6.0),
                       ("with case summary (3.5 min/alert)", 3.5)]:
    best = min((day_cost(tr, tb, minutes, CAPACITY)[0], tr, tb)
               for tr in np.arange(0.05, 0.70, 0.025)
               for tb in np.arange(0.30, 1.00, 0.025))
    cost, rev, caught, fb = day_cost(best[1], best[2], minutes, CAPACITY)
    print(f"{label:34s} review>={best[1]:.2f} block>={best[2]:.2f}  reviewed {rev:5d}"
          f"  caught {caught}/{fraud.sum()}  false blocks {fb:4d}  cost ${cost:,.0f}/day")
print(f"{'no review: block >= 0.70':34s} cost ${day_cost(1.1, 0.70, 6.0, 0)[0]:,.0f}/day")
