# Solution graph checklist (W1–W8)

| Rule | Check | ✓ |
|---|---|---|
| W1 | Every agent states its autonomy level and stop condition. | |
| W2 | Every write action has a checkpoint or guardrail before it, or a note saying why not. | |
| W3 | No agent touches a system of record except through an MCP server. | |
| W4 | Thresholds and rules live in code nodes, not agent annotations. | |
| W5 | Every knowledge store names an owner and a freshness target. | |
| W6 | Every edge into an agent that crosses a trust boundary passes a guardrail. | |
| W7 | Every branch has its condition on the edge, and branches cover all cases. | |
| W8 | Every node (except triggers, users and systems of record) has a trace tag. | |
