"""A release gate for agent changes (Chapter 13).

Compares a candidate's evaluation results with thresholds and with the
version in production. Hard gates must pass; regressions beyond tolerance block.
"""
GATES = {   # metric: (direction, threshold, hard)
    "leakage_cases":          ("max", 0,    True),
    "policy_violations":      ("max", 0,    True),
    "claims_without_calls":   ("max", 0,    True),
    "answer_correctness":     ("min", 0.97, False),
    "tool_trajectory_match":  ("min", 0.90, False),
    "p90_latency_s":          ("max", 8.0,  False),
    "cost_per_task_usd":      ("max", 0.05, False),
}
TOLERANCE = 0.01   # allowed regression vs production on soft metrics (absolute)

def gate(candidate: dict, production: dict) -> tuple[str, list[str]]:
    reasons = []
    for metric, (direction, threshold, hard) in GATES.items():
        value = candidate.get(metric)
        if value is None:
            reasons.append(f"BLOCK {metric}: missing result")      # fail closed
            continue
        ok = value <= threshold if direction == "max" else value >= threshold
        if not ok:
            reasons.append(f"BLOCK {metric}: {value} vs threshold {threshold}")
        elif not hard and metric in production:
            worse = (value - production[metric]) if direction == "max" else (production[metric] - value)
            scale = abs(production[metric]) or 1.0
            if worse > TOLERANCE * (1 if direction == "min" else scale):
                reasons.append(f"REVIEW {metric}: regressed from {production[metric]} to {value}")
    if any(r.startswith("BLOCK") for r in reasons):
        return "no-go", reasons
    return ("review" if reasons else "go"), reasons

def _cli():
    import argparse, json
    p = argparse.ArgumentParser(description="Release gate for an agent change.")
    p.add_argument("--candidate", help="JSON file of the candidate's evaluation results")
    p.add_argument("--production", help="JSON file of production's results (optional)")
    a = p.parse_args()
    if not a.candidate:
        return False
    cand = json.load(open(a.candidate))
    prod = json.load(open(a.production)) if a.production else {}
    decision, reasons = gate(cand, prod)
    print(decision)
    for r in reasons:
        print("  " + r)
    raise SystemExit(0 if decision == "go" else 1)


if __name__ == "__main__":
    if _cli() is False:
        pass  # no arguments: run the chapter example below
    prod = {"answer_correctness": 0.975, "tool_trajectory_match": 0.93,
            "p90_latency_s": 5.1, "cost_per_task_usd": 0.021}
    new_model = {"leakage_cases": 0, "policy_violations": 0, "claims_without_calls": 0,
                 "answer_correctness": 0.981, "tool_trajectory_match": 0.91,
                 "p90_latency_s": 4.2, "cost_per_task_usd": 0.018}
    new_prompt = {**new_model, "claims_without_calls": 2}
    for name, cand in [("model upgrade", new_model), ("prompt change", new_prompt),
                       ("missing eval", {k: v for k, v in new_model.items() if k != "leakage_cases"})]:
        print(name, "->", gate(cand, prod))
