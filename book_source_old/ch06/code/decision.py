"""Parsing a reviewer's decision: the sample's way and a fail-closed way."""

def sample_parse(node_input):
    """As in ambient-expense-agent: any text containing 'approve' approves."""
    if isinstance(node_input, dict):
        return node_input.get("decision", "unknown")
    return "approve" if "approve" in str(node_input).lower() else "reject"

ALLOWED = {"approve", "reject", "request_info"}

def strict_parse(node_input, reviewer, invoice, authority):
    """Fail closed: only a well-formed decision from an authorized reviewer counts."""
    if not isinstance(node_input, dict):
        return "invalid", "Decision must come from the review form, not free text."
    decision = node_input.get("decision")
    if decision not in ALLOWED:
        return "invalid", f"Unknown decision {decision!r}."
    if decision == "approve":
        if reviewer == invoice["requester"]:
            return "invalid", "Requester cannot approve their own invoice."
        if invoice["amount"] > authority.get(reviewer, 0):
            return "invalid", "Amount exceeds this reviewer's approval limit."
    return decision, ""

if __name__ == "__main__":
    for text in ["approve", "Do not approve", "I disapprove", "rejected"]:
        print(f"{text!r:18} -> sample: {sample_parse(text)}")
    inv = {"amount": 48_000, "requester": "kim"}
    limits = {"lee": 25_000, "ortiz": 100_000}
    print(strict_parse("approve", "ortiz", inv, limits))
    print(strict_parse({"decision": "approve"}, "lee", inv, limits))
    print(strict_parse({"decision": "approve"}, "ortiz", inv, limits))
