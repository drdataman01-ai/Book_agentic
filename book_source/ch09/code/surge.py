"""Contact-centre waiting during a disruption, with and without self-service (Chapter 9).

Erlang C gives the steady-state probability of waiting and the mean wait for
c agents, arrival rate lam (per minute) and mean handling time aht (minutes).
"""
from math import exp, lgamma, log

def erlang_c(c: int, lam: float, aht: float) -> tuple[float, float]:
    a = lam * aht                         # offered load in Erlangs
    if a >= c:
        return 1.0, float("inf")          # queue grows without bound
    # log-space sums for numerical stability
    log_terms = [k * log(a) - lgamma(k + 1) for k in range(c)]
    m = max(log_terms)
    s = sum(exp(t - m) for t in log_terms)
    top = exp(c * log(a) - lgamma(c + 1) - m) * c / (c - a)
    p_wait = top / (s + top)
    return p_wait, p_wait * aht / (c - a)  # mean wait in minutes

PASSENGERS = 9_600        # passengers on cancelled flights
CONTACT_SHARE = 0.60      # share who contact the airline
FIRST_WAVE = 0.65         # share of those contacts in the first two hours
HOURS = 2
AGENTS = 120              # agents available at short notice
AHT = 11.0                # minutes per rebooking call today

for selfserve in (0.0, 0.40, 0.55, 0.70):
    calls = PASSENGERS * CONTACT_SHARE * FIRST_WAVE * (1 - selfserve)
    lam = calls / (HOURS * 60)
    p, w = erlang_c(AGENTS, lam, AHT)
    wait = "unbounded" if w == float("inf") else f"{w:5.1f} min"
    print(f"self-service {selfserve:4.0%}: {calls:5.0f} calls, load {lam * AHT:5.1f} Erlangs,"
          f" P(wait) {p:4.2f}, mean wait {wait}")

# When load exceeds capacity, steady-state formulas break down. A fluid
# approximation: the backlog grows at (arrivals - service) per minute during
# the wave, then drains after it at the service rate minus later arrivals.
service = AGENTS / AHT                                   # calls finished per minute
later = PASSENGERS * CONTACT_SHARE * (1 - FIRST_WAVE) / (4 * 60)   # next four hours
print(f"\nbreak-even self-service share: {1 - service * HOURS * 60 / (PASSENGERS * CONTACT_SHARE * FIRST_WAVE):.0%}")
for selfserve in (0.0, 0.40, 0.55):
    lam = PASSENGERS * CONTACT_SHARE * FIRST_WAVE * (1 - selfserve) / (HOURS * 60)
    backlog = max(0.0, (lam - service) * HOURS * 60)
    drain = service - later * (1 - selfserve)
    clear_h = backlog / drain / 60
    print(f"self-service {selfserve:4.0%}: backlog after wave {backlog:5.0f} calls,"
          f" last caller waits about {HOURS + clear_h:4.1f} h from the start")
