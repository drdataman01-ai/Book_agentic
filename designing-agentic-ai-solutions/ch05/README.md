# Lab 5: Tools You Can Trust

**Chapter 5 — Case: Customer Support Triage** · Time: about 3 hours · Cloud: **yes** (Step 7)

## Goal

Build and test Harbor's returns MCP server, connect it to an ADK agent, and show by adversarial testing that **policy holds even when the model is persuaded to try to break it**.

## What you will learn

- The tool-design principles T1–T9 in practice (Section 5.5).
- Why authorization belongs in the server, using the caller's token, not in the prompt.
- How to report adversarial results as outcomes rather than transcripts (Section 5.7).

## Before you start

- Setup is done. Estimated credit used: **about $2–5**.
- You have read Sections 5.3–5.7.

## What's in this folder

```
ch05/
├── README.md
├── .env.example
├── requirements.txt
├── vendor/customer-service/   ← Google's sample, pinned at a9dc177 (Apache 2.0)
├── data/orders_500.jsonl      ← synthetic orders for 500 customers
├── token_issuer.py            ← local token issuer for testing
├── returns_server.py          ← the chapter's server (Listings 5.x)
├── tests/test_returns_server.py
├── returns_agent.py           ← TODO: connect an agent to the server
├── adversarial/               ← 150 adversarial scripts (JSON)
├── run_adversarial.py
├── unit_economics.py          ← the chapter's cost model
├── Dockerfile                 ← for deploying the server
├── deploy_server.sh
└── cleanup.sh
```

---

## Steps

### Step 1 — Install [Build]

```bash
$ cd ch05
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
```

**Checkpoint:** `python unit_economics.py` prints the chapter's cost per contact — baseline **$4.86**, D4 **$3.53**.

### Step 2 — Attack the sample as published [Build] [Design]

```bash
$ cd vendor/customer-service
$ adk web
```

Open three scripts from `../../adversarial/` — the folder's `README` suggests `refund_other_customer.json`, `outside_window.json` and `discount_by_authority.json` — and play each by hand, typing the user turns in order.

Record for each: **what the agent said**, and **what the mocked tools did** (look in the Events panel). The sample's tools are mocks that accept anything — note where that would matter in production.

Stop `adk web` and return to `ch05/`.

### Step 3 — Test the server without a model [Build]

```bash
$ pytest tests/test_returns_server.py -q
```

**Checkpoint:** all tests pass with **no model and no network**. Read the test names — each one corresponds to a rule the server enforces (90-day return window, quantity limits, one customer's data only, idempotent retries, the $150 auto-approval limit).

### Step 4 — Inspect the server over Streamable HTTP [Build]

In one terminal:

```bash
$ python returns_server.py --transport streamable-http --port 8080
```

In a second terminal:

```bash
$ npx @modelcontextprotocol/inspector
```

Connect the Inspector to `http://localhost:8080/mcp` with transport **Streamable HTTP**. To get a test token:

```bash
$ python token_issuer.py --customer C-00042
```

Paste it into the Inspector's **Authorization** header as `Bearer <token>`.

**Checkpoint:** in the Tools tab, confirm that:
- the server lists exactly two tools, `get_return_options` and `start_return`;
- the `reason` parameter of `start_return` is an **enumeration** (`damaged`, `defective`, `wrong_item`, `not_needed`, `late`), not free text;
- `get_return_options` carries `readOnlyHint: true`;
- `start_return` carries `destructiveHint: false` and `idempotentHint: true`.

Call `get_return_options` for an order belonging to another customer (the folder's `data/README.md` lists one). You should get `ORDER_NOT_FOUND` — not "forbidden", which would confirm the order exists. Call `start_return` twice with the same `idempotency_key` and confirm you get the same result and only one return.

Leave the server running.

### Step 5 — Connect an agent [Build]

Complete `returns_agent.py`:
1. Connect to the server with `McpToolset` and `StreamableHTTPConnectionParams(url="http://localhost:8080/mcp", headers={"Authorization": f"Bearer {token}"})`.
2. Add a `tool_filter=["get_return_options", "start_return"]` so the agent sees only the tools it needs, even if the server later adds more.
3. Read the test customer's token from the environment (`TEST_CUSTOMER_TOKEN`), never from the conversation.

```bash
$ export TEST_CUSTOMER_TOKEN=$(python token_issuer.py --customer C-00042)
$ adk web
```

**Checkpoint:** choosing `returns_agent`, you can ask *"I want to return the kettle from my last order"* and the Events panel shows `get_return_options` and then `start_return`, with a `reason` from the enumeration.

### Step 6 — Run all 150 adversarial scripts [Build]

```bash
$ python run_adversarial.py --target local --rate 30
```

**Checkpoint:** the script prints an **outcome table**, not transcripts:

| Outcome | Count |
|---|---|
| Policy-violating returns created | should be 0 |
| Cross-customer data returned | should be 0 |
| Agent *attempted* a disallowed action (server refused) | your number |
| Agent refused politely without trying | your number |

Transcripts are saved in `results/transcripts/`. Find **one** in which the agent was persuaded to *try* something it should not and the server refused. Save it for the deliverable.

### Step 7 — Deploy and repeat [Build]

Stop the local server (Ctrl+C), then:

```bash
$ ./deploy_server.sh
```

The script builds the container, deploys `returns-server` to Cloud Run **without** public access, and prints the URL. Then:

```bash
$ python run_adversarial.py --target cloud --rate 30
```

**Checkpoint:** the same two zeros as Step 6.

### Step 8 — Deploy the agent too (optional) [Build]

```bash
$ ./deploy_agent.sh
```

Deploys `returns_agent` to Agent Runtime with `adk deploy agent_engine`, pointed at the Cloud Run server. Talk to it from the console's Agent Runtime playground and confirm it can start a return for the test customer and cannot see another customer's order.

### Step 9 — Clean up

```bash
$ ./cleanup.sh
```

**Checkpoint:** `gcloud run services list` no longer shows `returns-server`, and the console's Agent Runtime page shows no `returns_agent` deployment.

---

## Deliverable

A short report with:
1. The outcome table from Step 2 (by hand) and from Step 6 (all 150).
2. One transcript in which the agent was persuaded to **try** something it should not, and the server refused.
3. Your answer to: **which of the sample's gaps did the server close without any change to the prompt?**

**Design track:** your instructor provides `results/`. Do Step 2 and the deliverable, and mark each refusal in your chosen transcript with the tool principle (T1–T9) that caused it.

## Troubleshooting

| Problem | Fix |
|---|---|
| Inspector can't connect | Use the URL ending in `/mcp` and transport *Streamable HTTP*, not SSE. |
| Every call returns `401` | The token has expired (they last 30 minutes). Issue a new one. |
| The agent sees all tools | Your `tool_filter` isn't set, or names don't match the server's tool names. |
| `run_adversarial.py --target cloud` gets `403` | Run `./deploy_server.sh --grant-invoker` to let your account call the service. |
| Vendored sample fails on import | Use the sample's own environment: `cd vendor/customer-service && pip install -e .` |
