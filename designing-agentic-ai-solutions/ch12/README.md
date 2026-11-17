# Lab 12: Decide Where It Runs

**Chapter 12 — Case: Commercial Loan Underwriting Memo** · Time: about 3 hours · Cloud: **yes**

## Goal

Deploy the memo-drafting workflow's agents to **Agent Runtime** and its calculation server to **Cloud Run**, measure what each memo costs to produce, and replace the planning figures in the total-cost-of-ownership (TCO) model.

## What you will learn

- The rule from Chapter 1, at scale: **the model writes the words, code supplies the numbers** (Section 12.5).
- How to bound a reflection loop with a checklist critic.
- How to compare deployment targets — and build versus buy — with measured costs (Sections 12.4 and 12.6).

## Before you start

- Setup is done. Estimated credit used: **about $8–15** (10 full memos, each with six section agents and up to two critic rounds).
- You have read Sections 12.3–12.7.
- A full draft takes **10–20 minutes** per deal; start Step 3 and read while it runs.

## What's in this folder

```
ch12/
├── README.md
├── .env.example
├── requirements.txt
├── data/deals/              ← 10 synthetic deal files and financial spreads
├── calc_server/
│   ├── server.py            ← ratios, covenants, projections, sensitivities (MCP)
│   └── Dockerfile
├── memo_workflow/
│   ├── agent.py             ← section agents, critic, assembly
│   └── checklist.yaml       ← the credit policy's required-content checklist
├── guardrails/
│   ├── numbers_trace.py     ← every number in the text must come from a calculation
│   └── citations.py
├── run_drafts.py
├── usage_report.py          ← run time, model calls, tokens, cost per memo
├── tco.py                   ← the chapter's TCO model
├── deploy.sh / cleanup.sh
└── tests/
```

---

## Steps

### Step 1 — Install and load the deals [Build]

```bash
$ cd ch12
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
$ python run_drafts.py --load data/deals/
$ pytest tests/ -q
```

**Checkpoint:** 10 deals loaded; tests pass (they test the calculation server and the guardrails, with no model). Run `python tco.py` and note the chapter's planning figures: a three-year TCO of about **$1.29 million** for the Agent Runtime build, **$1.44 million** on Cloud Run, **$2.06 million** on GKE and **$1.73 million** for the vendor platform.

### Step 2 — Deploy [Build]

```bash
$ ./deploy.sh
```

The script:
1. builds and deploys the **calculation server** to Cloud Run (no public access) and prints its URL;
2. deploys the **memo workflow** to Agent Runtime with:
   ```bash
   adk deploy agent_engine --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION \
       --display_name=memo-workflow ./memo_workflow
   ```
   with `CALC_SERVER_URL` set to the Cloud Run URL;
3. grants the Agent Runtime service account permission to invoke the calculation server.

**Checkpoint:** the script prints the Agent Runtime resource name. Add it to `.env` as `AGENT_RESOURCE`.

### Step 3 — Generate the drafts and measure them [Build]

```bash
$ python run_drafts.py --all --target cloud
$ python usage_report.py
```

Drafts run in the background; `run_drafts.py` polls until all 10 are done and saves them to `results/drafts/`.

**Checkpoint:** `usage_report.py` prints, per memo and on average:
- run time,
- model calls (by agent),
- input and output tokens,
- **cost per memo** (model, plus Cloud Run and Agent Runtime time).

### Step 4 — Check the drafts [Build] [Design]

```bash
$ python guardrails/numbers_trace.py results/drafts/
$ python guardrails/citations.py results/drafts/
```

**Checkpoint:** the numbers trace reports every figure in each memo that **does not** match a calculation-server result. The target is zero. Open the critic's log for each deal (`results/critic/`) and record the gaps it found and whether the second round fixed them.

Pick one memo and read it as a credit officer would. List anything the checklist missed.

### Step 5 — Update the TCO model [Build] [Design]

Open `tco.py` and replace the planning `per_memo` figure for the Agent Runtime option with your **measured** cost per memo from Step 3 (mark it `# MEASURED`). Rerun:

```bash
$ python tco.py
```

**Checkpoint:** a new TCO table. Does the build option still beat the vendor? By how much does per-memo cost have to rise before the decision flips?

### Step 6 — Clean up

```bash
$ ./cleanup.sh
```

**Checkpoint:** the console's **Agent Runtime** page shows no `memo-workflow`, and `gcloud run services list` shows no `calc-server`. Agent Runtime deployments cost money while they exist — check twice.

---

## Deliverable

A **one-page deployment decision record** (use `../templates/decision_record.md`) with:
1. your measurements from Step 3,
2. the guardrail and critic results from Step 4,
3. the updated TCO table from Step 5,
4. your decision on where the workflow should run, and the reversal trigger.

**Design track:** your instructor provides `results/`. Do Steps 4 and 5 and the deliverable.

## Troubleshooting

| Problem | Fix |
|---|---|
| `adk deploy agent_engine` fails on staging bucket | Set `STAGING_BUCKET` in `.env`; `deploy.sh` creates it if missing. |
| Section agents can't reach the calculation server | The Agent Runtime service account needs `roles/run.invoker` on `calc-server`; rerun `./deploy.sh --grant`. |
| Numbers trace flags rounded figures | The trace allows the rounding rules in `checklist.yaml`; check the agent formats numbers as the server returns them. |
| A draft takes over 30 minutes | Check the critic loop stops after two rounds. |
| `429` errors | Run deals one at a time: `run_drafts.py --all --concurrency 1`. |
