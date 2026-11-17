# Lab 11: Beat the Baseline

**Chapter 11 — Case: Demand Forecasting and Replenishment** · Time: about 3 hours (most of it the backtest running) · Cloud: optional (Step 6 runs the batch as a Cloud Run job, on CPU)

## Goal

Backtest a time-series foundation model against statistical baselines on synthetic grocery data, apply a decision rule written **in advance**, and serve the winner through an MCP server.

## What you will learn

- Why orders use a quantile, not the mean — the newsvendor rule (equation 11.1).
- How to run a rolling-origin backtest and score it with pinball loss at the critical ratio (Section 11.7).
- How to replace assumed compute costs with measured ones.

## Before you start

- Setup is done (or the local route). Estimated credit used: **under $2**; the backtest runs on your computer.
- You have read Sections 11.3–11.7.
- **Free-trial note:** the free trial does not allow GPUs, so this lab runs the foundation model **on CPU**. It is sized for that: the backtest uses 2,000 series and a small pinned model. Expect the foundation-model backtest to take 30–60 minutes on a laptop.

## The decision rule (written before you run anything)

From Section 11.7:

> The foundation model is adopted if it improves **simulated profit on fresh items by at least 2%** over the statistical models, with **no product category worse by more than 1%**.

Do not change this rule after you see the results.

## What's in this folder

```
ch11/
├── README.md
├── .env.example
├── requirements.txt
├── data/
│   ├── sales_2y.parquet       ← two years of daily sales, 2,000 store–product series
│   ├── calendar.parquet       ← promotions and holidays
│   └── products.csv           ← price, unit cost, shelf life, category → critical ratio
├── backtest.py
├── models/
│   ├── baselines.py           ← moving average, seasonal exponential smoothing (ETS)
│   └── tsfm.py                ← pinned time-series foundation model wrapper
├── decide.py                  ← applies the decision rule
├── forecast_server/
│   └── server.py              ← TODO: get_forecast, what_if
├── replenish.py               ← the chapter's compute-budget model
├── measure_throughput.py
├── job/                       ← Dockerfile and deploy script for Step 6
└── tests/
```

---

## Steps

### Step 1 — Install and load the data [Build]

```bash
$ cd ch11
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt       # includes the CPU build of PyTorch
$ cp .env.example .env
$ python backtest.py --describe
```

**Checkpoint:** the script prints 2,000 series, 730 days, the share of fresh items, and the range of critical ratios (for fresh items, typically between about 0.3 and 0.7). Also run `python replenish.py` — it prints the chapter's planning figures: a critical ratio of **0.37** for the example item, and an **assumed** nightly batch of **0.53 GPU-hours, $1.33 a night** for the full 480,000-series catalog.

### Step 2 — Run the rolling-origin backtest [Build]

```bash
$ python backtest.py --models ma ets --weeks 26
$ python backtest.py --models tsfm --weeks 26 --device cpu --batch-size 64
```

Each week in the last 26, the script forecasts the next 7 days using only data before that week, then compares with what actually sold. The baselines take a few minutes; the foundation model takes longer.

**Checkpoint:** `results/backtest.parquet` has a row per series, origin and model. The script prints, for each model:
- **pinball loss** at each product's critical ratio (lower is better),
- MASE, for comparison across products,
- **simulated profit** from ordering with that forecast through the newsvendor rule, overall and by category.

> Short on time? Add `--series 500` to backtest a stratified quarter of the series.

### Step 3 — Apply the decision rule [Build] [Design]

```bash
$ python decide.py results/backtest.parquet
```

**Checkpoint:** the script prints the profit improvement on fresh items, the worst category, and `ADOPT` or `DO NOT ADOPT`. Write down the decision and the numbers behind it.

### Step 4 — Serve the winning forecasts [Build]

Write the winning model's forecasts for the next 7 days to the store:

```bash
$ python backtest.py --publish --model <winner>
```

Complete `forecast_server/server.py`:

| Tool | Does |
|---|---|
| `get_forecast(store, product, date)` | returns the quantiles and the order quantity at the product's critical ratio — **read-only**, from the store |
| `what_if(store, product, change)` | reruns the foundation model for one series with a change (a promotion, a price change, a holiday) and returns the new quantiles. Rate-limited; never writes to the store |

```bash
$ pytest tests/test_forecast_server.py -q
$ npx @modelcontextprotocol/inspector python forecast_server/server.py
```

**Checkpoint:** in the Inspector, `get_forecast` returns in well under a second; `what_if` for a promotion raises the upper quantiles.

### Step 5 — Measure throughput and correct the budget [Build]

```bash
$ python measure_throughput.py --device cpu --series 2000
```

**Checkpoint:** the script prints series per second and the time and cost to forecast all 2,000 series on your hardware. Replace the **assumed** GPU throughput in `replenish.py` with your CPU measurement (mark it `# MEASURED`, and note the hardware), and rerun it to get the time and cost per night for the full 480,000-series catalog on CPU.

### Step 6 — Run the batch as a Cloud Run job (optional) [Build]

```bash
$ ./job/deploy_job.sh
$ gcloud run jobs execute forecast-batch --region=$GOOGLE_CLOUD_LOCATION --wait
```

This runs the nightly batch for 2,000 series as a **CPU-only** Cloud Run job. Compare its run time and cost with your laptop.

### Step 7 — Clean up

```bash
$ ./job/cleanup.sh       # only if you did Step 6
```

---

## Deliverable

1. The backtest table: pinball loss, MASE and simulated profit by model, overall and by category.
2. The decision, with the numbers that triggered it.
3. The corrected compute budget from Step 5, and a sentence on whether the chapter's design would still run nightly within its deadline on CPU — and when it would need accelerators.

**Design track:** your instructor provides `results/`. Do Step 3 and the deliverable, and explain in one paragraph why pinball loss at the critical ratio is a better metric for this decision than MAPE.

## Troubleshooting

| Problem | Fix |
|---|---|
| The foundation model runs out of memory | Lower `--batch-size` to 16. |
| The backtest is too slow | Use `--series 500`; the decision rule still applies. |
| Model weights won't download | They are fetched once from the pinned source in `.env.example`; check your network, or ask your instructor for the cached copy. |
| `decide.py` says a category is missing | Every category needs at least one fresh product in your sample; use the stratified `--series` option. |
