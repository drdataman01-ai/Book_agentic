"""Trade-off scores and weight sensitivity for the policy assistant (Chapter 4)."""
import numpy as np

criteria = ["quality", "cost", "speed", "reliability", "security",
            "control", "maintainability", "workload"]
weights = np.array([0.25, 0.05, 0.05, 0.10, 0.20, 0.10, 0.10, 0.15])
scores = {
    "D1 sample as is":       [2, 5, 5, 3, 1, 1, 4, 3],   # fails constraint R2
    "D2 grounded, filtered": [4, 4, 4, 4, 5, 4, 4, 4],
    "D3 curated first":      [5, 4, 5, 4, 5, 5, 2, 3],
}
S = np.array(list(scores.values()), dtype=float)
names = list(scores)
for n, s in zip(names, S @ weights):
    print(f"{n:24s} {s:.2f}")

viable = S[1:]                                  # D1 removed by the constraint
rng = np.random.default_rng(7)
W = rng.dirichlet(weights * 40, size=10_000)
wins = np.bincount((W @ viable.T).argmax(axis=1), minlength=2)
for n, k in zip(names[1:], wins):
    print(f"{n:24s} wins {k / len(W):.1%} of perturbed weightings")
