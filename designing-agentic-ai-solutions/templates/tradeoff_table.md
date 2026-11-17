# Trade-off table

**Constraints checked first:** <!-- any design that fails a constraint is out, whatever its score -->

| Criterion | Weight | D1 | D2 | D3 |
|---|---|---|---|---|
| *Money rows (per unit): run cost, human time, expected error cost* | — | | | |
| Quality | | | | |
| Speed | | | | |
| Reliability | | | | |
| Security and privacy | | | | |
| Control and auditability | | | | |
| Maintainability | | | | |
| Human workload (if not in money rows) | | | | |
| **Weighted score** | 1.00 | | | |

Mark each score **M** (measured) or **E** (estimated).

**Sensitivity:** share of perturbed weightings each design wins (run `tradeoff.py`); what would flip the decision.
