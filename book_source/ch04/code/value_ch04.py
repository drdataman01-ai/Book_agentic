"""Annual value case for Alder & Finch's policy assistant (Chapter 4)."""
P = dict(
    tickets=2_600 * 12,      # policy-question tickets per year today (measured)
    deflect=0.50,            # share answered without a ticket (assumed; pilot tests)
    hr_min=11,               # HR touch minutes per ticket (measured)
    hr_cost=0.95,            # loaded HR cost per minute ($)
    redeploy=0.6,            # share of freed HR time that becomes value (assumed)
    wrong_before=0.07,       # wrong answers today (audit, measured)
    wrong_after=0.03,        # wrong answers on deflected questions (target)
    cost_wrong=120,          # rework and correction per wrong answer ($, estimated)
    questions=4_000 * 12,    # questions asked of the assistant (includes new demand)
    per_question=0.02,       # search + model per question ($, check current pricing)
    platform=18_000,         # hosting, index, monitoring per year ($)
    engineer=45_000,         # 0.3 FTE to run and improve
    curation=30_000,         # 0.2 FTE HR content owner keeping metadata right
)
BUILD = 120_000

def net_value(p):
    deflected = p["tickets"] * p["deflect"]
    labor = deflected * p["hr_min"] * p["hr_cost"] * p["redeploy"]
    errors = deflected * (p["wrong_before"] - p["wrong_after"]) * p["cost_wrong"]
    run = (p["questions"] * p["per_question"] + p["platform"]
           + p["engineer"] + p["curation"])
    return labor, errors, -run

labor, errors, run = net_value(P)
net = labor + errors + run
print(f"labor   {labor:>10,.0f}\nerrors  {errors:>10,.0f}\nrun     {run:>10,.0f}")
print(f"net     {net:>10,.0f}   payback {12 * BUILD / net:.1f} months")
for d in (0.3, 0.7):
    print(f"deflect={d:.0%}: net {sum(net_value({**P, 'deflect': d})):,.0f}")
