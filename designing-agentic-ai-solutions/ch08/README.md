# Lab 8: Evaluating What Matters

**Chapter 8 — Case: Credit Card Fraud Review** · Time: about 3 hours · Cloud: **yes** (Step 7 deploys the scoring server to Cloud Run)

## Goal

Build the scoring server and the case agent on a synthetic labeled dataset, and produce an evaluation **a model risk manager would accept**.

## What you will learn

- Why fraud evaluation needs time-based splits and mature labels (Section 8.7).
- How to set review and block thresholds from cost, not accuracy (equation 3.2 and Section 8.7).
- How to check that a model-written explanation is faithful to the score it explains (Section 8.5).

## Before you start

- Setup is done. Estimated credit used: **about $2–5** (300 case summaries plus faithfulness checks; Cloud Run is within the free tier).
- You have read Sections 8.3–8.7.

## What's in this folder

```
ch08/
├── README.md
├── .env.example
├── requirements.txt
├── data/
│   ├── transactions_18m.parquet   ← 18 months of synthetic card-not-present transactions
│   └── labels.parquet             ← fraud labels with the date each label became known
├── train.py                       ← provided gradient-boosted scoring model
├── scoring_server/
│   └── server.py                  ← TODO: explain_score, similar_cases
├── case_agent/
│   └── agent.py                   ← TODO: case agent with output schema
├── faithfulness.py                ← the chapter's guardrail (top factors must match)
├── run_summaries.py
├── fraud_policy.py                ← the chapter's threshold and daily-cost model
├── label_delay.py
├── tests/
├── deploy_server.sh / cleanup.sh
└── templates/validation_report.md
```

---

## Steps

### Step 1 — Load the data and train [Build]

```bash
$ cd ch08
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
$ python train.py --train-months 1-12 --test-months 13-15
```

The labels file records, for every fraud label, the **date it became known**. `train.py` uses only labels known by the end of month 12 for training, and the test period (months 13–15) is old enough for its labels to have matured.

**Checkpoint:** the script prints the test-period fraud rate, the precision–recall AUC, and writes `models/scorer.joblib` and `results/test_scores.parquet`.

### Step 2 — Wrap the model in an MCP server [Build]

Complete `scoring_server/server.py` with two **read-only** tools:

| Tool | Returns |
|---|---|
| `explain_score(transaction_id)` | the score and the top feature attributions (SHAP values), with masked card number |
| `similar_cases(transaction_id, k=5)` | the *k* most similar past cases with their final outcome — **only cases whose labels have matured** |

```bash
$ pytest tests/test_scoring_server.py -q
```

**Checkpoint:** tests pass. In the MCP Inspector (`npx @modelcontextprotocol/inspector python scoring_server/server.py`), `explain_score` for a test transaction returns a score and four or more attributions, and no unmasked card numbers.

### Step 3 — Build the case agent and the guardrail [Build]

Complete `case_agent/agent.py`: an agent that calls both tools and writes a short case summary for the analyst, with an output schema containing `summary`, `factors_cited` and `recommendation` (`review`, `release` or `block`).

Attach `faithfulness.check_explanation` as an `after_agent_callback`: a summary fails if it cites factors that are **not** among the score's top factors, or omits a top factor.

Generate summaries for 300 test cases:

```bash
$ python run_summaries.py --n 300 --rate 30
```

**Checkpoint:** the script prints the **faithfulness pass rate** and writes `results/summaries.jsonl`. Read five failures and classify them: wrong factor, missing factor, or a factor described in the wrong direction.

### Step 4 — Recompute the thresholds [Build] [Design]

`fraud_policy.py` currently uses **simulated** scores. Run it as is, then with your model's test-period scores:

```bash
$ python fraud_policy.py
$ python fraud_policy.py --scores results/test_scores.parquet --review-minutes 6
$ python fraud_policy.py --scores results/test_scores.parquet --review-minutes 3.5
```

**Checkpoint:** each run prints the chosen review and block thresholds, alerts reviewed, fraud caught, false blocks and **total daily cost**. With simulated scores the chapter found about **$52,994 a day** at 6 minutes and **$48,533 a day** at 3.5 minutes. How do your numbers compare? What does a faster review buy?

### Step 5 — Show the cost of ignoring label delay [Build]

```bash
$ python label_delay.py --months 16-18
```

The script evaluates the model on months 16–18 twice: once with **all labels known today**, and once with **only the labels known at the end of each month**.

**Checkpoint:** the second evaluation shows a lower apparent fraud rate and an inflated precision. Write one paragraph explaining what a team would wrongly conclude if it evaluated this way.

### Step 6 — Write the validation report [Design]

Use `templates/validation_report.md` — **four pages**:
1. Purpose and intended use
2. Data and splits (with the label-delay rule)
3. Cost-based results (from Step 4)
4. Faithfulness results (from Step 3)
5. Limitations
6. Monitoring plan: what you will measure, how often, and what triggers a review

### Step 7 — Deploy the scoring server [Build]

```bash
$ ./deploy_server.sh
```

The script deploys `scoring-server` to Cloud Run with no public access, on CPU, with the model file baked into the container. Point the case agent at it (`SCORING_SERVER_URL` in `.env`) and rerun 20 summaries:

```bash
$ python run_summaries.py --n 20 --server cloud
```

**Checkpoint:** the faithfulness pass rate is in line with Step 3, and Cloud Run's metrics show the request latency of `explain_score`.

### Step 8 — Clean up

```bash
$ ./cleanup.sh
```

**Checkpoint:** `gcloud run services list` no longer shows `scoring-server`.

---

## Deliverable

The four-page validation report, with `results/` attached.

**Design track:** your instructor provides `results/`. Do Steps 4 (reading the outputs), 5 (explanation) and 6.

## Troubleshooting

| Problem | Fix |
|---|---|
| Training takes too long | Use `--sample 0.25`; the lab works on a quarter of the data. |
| Faithfulness pass rate near 0% | Check the agent receives the attributions from `explain_score`, and the schema's `factors_cited` uses the same feature names. |
| `similar_cases` returns recent cases | It must filter on the label's known date, not the transaction date. |
| `fraud_policy.py` can't read your scores | The file must have columns `transaction_id, score, label, amount`. |
