# Capstone Project: A Cross-Department Solution

**Chapter 13 — Capstone: Cross-Department Operations** · Time: several weeks, in teams · Cloud: **yes**

## The brief

In teams of **three or four**, design, build and present a cross-department solution for a company of your choice — real or fictional — in which **at least two departments' agents or servers must cooperate**.

Harbor's order desk in Chapter 13 is an example. Others:
- **Hospital patient discharge** — clinical, pharmacy, transport, billing
- **University admissions** — admissions, financial aid, housing
- **Insurance claims** — intake, coverage, repair network, payments

Use synthetic data only.

## Deliverables

| # | Deliverable | Template | Due (14-week course) |
|---|---|---|---|
| 1 | **Business brief**: a measured or carefully estimated current-process map, SUAO stakeholders, KPIs and risks | `templates/business_brief.md` | Week 8 |
| 2 | **Solution graphs** for at least two alternatives, well formed under rules W1–W8, with each cross-team connection justified by Table 13.1 | `../templates/solution_graph_checklist.md`, `templates/connections.md` | Week 10 |
| 3 | **Trade-off table** with money rows where possible, a sensitivity check, a failure walk-through and a decision record | `../templates/tradeoff.py`, `../templates/failure_walkthrough.md`, `../templates/decision_record.md` | Week 12 |
| 4 | **A working deployment** of the chosen design on Google Cloud, with at least one MCP server and — if the design calls for it — one A2A connection, with an agent card for any A2A agent | `starter/` | Week 13 |
| 5 | **Evaluation report** with thresholds, results, and a release gate that your team's own final change passed | `release_gate.py`, `templates/eval_report.md` | Week 13 |
| 6 | **Operating-model page**: owners, risk tier, monitoring and adoption plan | `templates/operating_model.md` | Week 14 |
| 7 | **One-page memo**, presented to a panel playing the sponsor | `../templates/memo.md` | Week 14 |

Dates follow the 14-week plan in Appendix D (teams form in week 7). In the 10-week plan, teams form in week 7 and everything is due by the week-10 presentations. Your instructor may change the dates.

## Assessment

The rubric in Appendix D weights:

| Area | Weight |
|---|---|
| Design | 30% |
| Business case | 25% |
| Build and deployment | 20% |
| Evaluation | 15% |
| Presentation | 10% |

**Design-track teams** may substitute a clickable prototype and a detailed build plan for the deployment, with that weight moved to the business case and evaluation design.

## What's in this folder

```
ch13/
├── README.md
├── templates/            ← business brief, connections, eval report, operating model
├── starter/
│   ├── mcp_server/       ← a minimal MCP server (Streamable HTTP, token auth, read-only + one write tool)
│   ├── workflow_agent/   ← an ADK workflow that calls the server
│   ├── a2a_agent/        ← an A2A agent with an agent card, served on Cloud Run
│   ├── eval/             ← evaluation-record format and runner
│   ├── deploy.sh
│   └── cleanup.sh
├── release_gate.py       ← the chapter's release gate (fails closed)
└── examples/harbor_order_desk/   ← the chapter's example, as a reference
```

---

## How to work through it

### Step 0 — Form a team and set up the shared project

1. Form a team of three or four. Agree who owns each department's component — owners matter here, as in Section 13.3.
2. **One** team member creates the team project on their free trial and adds the others:
   ```bash
   $ gcloud projects add-iam-policy-binding $PROJECT \
       --member=user:teammate@example.com --role=roles/editor
   ```
   Teammates set `GOOGLE_CLOUD_PROJECT` in `../setup/course.env` to the team project.
3. Set a budget alert on the team project (see [`../setup/README.md`](../setup/README.md#set-a-budget-alert-recommended)). A team project spends one person's credit — share the cost of experiments.
4. Create a team repository from this folder and protect the main branch: every change goes through a pull request.

### Step 1 — Business brief [Design] (week 8)

Pick the company and the process. Map the current process with times and volumes — measured if you can get data, carefully estimated if not, and say which. Identify Sponsor, Users, Affected and Owners (SUAO). Turn the sponsor's goals into KPIs (Chapter 3).

**Check before you submit:** every number is marked measured or estimated; at least one KPI is one the sponsor would be paid on.

### Step 2 — Two alternatives [Design] (week 10)

Draw at least two solution graphs. Check each against W1–W8 (Section 2.2). For every connection between departments, fill in `templates/connections.md`: workflow step, MCP tool, or A2A agent — and why, using Table 13.1.

**Check:** a reviewer outside your team can say which department owns every node.

### Step 3 — Choose [Design] (week 12)

Copy `../templates/tradeoff.py`. Score both alternatives, with money rows where you can. Run the sensitivity check. Walk through at least three failures. Write the decision record, with reversal triggers.

### Step 4 — Build and deploy [Build] (weeks 12–13)

Start from `starter/`:

```bash
$ cd starter
$ python3 -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
$ pytest -q                          # the starter's tests pass before you change anything
$ ./deploy.sh                        # deploys the starter as-is, to check your project works
```

Then replace the starter components with your design. Requirements:
- **At least one MCP server**, tested without a model, deployed to Cloud Run without public access.
- If your design has an **A2A** connection: an agent card listing narrow, versioned skills, and identity passed with each request — **identity travels; trust does not**.
- Every tool that changes something is idempotent and authorized in code, not in a prompt.
- Model names, instructions and tool versions are **pinned** in configuration.

### Step 5 — Evaluate and gate [Build] (week 13)

Write your thresholds **before** you run the evaluation. Run it, then put your final change through the release gate:

```bash
$ python ../release_gate.py --candidate eval/results/candidate.json \
    --production eval/results/production.json
```

Edit the thresholds in `GATES` at the top of `release_gate.py` to the ones you wrote down — before you run it.

**Check:** the gate prints `go`. (`review` means a soft metric regressed against production — explain it in the report; `no-go` means a hard gate failed or a result is missing.) A missing result counts as a failure — that is deliberate. Include the gate output in the evaluation report.

### Step 6 — Operating model [Design] (week 14)

Fill in `templates/operating_model.md`: solution owner, platform dependencies, system owners, risk tier (from what your solution can change), monitoring, and the adoption plan — including what happens to the time you free up.

### Step 7 — Present (week 14)

Write the one-page memo and present it to the panel playing the sponsor. Expect questions on the assumption your case rests on.

### Step 8 — Clean up

After grading:

```bash
$ ./starter/cleanup.sh
$ ../setup/list_resources.sh
```

Delete anything still listed. The team member whose trial pays should check the Billing page.

---

## Submission checklist

- [ ] Business brief
- [ ] Two solution graphs, W1–W8 checked, connections justified
- [ ] Trade-off table, sensitivity check, failure walk-through, decision record
- [ ] Deployed system (URLs and a short demo video), or prototype and build plan (design track)
- [ ] Agent card(s), if A2A is used
- [ ] Evaluation report with release-gate output
- [ ] Operating-model page
- [ ] One-page memo and slides
- [ ] Repository link, with a README that tells a new team member how to run it

## Troubleshooting

| Problem | Fix |
|---|---|
| Teammates get `PERMISSION_DENIED` | They need a role on the team project, and to run `gcloud auth application-default login` with the same account. |
| The trial credit is running low | Delete idle Agent Runtime deployments and data stores first; run evaluations with `--rate`. Talk to your instructor early. |
| The A2A agent can't be discovered | Its agent card must be served at `/.well-known/agent-card.json` on the service URL. |
| The release gate fails on a metric you didn't measure | Measure it, or remove it from the thresholds **with a written reason** in the evaluation report — never by editing the gate. |
