"""Weighted trade-off scores and a weight-sensitivity check (Chapter 2)."""
import numpy as np

criteria = ["quality", "cost", "speed", "reliability", "security",
            "control", "maintainability", "workload"]
weights = np.array([0.20, 0.10, 0.20, 0.10, 0.10, 0.15, 0.05, 0.10])
scores = {                      # 1 (poor) .. 5 (excellent)
    "D1 single agent":    [2, 3, 5, 2, 2, 1, 3, 5],
    "D2 rep-reviewed":    [5, 4, 2, 4, 4, 5, 4, 2],
    "D3 straight-through": [4, 4, 4, 4, 4, 4, 3, 4],
}
S = np.array(list(scores.values()), dtype=float)
names = list(scores)

base = S @ weights
for n, s in zip(names, base):
    print(f"{n:22s} {s:.2f}")

# Sensitivity: draw weight vectors near the base weights and count winners.
rng = np.random.default_rng(7)
W = rng.dirichlet(weights * 40, size=10_000)     # concentration 40 -> moderate spread
wins = np.bincount((W @ S.T).argmax(axis=1), minlength=len(names))
for n, k in zip(names, wins):
    print(f"{n:22s} wins {k / len(W):.1%} of perturbed weightings")

# Break-even: how much must one weight rise (others rescaled) before D2 beats D3?
for i, c in enumerate(criteria):
    for w_new in np.arange(weights[i], 0.95, 0.01):
        w = weights * (1 - w_new) / (1 - weights[i]); w[i] = w_new
        if (S @ w)[1] > (S @ w)[2]:
            print(f"D2 overtakes D3 if '{c}' weight rises from {weights[i]:.2f} to {w_new:.2f}")
            break
