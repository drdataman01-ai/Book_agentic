# Lab 3: A Value Case You Can Defend

**Chapter 3 — The Business of AI Solutions** · Time: about 90 minutes · Cloud: none

## Goal

Produce a value case, a pilot plan and a memo for Harbor's returns design from Chapter 2, **using data rather than guesses wherever data exists**.

## What you will learn

- How to establish a baseline with honest uncertainty (Sections 3.2 and 3.4).
- How to separate measured inputs from assumed ones, and find the assumption a case rests on (Section 3.5).
- How to write go/no-go criteria and a one-page memo (Sections 3.10–3.11).

## Before you start

- You have read Chapter 3, especially the unit-economics equation (3.1) and the tornado analysis.
- No cloud account is needed. This lab runs entirely on your computer.

## What's in this folder

```
ch03/
├── README.md
├── requirements.txt
├── data/
│   ├── returns_12m.csv       ← 12 months of synthetic returns: timestamps, handling minutes, credit amounts
│   └── audit_sample.csv      ← 400 audited credits, marked in or out of warranty
├── baseline.ipynb            ← starter notebook for Step 2
├── value_case.py             ← the chapter's value-case script (the Alder & Finch example)
└── templates/
    ├── go_no_go.md
    └── memo.md
```

---

## Steps

### Step 1 — Install and explore [Build]

```bash
$ cd ch03
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python value_case.py
```

**Checkpoint:** `value_case.py` prints the chapter's example — a net value of about **$2.64 million** — and a tornado ranking with **win_rate_lift** at the top. You will now build the same thing for the returns case.

### Step 2 — Compute the baseline [Build] [Design]

Open `baseline.ipynb` (`jupyter lab baseline.ipynb`) or write a script. From `returns_12m.csv` and `audit_sample.csv`, compute:

| Measure | Statistic |
|---|---|
| Days from request to RMA | median and 90th percentile |
| Days from request to credit | median and 90th percentile |
| Representative minutes per return | median and mean |
| Out-of-warranty credit rate | rate with a **95% confidence interval** |

For the confidence interval, use the Wilson interval (the notebook has a helper).

**Checkpoint:** the out-of-warranty rate has an interval of a few percentage points either side — 400 audited credits is not a huge sample. Write down what that interval means for any saving you claim from catching those credits.

### Step 3 — Build the returns value case [Build]

```bash
$ cp value_case.py returns_value.py
```

Rewrite the inputs in `returns_value.py` for the returns case: return volume, minutes saved per return, loaded cost per minute, out-of-warranty credits avoided, model and platform costs, build and run costs.

Mark **every** input with a comment:

```python
minutes_per_return = 11.2   # MEASURED: baseline median, Step 2
auto_share = 0.55           # ASSUMED: from Lab 2 threshold sweep; to be confirmed in pilot
```

**Checkpoint:** every input line ends in a `MEASURED` or `ASSUMED` comment. Count how many of each you have.

### Step 4 — Find the assumption the case rests on [Build] [Design]

```bash
$ python returns_value.py
```

**Checkpoint:** the script prints the net value and a tornado ranking — the inputs ordered by how much the net value swings when each moves from its low to its high value.

Identify the **top input**. Is it measured or assumed? Write one paragraph: if this input is at its low value, is the case still worth doing?

### Step 5 — Write go/no-go criteria [Design]

Fill in `templates/go_no_go.md` for a **six-week pilot**. Include at least:
- one **error budget** (for example, a maximum rate of wrong credits), and
- one **adoption** criterion (for example, the share of returns representatives send through the new process).

Each criterion needs a threshold, a measurement method and a data source.

### Step 6 — Write the memo [Design]

Fill in `templates/memo.md` — **one page**: the problem, the recommendation, the value range (not one number), the key assumption, the pilot and its decision date, and the ask.

### Step 7 — Clean up

Nothing to clean up.

---

## Deliverable

1. The baseline table from Step 2.
2. `returns_value.py` and its tornado output.
3. The go/no-go table.
4. The one-page memo.
5. One paragraph: **how will the pilot measure the assumption your case rests on?**

**Design track:** use a spreadsheet instead of `returns_value.py` if you prefer; your instructor can provide one with the same inputs. The tornado can be done by changing one input at a time.

## Troubleshooting

| Problem | Fix |
|---|---|
| Your confidence interval includes negative numbers | You used the normal approximation; use the Wilson helper. |
| Every input looks like the top of the tornado | Check the low/high ranges are realistic, not ±100%. |
| `jupyter: command not found` | `pip install jupyterlab`, or run the analysis as a plain script. |
