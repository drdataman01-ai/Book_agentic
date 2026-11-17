"""Check that an agent's fraud explanation cites only what the model used (Chapter 8)."""
import re

def top_factors(attributions: dict, k: int = 4, min_share: float = 0.10) -> set:
    """Features that carry at least min_share of total absolute attribution, top k."""
    total = sum(abs(v) for v in attributions.values()) or 1.0
    ranked = sorted(attributions, key=lambda f: -abs(attributions[f]))
    return {f for f in ranked[:k] if abs(attributions[f]) / total >= min_share}

FACTOR = re.compile(r"\{factor:([a-z_]+)\}")

def check_explanation(text: str, attributions: dict) -> list[str]:
    """Return problems: cited factors the model did not rely on, or none cited."""
    cited = set(FACTOR.findall(text))
    allowed = top_factors(attributions)
    problems = [f"cites '{f}', which is not a top factor" for f in sorted(cited - allowed)]
    if not cited:
        problems.append("cites no model factor")
    return problems

if __name__ == "__main__":
    attr = {"amount_vs_history": 0.41, "new_device": 0.22, "merchant_risk": 0.15,
            "geo_distance_km": 0.04, "hour_of_day": 0.02}
    good = ("Amount is 9x the cardholder's usual {factor:amount_vs_history}, "
            "on a device never seen before {factor:new_device}.")
    bad = ("Unusual location {factor:geo_distance_km} at night {factor:hour_of_day}.")
    print("good:", check_explanation(good, attr) or "ok")
    print("bad: ", check_explanation(bad, attr))
