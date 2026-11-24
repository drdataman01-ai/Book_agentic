"""A tamper-evident audit trail for onboarding decisions (Chapter 10).

Each entry includes the hash of the previous entry, so changing or deleting
any past entry breaks the chain from that point on. Production systems also
write to write-once storage; the chain lets anyone verify the copy they hold.
"""
import hashlib, json
from datetime import datetime, timezone

GENESIS = "0" * 64

def _digest(entry: dict) -> str:
    return hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()

def append(log: list[dict], actor: str, action: str, case_id: str, **details) -> dict:
    entry = {
        "seq": len(log),
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "actor": actor,            # person, agent name+version, or rule name+version
        "action": action,
        "case_id": case_id,
        "details": details,        # inputs referenced by hash or ID, never raw documents
        "prev": log[-1]["hash"] if log else GENESIS,
    }
    entry["hash"] = _digest(entry)
    log.append(entry)
    return entry

def verify(log: list[dict]) -> int | None:
    """Return the first sequence number where the chain is broken, or None."""
    prev = GENESIS
    for e in log:
        body = {k: v for k, v in e.items() if k != "hash"}
        if e["prev"] != prev or _digest(body) != e["hash"]:
            return e["seq"]
        prev = e["hash"]
    return None

if __name__ == "__main__":
    log: list[dict] = []
    append(log, "doc_agent@2.3 / prompt v14", "extracted", "K-881", doc_sha256="9f2c...e1")
    append(log, "sanctions_screen@vendor-api v5", "screened", "K-881", hits=0)
    append(log, "risk_rule@v7", "rated", "K-881", rating="medium", factors=["cash-intensive NAICS"])
    append(log, "analyst:j.osei", "approved", "K-881", reason_code="EDD-COMPLETE")
    print("chain intact, first break at:", verify(log))
    log[2]["details"]["rating"] = "low"          # someone edits history
    print("after edit,  first break at:", verify(log))
