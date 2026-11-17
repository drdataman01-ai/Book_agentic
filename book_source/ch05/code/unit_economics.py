"""Cost per contact by design and by intent for Cymbal's support (Chapter 5).

All prices are illustrative planning figures; replace them with your own
contract rates and current model pricing before using the results.
"""
MONTHLY_CONTACTS = 52_000
HUMAN_PER_MIN = 0.62            # blended loaded cost of in-house and outsourced agents
SEAT_PER_HUMAN_CONTACT = 0.45   # contact-centre software per human-handled contact

#            share  human min  D1 auto  D2 auto  D3 time cut
INTENTS = {
    "order status":  (0.34, 4.5, 0.70, 0.88, 0.35),
    "delivery issue":(0.14, 9.0, 0.30, 0.40, 0.30),
    "return/refund": (0.18, 8.0, 0.45, 0.55, 0.30),
    "product q":     (0.12, 7.0, 0.60, 0.65, 0.30),
    "scheduling":    (0.08, 6.0, 0.55, 0.60, 0.25),
    "complaint":     (0.06, 14.0, 0.10, 0.00, 0.25),
    "other":         (0.08, 9.0, 0.20, 0.15, 0.20),
}
DESIGNS = {  # model $/AI contact, error rate on AI-resolved, $ per error, fixed $/month
    "Baseline": dict(model=0.000, err=0.000, err_cost=0, fixed=0),
    "D1 single agent": dict(model=0.024, err=0.060, err_cost=22, fixed=16_000),
    "D2 triage + tools": dict(model=0.011, err=0.015, err_cost=22, fixed=38_000),
    "D3 agent assist": dict(model=0.006, err=0.000, err_cost=22, fixed=17_000),
    "D4 hybrid by intent": dict(model=0.009, err=0.015, err_cost=22, fixed=36_000),
}
# D4 automates the low-risk intents as D2 does and gives people D3's assist on the rest
D4_ASSIST = {"return/refund", "complaint", "other"}
ESCALATION_OVERHEAD_MIN = 1.5    # extra human minutes when a bot hands a case over
D2_SUMMARY_SAVES_MIN = 3.0       # D2 hands complaints over with a summary

def per_intent(design, share, minutes, auto1, auto2, cut3, name="", params=None):
    """Cost of one contact of this intent under this design, and its automation rate."""
    d = params or DESIGNS[design]
    if design == "D4 hybrid by intent":     # route by intent, keep D4's own prices
        mode = "D3 agent assist" if name in D4_ASSIST else "D2 triage + tools"
        return per_intent(mode, share, minutes, auto1, auto2, cut3, name, params=d)
    if design == "Baseline":
        auto, human_min = 0.0, minutes
    elif design == "D1 single agent":
        auto, human_min = auto1, minutes + ESCALATION_OVERHEAD_MIN
    elif design == "D2 triage + tools":
        auto = auto2
        human_min = minutes + ESCALATION_OVERHEAD_MIN
        if auto2 == 0.0:   # complaints: routed straight to a person with a summary
            human_min = minutes - D2_SUMMARY_SAVES_MIN
    else:  # D3: every contact handled by a person, with drafts and pre-fetched data
        auto, human_min = 0.0, minutes * (1 - cut3)
    human = (1 - auto) * (human_min * HUMAN_PER_MIN + SEAT_PER_HUMAN_CONTACT)
    model = d["model"] if design == "D3 agent assist" else auto * d["model"]
    errors = auto * d["err"] * d["err_cost"]
    return human + model + errors, auto


def summary(design):
    var = contain = 0.0
    for name, (share, minutes, a1, a2, cut) in INTENTS.items():
        cost, auto = per_intent(design, share, minutes, a1, a2, cut, name)
        var += share * cost
        contain += share * auto
    fixed = DESIGNS[design]["fixed"] / MONTHLY_CONTACTS
    return var, fixed, contain

for design in DESIGNS:
    var, fixed, contain = summary(design)
    total = var + fixed
    print(f"{design:20s} ${total:4.2f}/contact  (variable {var:4.2f}, fixed {fixed:4.2f})"
          f"  contained {contain:3.0%}  monthly ${total * MONTHLY_CONTACTS:>9,.0f}")

print("\nD2 cost per contact by intent (variable part):")
for name, (share, minutes, a1, a2, cut) in INTENTS.items():
    cost, auto = per_intent("D2 triage + tools", share, minutes, a1, a2, cut)
    print(f"  {name:15s} automated {auto:4.0%}   ${cost:4.2f}")
