"""Three-year total cost of ownership: build on three targets, or buy (Chapter 12).

Every input is an illustrative planning figure; replace with quotes and measurements.
"""
YEARS = 3
MEMOS_PER_YEAR = 4_400            # new credit memos plus annual reviews
ENGINEER = 210_000                # loaded cost of one engineer-year ($)

OPTIONS = {
    #                      build    platform/yr  ops FTE  per memo  integration  exit
    "Build: Agent Runtime": (650_000,  60_000,     0.6,    3.20,     0,          40_000),
    "Build: Cloud Run":     (700_000,  35_000,     0.9,    3.20,     0,          30_000),
    "Build: GKE":           (780_000,  90_000,     1.5,    3.00,     0,          30_000),
    "Buy: vendor platform": (0,       300_000,     0.3,   18.00,   250_000,     150_000),
}

def tco(build, platform, ops_fte, per_memo, integration, exit_cost, memos=MEMOS_PER_YEAR):
    yearly = platform + ops_fte * ENGINEER + per_memo * memos
    return build + integration + YEARS * yearly + exit_cost

for name, args in OPTIONS.items():
    print(f"{name:22s} 3-year TCO ${tco(*args):>11,.0f}")

print("\nTCO by annual volume (memos):")
print("volume  " + "  ".join(f"{n:>13s}" for n in ("Agent Runtime", "Cloud Run", "GKE", "Vendor")))
for v in (1_000, 4_400, 15_000):
    print(f"{v:6,d}  " + "  ".join(f"${tco(*a, memos=v):>12,.0f}" for a in OPTIONS.values()))
