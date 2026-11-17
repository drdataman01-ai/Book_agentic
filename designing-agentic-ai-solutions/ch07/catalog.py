"""Safe-action catalog for Parcelpoint's incident agent (Chapter 7)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Action:
    name: str
    tier: int                 # 1 automatic, 2 needs on-call approval, 3 never
    reversible: bool
    max_blast_radius: float   # share of traffic the action may affect

CATALOG = {
    "scale_within_limits": Action("scale_within_limits", 1, True, 1.00),
    "restart_one":         Action("restart_one", 1, True, 0.05),
    "rollback_last":       Action("rollback_last", 2, True, 1.00),
    "failover_region":     Action("failover_region", 2, True, 1.00),
    "flush_cache":         Action("flush_cache", 3, False, 1.00),
}

def authorize(name: str, ctx: dict) -> tuple[str, str]:
    """Return ('auto' | 'approval' | 'deny', reason). Unknown means deny."""
    a = CATALOG.get(name)
    if a is None or a.tier == 3:
        return "deny", "Not in the catalog for agents."
    if ctx["blast_radius"] > a.max_blast_radius:
        return "deny", "Affects more traffic than this action allows."
    if ctx.get("change_freeze"):
        return "approval", "Change freeze: a person must approve."
    if ctx["actions_this_incident"] >= 3:
        return "approval", "Action budget for this incident reached."
    if a.tier == 1 and a.reversible and ctx["preconditions_met"]:
        return "auto", "Tier 1, reversible, preconditions hold."
    return "approval", "Tier 2 or preconditions not met."

if __name__ == "__main__":
    base = dict(blast_radius=0.02, preconditions_met=True, actions_this_incident=0)
    for name, extra in [("restart_one", {}), ("restart_one", {"blast_radius": 0.3}),
                        ("rollback_last", {}), ("scale_within_limits", {"change_freeze": True}),
                        ("flush_cache", {}), ("delete_volume", {})]:
        print(f"{name:20s} {authorize(name, {**base, **extra})}")
