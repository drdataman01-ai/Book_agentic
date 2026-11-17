"""Reviewer cost vs. error cost for supplier invoices (Chapter 6).

Synthetic month of invoices with three kinds of problem. A review policy
chooses which invoices a person checks; the cost of a policy is the review
labor plus the losses from problems that are paid without review.
"""
import numpy as np

rng = np.random.default_rng(42)
N = 9_500                                   # invoices per month
amount = np.round(rng.lognormal(mean=7.2, sigma=1.1, size=N), 2)

# Problems and the loss if paid unnoticed (illustrative, from Meridian's audit)
dup = rng.random(N) < 0.004                 # duplicate of an earlier invoice
over = rng.random(N) < 0.030                # price or quantity above PO/receipt
fraud = rng.random(N) < 0.0006              # changed bank details, fake supplier
loss = np.where(dup, amount, 0.0)
loss += np.where(over, amount * rng.uniform(0.03, 0.15, N), 0.0)
loss += np.where(fraud, amount * 3.0, 0.0)  # fraud tends to repeat until caught
bad = loss > 0

# A risk score from deterministic checks and a light model: higher for problems
score = rng.beta(1.2, 9, N)
score[dup] = rng.beta(8, 2, dup.sum())       # duplicate check is strong
score[over] = np.maximum(score[over], rng.beta(5, 3, over.sum()))
score[fraud] = rng.beta(6, 2, fraud.sum())

REVIEW_COST = 6.00      # 8 minutes of a clerk at $0.75/min, plus tooling
CATCH = 0.95            # reviewers catch 95% of problems they look at

def policy_cost(review_mask):
    reviewed = review_mask.sum()
    missed = loss * np.where(review_mask, 1 - CATCH, 1.0)
    return reviewed * REVIEW_COST + missed.sum(), reviewed

print(f"invoices {N:,}; with a problem {bad.sum()} ({bad.mean():.1%}); "
      f"exposure ${loss.sum():,.0f}/month")
for label, mask in [("review none", np.zeros(N, bool)),
                    ("review all", np.ones(N, bool)),
                    ("amount >= $5,000", amount >= 5_000),
                    ("amount >= $1,000", amount >= 1_000)]:
    c, r = policy_cost(mask)
    print(f"{label:22s} reviewed {r:5d}  cost ${c:>9,.0f}")

best = min(((policy_cost(score >= t)[0], t) for t in np.linspace(0, 1, 201)))
c, r = policy_cost(score >= best[1])
print(f"{'risk score >= %.3f' % best[1]:22s} reviewed {r:5d}  cost ${c:>9,.0f}  (best threshold)")
