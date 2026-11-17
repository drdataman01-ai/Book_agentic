"""One-at-a-time sensitivity of D4's monthly savings (Chapter 5)."""
import copy
import unit_economics as ue

def d4_monthly_saving():
    base = sum(s * ue.per_intent("Baseline", s, m, a1, a2, c, n)[0]
               for n, (s, m, a1, a2, c) in ue.INTENTS.items())
    var, fixed, _ = ue.summary("D4 hybrid by intent")
    return (base - var - fixed) * ue.MONTHLY_CONTACTS

ORIG = copy.deepcopy(ue.INTENTS), ue.HUMAN_PER_MIN, copy.deepcopy(ue.DESIGNS)
def reset():
    ue.INTENTS, ue.HUMAN_PER_MIN, ue.DESIGNS = copy.deepcopy(ORIG[0]), ORIG[1], copy.deepcopy(ORIG[2])

def set_intent(name, idx, value):
    t = list(ue.INTENTS[name]); t[idx] = value; ue.INTENTS[name] = tuple(t)

print(f"base saving per month: ${d4_monthly_saving():,.0f}")
cases = {
    "order-status automation 0.70 / 0.95": [lambda: set_intent("order status", 3, 0.70),
                                            lambda: set_intent("order status", 3, 0.95)],
    "assist time cut -10 pts / +10 pts": [lambda: [set_intent(n, 4, ue.INTENTS[n][4] - 0.10) for n in ue.D4_ASSIST],
                                          lambda: [set_intent(n, 4, ue.INTENTS[n][4] + 0.10) for n in ue.D4_ASSIST]],
    "human cost $0.45 / $0.75 per min": [lambda: setattr(ue, "HUMAN_PER_MIN", 0.45),
                                         lambda: setattr(ue, "HUMAN_PER_MIN", 0.75)],
    "error cost $22 -> $66 / $11": [lambda: ue.DESIGNS["D4 hybrid by intent"].update(err_cost=66),
                                    lambda: ue.DESIGNS["D4 hybrid by intent"].update(err_cost=11)],
    "model cost x10 / x0.5": [lambda: ue.DESIGNS["D4 hybrid by intent"].update(model=0.09),
                              lambda: ue.DESIGNS["D4 hybrid by intent"].update(model=0.0045)],
}
for label, (lo, hi) in cases.items():
    reset(); lo(); a = d4_monthly_saving()
    reset(); hi(); b = d4_monthly_saving()
    print(f"{label:38s} ${a:>8,.0f}  ${b:>8,.0f}")
reset()
