# Lab 6: A Checkpoint That Holds

**Chapter 6 — Case: Invoice to Payment** · Time: about 3 hours · Cloud: **yes**

## Goal

Build design D2 from the sample, run it in **shadow mode** on a synthetic month of invoices, set the review threshold from the results, and show that the human checkpoint **resists unauthorized and malformed decisions**.

## What you will learn

- How to build a human-in-the-loop checkpoint with ADK workflows and `RequestInput` (Section 6.5).
- Why the decision must be parsed strictly and fail closed.
- How to set a review threshold from cost, not from a feeling (Section 6.7).

## Before you start

- Setup is done. Estimated credit used: **about $5–10**. Pub/Sub and Cloud Run usage at this scale is within the always-free tier; most of the cost is model calls.
- You have read Sections 6.3–6.7.

## What's in this folder

```
ch06/
├── README.md
├── .env.example
├── requirements.txt
├── vendor/ambient-expense-agent/   ← Google's sample, pinned at 1b20a7a
├── terraform/                      ← the sample's Terraform, plus the invoice topic
├── data/
│   ├── erp/                        ← synthetic vendors, purchase orders, receipts
│   ├── invoices_9500.jsonl         ← one synthetic month; 340 have a problem
│   └── test_expenses.jsonl         ← three test expenses for Step 1
├── invoice_flow/
│   ├── controls.py                 ← TODO: match, duplicates, bank-detail check
│   ├── decision.py                 ← strict_parse (Listing 6.x)
│   └── workflow.py                 ← TODO: assemble the workflow
├── tests/test_controls.py          ← TODO: add your tests
├── publish_invoices.py
├── review_policy.py                ← computes the review-policy table
├── control_attacks.py
└── cleanup.sh
```

---

## Steps

### Step 1 — Deploy the sample and test it as published [Build] [Design]

```bash
$ cd ch06
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
$ cd terraform && terraform init && terraform apply -var="project=$GOOGLE_CLOUD_PROJECT" && cd ..
```

Send the three test expenses:

```bash
$ python vendor_send.py data/test_expenses.jsonl
```

The third expense pauses for approval. Resume it with the text **"do not approve"**:

```bash
$ python vendor_send.py --resume <session-id> --text "do not approve"
```

**Checkpoint:** record the outcome. Was the expense approved? Look at how the sample parses the reply and explain why.

### Step 2 — Write the controls [Build]

Complete `invoice_flow/controls.py`:

| Function | Rule |
|---|---|
| `three_way_match(invoice, po, receipt)` | Quantities and prices within the tolerances in the chapter |
| `find_duplicates(invoice, history)` | Same vendor, amount and date window, or same invoice number with different formatting |
| `bank_details_changed(invoice, vendor)` | Bank details differ from the vendor master |

Add tests to `tests/test_controls.py`, using the synthetic ERP in `data/erp/`.

```bash
$ pytest tests/ -q
```

**Checkpoint:** all tests pass without a model.

### Step 3 — Assemble the workflow [Build]

Open `invoice_flow/workflow.py` and assemble the workflow from the chapter's listing: intake → controls → risk scoring → route → (auto-approve | human review via `RequestInput`) → decision → post.

Replace the sample's decision node with `strict_parse` from `decision.py`, which accepts only the structured payload `{"decision": "approve" | "reject", "approver_id": ..., "invoice_id": ...}` and **fails closed** on anything else.

```bash
$ adk web     # choose invoice_flow
```

**Checkpoint:** send one invoice that needs review. Reply with free text "do not approve" — the workflow must **not** approve it.

### Step 4 — Run a month in shadow mode [Build]

Deploy the workflow and publish the month:

```bash
$ ./deploy_workflow.sh --shadow
$ python publish_invoices.py data/invoices_9500.jsonl --rate 200
```

In shadow mode, the workflow logs what it **would** do but posts nothing. Processing takes about 30–40 minutes.

Then compute the review-policy table from the workflow's own logs:

```bash
$ python review_policy.py --from-logs
```

**Checkpoint:** a table like the chapter's Table 6.2 — for each review policy (review all, review none, thresholds on risk score): invoices reviewed, problems caught, exposure missed, review cost, total cost. Choose a threshold, and write two sentences explaining it. (For comparison, the chapter's simulation chose a risk score of about 0.37, reviewing about 550 invoices.)

### Step 5 — Attack the checkpoint [Build]

```bash
$ python control_attacks.py
```

The script tries three attacks:
1. approval by a user **without** the approver role,
2. approval by the **requester** of the invoice (separation of duties),
3. approval with an **edited decision payload** (changed amount or invoice ID).

**Checkpoint:** all three are refused, and each refusal is in the log with the reason.

### Step 6 — Clean up

```bash
$ ./cleanup.sh
```

**Checkpoint:** `terraform destroy` completes, and `gcloud run services list` and `gcloud pubsub topics list` show none of the lab's resources.

---

## Deliverable

1. The review-policy table from **your** run.
2. Your chosen threshold and its justification.
3. The control-attack results.
4. One paragraph answering: **which of the sample's gaps would an external auditor find first?**

**Design track:** your instructor provides the logs. Do Step 1, run `review_policy.py --from-logs results/`, and complete the deliverable.

## Troubleshooting

| Problem | Fix |
|---|---|
| Invoices never reach the workflow | Check the push subscription points at the service URL, and the service account has `run.invoker`. |
| `review_policy.py` finds no logs | Logs can take a minute to arrive; check the `LOG_FILTER` in `.env`. |
| The workflow approves malformed replies | The decision node still uses the sample's parser — replace it with `strict_parse`. |
| Shadow run is slow | Raise `--rate`, or reduce to the 2,000-invoice subset with `--sample 2000`. |
