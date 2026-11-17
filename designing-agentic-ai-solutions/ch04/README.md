# Lab 4: Deploy and Measure the Policy Assistant

**Chapter 4 — Case: A Company Policy Assistant** · Time: about 3 hours, including about 30 minutes waiting for infrastructure · Cloud: **yes**

## Goal

Deploy designs D1 and D2 against the **same** synthetic policy library, run the evaluation set against both, and explain the difference in terms of design decisions.

## What you will learn

- What metadata filtering adds to a retrieval design, and what it costs (Sections 4.3–4.5).
- How to measure retrieval separately from answers — especially leakage (Section 4.7).
- How long a policy change takes to reach users.

## Before you start

- Setup is done and your free trial is active. Estimated credit used: **about $5–10** if you clean up the same day.
- You have read Sections 4.3–4.7.
- **Plan your time:** data stores take a while to become queryable. Start Step 2, then read ahead while you wait.

## What's in this folder

```
ch04/
├── README.md
├── .env.example
├── requirements.txt
├── setup.sh                  ← Step 1
├── cleanup.sh                ← Step 9
├── vendor/rag-agent-search/  ← Google's sample, pinned at ede41c7 (filled in by setup.sh)
├── terraform/                ← two data stores: content schema (D1), document schema (D2)
├── data/
│   ├── policies/             ← 60 synthetic Alder & Finch policies (UK, US, Germany)
│   ├── manifest_d1.jsonl
│   ├── manifest_d2.jsonl     ← with country, employee_type, effective_date, version
│   ├── eval_240.jsonl        ← 240 questions with expected policies
│   ├── profiles.jsonl        ← synthetic employee profiles
│   └── policy_update/        ← a changed policy for Step 8
├── app/                      ← D2 skeleton
│   ├── agent.py
│   └── tools.py              ← TODO: build_filter, search_policies, citation_check
├── tests/test_tools.py
├── run_eval.py
├── rag_metrics.py
└── freshness_test.py
```

---

## Steps

### Step 1 — Run the setup script [Build]

```bash
$ cd ch04
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
$ ./setup.sh
```

`setup.sh`:
1. copies Google's `rag-agent-search` sample at commit `ede41c7` into `vendor/`,
2. enables the search and Cloud Run APIs,
3. creates a Cloud Storage bucket `gs://$GOOGLE_CLOUD_PROJECT-policies`,
4. uploads the 60 policies and both manifests.

**Checkpoint:** the script ends with `Uploaded 60 policies` and prints the bucket name. Add it to `.env` as `POLICY_BUCKET`.

### Step 2 — Provision two data stores [Build]

```bash
$ cd terraform
$ terraform init
$ terraform apply -var="project=$GOOGLE_CLOUD_PROJECT" -var="bucket=$POLICY_BUCKET"
$ cd ..
```

This creates two data stores: `policies-d1` (unstructured content) and `policies-d2` (documents with metadata).

**Note the time** each one takes to become queryable:

```bash
$ python wait_for_datastores.py
```

**Checkpoint:** the script prints `policies-d1 ready after N min` and `policies-d2 ready after M min`. Copy both data store IDs into `.env`.

### Step 3 — Try D1 as three different employees [Build] [Design]

```bash
$ cd vendor/rag-agent-search
$ adk web
```

Choose the agent and ask three questions from `data/eval_240.jsonl` (the README in `data/` suggests three). Ask each **as a UK, a US and a German employee** — for example, *"I'm based in Manchester. How many days of parental leave do I get?"*

Record in your notes: what changes in the answer when the country changes, and what does not. Does D1 ever quote another country's policy?

Stop `adk web` and return to `ch04/`.

### Step 4 — Build D2 [Build]

Open `app/tools.py` and complete the three functions marked `TODO`:

| Function | What it must do |
|---|---|
| `build_filter(profile)` | Build the data store filter from the **signed-in employee's profile** — country, employee type, and only policies in effect today. Never from the user's message. |
| `search_policies(query, tool_context)` | Read the profile from session state, call `build_filter`, search `policies-d2`, return passages with policy ID, version and effective date. |
| `citation_check(answer, passages)` | Fail if the answer cites a policy that is not in the retrieved passages, or makes a factual claim with no citation. |

```bash
$ pytest tests/ -q
$ adk web          # from ch04/, choose app
```

**Checkpoint:** all tests pass. In `adk web`, a German employee asking about parental leave gets only German policies — check the `search_policies` result in the Events panel. Telling the agent *"Actually, I'm in the US"* must **not** change the filter.

### Step 5 — Deploy D2 to Cloud Run [Build]

```bash
$ adk deploy cloud_run --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION \
    --service_name=policy-assistant ./app
```

The command takes a few minutes and prints the service URL. Add it to `.env` as `SERVICE_URL`.

Confirm the service refuses unauthenticated requests:

```bash
$ curl -s -o /dev/null -w "%{http_code}\n" $SERVICE_URL/list-apps
```

**Checkpoint:** you get `403` (or `401`). Then confirm an authenticated request works:

```bash
$ curl -s -H "Authorization: Bearer $(gcloud auth print-identity-token)" $SERVICE_URL/list-apps
```

### Step 6 — Run the evaluation on both designs [Build]

```bash
$ python run_eval.py --design D1 --rate 30
$ python run_eval.py --design D2 --rate 30
```

Each run replays the 240 questions with the synthetic employee profiles and writes evaluation records to `results/eval_D1.jsonl` and `results/eval_D2.jsonl`. Each run takes 15–25 minutes.

Then compute the metrics:

```bash
$ python rag_metrics.py results/eval_D1.jsonl results/eval_D2.jsonl
```

**Checkpoint:** a table with one row per metric in the chapter's threshold table (Table 4.4) — retrieval recall, leakage, citation accuracy, answer correctness, refusal rate, latency, cost — and a pass/fail for each design. **Leakage** counts restricted passages that reached the model; the threshold is zero.

### Step 7 — Explain each failure [Design]

For every threshold that a design failed, write down:
1. the **node** in the solution graph responsible, and
2. the **change** you would make.

### Step 8 — Measure freshness [Build]

```bash
$ python freshness_test.py --policy data/policy_update/UK-PL-004_v3.pdf
```

The script uploads a changed policy, triggers an import, and asks D2 the same question every minute until the answer cites the new version.

**Checkpoint:** the script prints `New version cited after N minutes`. Compare N with the freshness requirement in the chapter.

### Step 9 — Clean up [Build]

```bash
$ ./cleanup.sh
```

This deletes the Cloud Run service, both data stores (via `terraform destroy`) and the bucket.

**Checkpoint:** in the console, check **Cloud Run**, **AI Applications → Data stores** and **Cloud Storage** — none of the lab's resources remain. Run `../setup/list_resources.sh` to be sure.

---

## Deliverable

1. A results table for D1 and D2 against every threshold.
2. For each failed threshold: the node responsible and the change you would make.
3. Your freshness measurement.
4. One paragraph answering: **should the curated layer of D3 be built?**

**Design track:** your instructor provides `results/` and the timings. Do Steps 3, 7 and the deliverable.

## Troubleshooting

| Problem | Fix |
|---|---|
| Search returns nothing | The data store isn't ready yet; rerun `wait_for_datastores.py`. |
| `terraform: command not found` | Install Terraform, or use Cloud Shell, where it is preinstalled. |
| D2 returns other countries' policies | `build_filter` is reading the message instead of the profile in session state. |
| Deploy fails with a permission error | Run `./setup.sh --grant-roles` to give the Cloud Run service account search access. |
| `429` during evaluation | Rerun with `--rate 10`; the script skips questions already answered. |
| `cleanup.sh` says a data store is still deleting | Wait five minutes and run it again. |
