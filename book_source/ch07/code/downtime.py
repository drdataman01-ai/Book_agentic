"""Value of faster incident response at Parcelpoint (Chapter 7).

MTTR is split into phases; each design changes some phases. Automated
actions can also go wrong, which adds outage time with some probability.
"""
PHASES = ["detect", "acknowledge", "diagnose", "mitigate", "verify"]
BASE = {"P1": dict(per_month=3, cost_per_min=1_200, minutes=[6, 9, 38, 15, 6]),
        "P2": dict(per_month=14, cost_per_min=150, minutes=[10, 18, 70, 40, 22])}

DESIGNS = {
    # multipliers per phase, p(wrong automated action), minutes added if wrong
    "D1 chat assistant":   dict(mult=[1.0, 1.0, 0.85, 1.0, 1.0], p_wrong=0.00, wrong_min=0),
    "D2 triage + safe actions": dict(mult=[1.0, 0.35, 0.55, 0.70, 1.0], p_wrong=0.02, wrong_min=20),
    "D3 auto-remediate":   dict(mult=[1.0, 0.20, 0.50, 0.40, 1.0], p_wrong=0.08, wrong_min=35),
}

def monthly_cost(mult=None, p_wrong=0.0, wrong_min=0):
    total = 0.0
    for b in BASE.values():
        mins = sum(m * (mult[i] if mult else 1) for i, m in enumerate(b["minutes"]))
        mins += p_wrong * wrong_min
        total += b["per_month"] * mins * b["cost_per_min"]
    return total

base = monthly_cost()
print(f"baseline outage cost ${base:,.0f}/month "
      f"(P1 MTTR {sum(BASE['P1']['minutes'])} min)")
for name, d in DESIGNS.items():
    c = monthly_cost(**d)
    p1 = sum(m * d["mult"][i] for i, m in enumerate(BASE["P1"]["minutes"])) + d["p_wrong"] * d["wrong_min"]
    print(f"{name:26s} P1 MTTR {p1:5.1f} min  saving ${base - c:>9,.0f}/month")

print("\nD3 saving if a wrong action is more likely or more harmful:")
for p, w in [(0.08, 35), (0.15, 60), (0.25, 90)]:
    d = {**DESIGNS["D3 auto-remediate"], "p_wrong": p, "wrong_min": w}
    print(f"  p_wrong={p:.2f}, +{w} min  saving ${base - monthly_cost(**d):>9,.0f}/month")
