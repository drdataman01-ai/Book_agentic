"""Retrieval and answer metrics for a policy assistant (Chapter 4)."""
from dataclasses import dataclass, field

@dataclass
class Case:
    question: str
    gold_docs: set[str]          # documents that answer it; empty = policy is silent
    retrieved: list[str]         # document IDs in rank order
    cited: list[str]             # document IDs cited in the answer
    abstained: bool              # assistant declined and offered an HR ticket
    allowed: set[str] = field(default_factory=set)  # docs this employee may see

def recall_at_k(cases, k=5):
    answerable = [c for c in cases if c.gold_docs]
    hits = sum(bool(c.gold_docs & set(c.retrieved[:k])) for c in answerable)
    return hits / len(answerable)

def mrr(cases):
    answerable = [c for c in cases if c.gold_docs]
    total = 0.0
    for c in answerable:
        rank = next((i + 1 for i, d in enumerate(c.retrieved) if d in c.gold_docs), None)
        total += 1 / rank if rank else 0.0
    return total / len(answerable)

def citation_precision(cases):
    cites = [(d, c) for c in cases for d in c.cited]
    return sum(d in c.retrieved for d, c in cites) / len(cites) if cites else 1.0

def abstention(cases):
    silent = [c for c in cases if not c.gold_docs]
    answerable = [c for c in cases if c.gold_docs]
    recall = sum(c.abstained for c in silent) / len(silent)        # silent -> abstain
    false_abstain = sum(c.abstained for c in answerable) / len(answerable)
    return recall, false_abstain

def leakage(cases):
    return sum(any(d not in c.allowed for d in c.retrieved + c.cited) for c in cases)

if __name__ == "__main__":
    ALL = {"UK-LEAVE-v7", "US-LEAVE-v4", "GL-TRAVEL-v3", "UK-TRAVEL-v2", "MGR-PERF-v1"}
    staff = ALL - {"MGR-PERF-v1"}
    cases = [
        Case("How many days of annual leave do I get?", {"UK-LEAVE-v7"},
             ["UK-LEAVE-v7", "US-LEAVE-v4"], ["UK-LEAVE-v7"], False, staff),
        Case("Can I fly business class to Singapore?", {"UK-TRAVEL-v2"},
             ["GL-TRAVEL-v3", "UK-TRAVEL-v2"], ["UK-TRAVEL-v2"], False, staff),
        Case("Is there a policy on desk plants?", set(),
             ["GL-TRAVEL-v3"], [], True, staff),
        Case("How are performance ratings calibrated?", set(),
             ["MGR-PERF-v1"], [], True, staff),          # retrieved a manager-only doc
    ]
    print(f"recall@5            {recall_at_k(cases):.2f}")
    print(f"MRR                 {mrr(cases):.2f}")
    print(f"citation precision  {citation_precision(cases):.2f}")
    r, fa = abstention(cases)
    print(f"abstention recall   {r:.2f}   false abstention {fa:.2f}")
    print(f"cases with leakage  {leakage(cases)}")
