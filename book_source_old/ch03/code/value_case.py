"""Annual value case and one-at-a-time sensitivity for Harbor's quote design (Chapter 3)."""

BASE = dict(
    quotes=20_000,          # quotes per year
    order_value=48_000,     # average quoted order ($)
    win_rate_lift=0.01,     # +1 percentage point win rate from faster quotes
    gross_margin=0.24,      # gross margin on won orders
    minutes_saved=27,       # analyst minutes saved per quote (35 -> 8)
    redeploy_share=0.5,     # share of freed analyst time that turns into value
    cost_per_min=1.10,      # loaded analyst cost per minute ($)
    err_before=0.024,       # share of quotes issued below margin floor today
    err_after=0.002,        # ... with the floor enforced in code
    win_rate=0.31,          # share of quotes that become orders
    loss_per_err=1_150,     # margin shortfall per below-floor order ($)
    review_share=0.18,      # share of quotes routed to a manager
    review_min=6,           # manager minutes per review
    mgr_cost_per_min=1.60,  # loaded manager cost per minute ($)
    model_cost=0.03,        # model + tool calls per quote ($)
    platform_cost=24_000,   # hosting, search, monitoring per year ($)
    support_cost=60_000,    # 0.4 FTE engineer to run and improve it ($/yr)
)
BUILD_COST = 180_000        # one-time: build, integration, change management ($)

def annual(p):
    growth = p["quotes"] * p["win_rate_lift"] * p["order_value"] * p["gross_margin"]
    labor = p["quotes"] * p["minutes_saved"] * p["cost_per_min"] * p["redeploy_share"]
    errors = p["quotes"] * p["win_rate"] * (p["err_before"] - p["err_after"]) * p["loss_per_err"]
    review = p["quotes"] * p["review_share"] * p["review_min"] * p["mgr_cost_per_min"]
    run = p["quotes"] * p["model_cost"] + p["platform_cost"] + p["support_cost"]
    return dict(growth=growth, labor=labor, errors=errors,
                review=-review, run=-run)

parts = annual(BASE)
net = sum(parts.values())
for k, v in parts.items():
    print(f"{k:8s} {v:>12,.0f}")
print(f"{'net':8s} {net:>12,.0f}   payback {12 * BUILD_COST / net:.1f} months")

# One-at-a-time sensitivity: low and high value for the riskiest inputs
RANGES = dict(win_rate_lift=(0.0, 0.02), redeploy_share=(0.0, 1.0),
              model_cost=(0.01, 0.30), review_share=(0.10, 0.40),
              err_after=(0.0, 0.01), loss_per_err=(600, 2_000))
def net(p):
    return sum(annual(p).values())

swing = {k: (net({**BASE, k: lo}), net({**BASE, k: hi}))
         for k, (lo, hi) in RANGES.items()}
print("\ninput            net@low     net@high")
by_width = sorted(swing.items(), key=lambda kv: -abs(kv[1][1] - kv[1][0]))
for k, (n_lo, n_hi) in by_width:
    print(f"{k:15s} {n_lo:>10,.0f} {n_hi:>11,.0f}")
