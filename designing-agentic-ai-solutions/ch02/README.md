# Lab 2: Measuring Two Designs

**Chapter 2 — The Designer's Toolkit** · Time: about 90 minutes · Cloud: Gemini only (nothing deployed)

## Goal

Replace three of the *estimated* scores in the chapter's trade-off table — **quality, cost and human workload** — with *measurements*, by running the intake stage of designs D2 and D3 on the same sample of Harbor returns.

## What you will learn

- How to turn a trade-off table from opinion into evidence (Section 2.6).
- How to implement a decision rule as plain, testable code rather than as an instruction to a model (Section 2.8).
- How to choose a confidence threshold from data.

## Before you start

- You have completed [`../setup/README.md`](../setup/README.md) (or the local route).
- You have read Sections 2.3–2.8, including the decision record and the failure walk-through for D3.

## What's in this folder

```
ch02/
├── README.md
├── .env.example
├── requirements.txt
├── data/
│   ├── returns_200.jsonl     ← 200 synthetic return requests with the correct outcome
│   └── warranty_table.csv
├── stubs/
│   ├── erp_server.py         ← stub MCP server for the ERP
│   └── shipping_server.py    ← stub MCP server for shipping labels
├── router/                   ← the provided router agent
├── run_router.py
├── safe_zone.py              ← TODO: you write the rule here
├── tests/test_safe_zone.py   ← TODO: you write the tests here
├── simulate.py
├── sweep_threshold.py
├── tradeoff.py               ← the chapter's trade-off and sensitivity script
└── results/                  ← scripts write their output here
```

---

## Steps

### Step 1 — Install [Build]

```bash
$ cd ch02
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
```

**Checkpoint:** `python tradeoff.py` prints the chapter's table and reports that **D3 wins in about 85% of** the weight perturbations. This is your starting point — every score in it is still an estimate.

### Step 2 — Run the router on all 200 requests [Build]

```bash
$ python run_router.py --rate 30
```

The script sends each request to the router agent, which classifies it (`in_warranty`, `out_of_warranty`, `needs_review`, …) and returns a confidence score.

**Checkpoint:** the script prints routing accuracy against the labels and writes `results/router_runs.csv` with one row per request: `request_id, label, predicted, confidence, tokens_in, tokens_out`.

Record the routing accuracy in your notes.

### Step 3 — Write the safe-zone rule as code [Build]

Open `safe_zone.py`. Implement `in_safe_zone(request, router_result, threshold)` so that it returns `True` only when **all** the conditions in the chapter's decision record hold, **including the two changes from the failure walk-through**.

Then write unit tests in `tests/test_safe_zone.py`. At least one test per condition, plus one for each failure-walk-through change.

> **Rule:** these tests must not call a model. They pass in fixed `router_result` values. If your test needs the network, it is testing the wrong thing.

```bash
$ pytest tests/ -q
```

**Checkpoint:** all tests pass, and they run in under a second.

### Step 4 — Simulate both designs [Build]

```bash
$ python simulate.py --design D2
$ python simulate.py --design D3 --threshold 0.8
```

The script assumes a representative takes **4 minutes per review**. For each design it reports:
- share of correct outcomes,
- model cost per request,
- representative minutes per 100 requests.

**Checkpoint:** both runs print those three numbers and write `results/sim_D2.json` and `results/sim_D3.json`. Copy the numbers into the measurements table in your notes.

### Step 5 — Choose the threshold [Build] [Design]

```bash
$ python sweep_threshold.py --from 0.5 --to 0.95 --step 0.05
```

**Checkpoint:** `results/threshold_sweep.png` shows correct outcomes (y) against the share of requests handled automatically (x), one point per threshold.

Choose a threshold and write two sentences explaining why — what you gain and what you give up compared with the next threshold up and down.

Rerun Step 4 for D3 with your chosen threshold.

### Step 6 — Update the trade-off table [Build] [Design]

1. Convert each measurement to a 1–5 score using the anchors in the chapter's criteria table (Table 2.5).
2. Open `tradeoff.py` and replace the estimated quality, cost and workload scores for D2 and D3 with your measured scores. Add a comment `# MEASURED` beside each one you changed.
3. Rerun:
   ```bash
   $ python tradeoff.py
   ```

**Checkpoint:** the script prints a new table and a new win share. Note whether D3 still wins, and how robust the result is.

### Step 7 — Revise the decision record [Design]

Copy `../templates/decision_record.md` and revise the chapter's decision record. If the decision changed, name the **reversal trigger** that fired.

### Step 8 — Clean up

Nothing was deployed. Deactivate the environment with `deactivate`.

---

## Deliverable

1. The updated trade-off table, with measured scores marked.
2. `results/threshold_sweep.png` and your chosen threshold with its justification.
3. The revised decision record. State whether the measurements changed the decision and, if so, which reversal trigger fired.

**Design track:** your instructor provides `results/` from a complete run. Do Steps 5–7.

## Troubleshooting

| Problem | Fix |
|---|---|
| `429 RESOURCE_EXHAUSTED` during Step 2 | Rerun with `--rate 10`. The script resumes from where it stopped. |
| Routing accuracy looks far too low (< 50%) | Check `MODEL_NAME` in `.env` matches `.env.example`. |
| `tradeoff.py` win share didn't change | Check you edited the scores for both D2 and D3, and saved the file. |
| Your safe-zone tests need the network | Pass a fixed dictionary as `router_result`; don't call `run_router`. |
