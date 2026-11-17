# Lab 9: Surviving the Storm

**Chapter 9 — Case: Airline Disruption Rebooking** · Time: about 3 hours · Cloud: **yes** (Firestore for the case store; Agent Runtime in Step 6)

## Goal

Build design D2's three agents with the case store and the handoff contract, and run a scaled-down storm replay.

## What you will learn

- How to keep state in a case record that outlives any one conversation (Section 9.5).
- How to hand a case from one agent to another — and to a person — without losing it.
- How a system degrades when a system of record slows down (Section 9.7).

## Before you start

- Setup is done. Estimated credit used: **about $4–8**. Firestore at this volume is within its free allowance; most of the cost is model calls for 500 passengers.
- You have read Sections 9.3–9.7.

## What's in this folder

```
ch09/
├── README.md
├── .env.example
├── requirements.txt
├── setup.sh / cleanup.sh
├── reservation_server/
│   └── server.py           ← simulated reservations: search, hold_seats, reissue (rate-limited)
├── case.py                 ← DisruptionCase model and hand_off (from the chapter)
├── case_store.py           ← Firestore-backed store (or local SQLite with --local)
├── eu261.py                ← compensation rule as code
├── agents/
│   ├── intake.py           ← TODO
│   ├── rebooking.py        ← TODO
│   └── care.py             ← TODO
├── replay.py
├── data/storm_500.jsonl    ← 500 synthetic passengers on cancelled flights
├── surge.py                ← the chapter's staffing model
└── tests/
```

---

## Steps

### Step 1 — Start the reservation server and the case store [Build]

```bash
$ cd ch09
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
$ ./setup.sh                       # creates a Firestore database in Native mode
$ python reservation_server/server.py --port 8090 --rate-limit 20
```

`--rate-limit 20` allows 20 requests per second, like a busy reservation system during a storm. Leave it running.

> No cloud? Run `python case_store.py --local` to use SQLite instead of Firestore.

**Checkpoint:** `pytest tests/test_case.py -q` passes, and the server's `/health` endpoint at http://localhost:8090/health returns `ok`.

### Step 2 — Build the three agents [Build]

Each agent gets **only its own tools**:

| Agent | Tools | Hands off to |
|---|---|---|
| `intake` | read the case, read the passenger's booking | rebooking, care, or a person |
| `rebooking` | search flights, `hold_seats`, `reissue` | care, or a person |
| `care` | `eu261.py` compensation, vouchers, hotel | done, or a person |

Implement every handoff with `hand_off(case, to_stage, to_owner, note)` from `case.py`. It writes the stage change to the case store before the next agent starts.

Rules you must enforce in code:
- `reissue` is refused unless the case has an **unexpired hold** from `hold_seats`.
- Compensation comes only from `eu261.py`; the care agent explains it but never computes it.
- Any passenger flagged for **special assistance** is handed to a person.

```bash
$ pytest tests/ -q
$ adk web        # try one passenger: choose intake
```

**Checkpoint:** one test passenger goes intake → rebooking → care, and the case store shows three stage changes with notes.

### Step 3 — Run the storm replay [Build]

```bash
$ python replay.py --passengers data/storm_500.jsonl --rate 60
```

Each synthetic passenger accepts the first offer, asks for something else, or asks for a person, according to their profile. The replay takes 30–45 minutes.

**Checkpoint:** the script prints the metrics from the chapter's Table 9.4:

| Metric | Threshold |
|---|---|
| Passengers self-served | ≥ 65% |
| Median time to confirmed itinerary, self-served | ≤ 30 min |
| Special-assistance cases handed to a person (recall) | 100% |
| Reissue with an expired or missing hold | 0 |
| Compensation differing from the rule | 0 |
| Statements contradicting the rule (sampled) | ≤ 1% |
| Another passenger's data in a response | 0 |
| Case reopened with the same request | ≤ 5% |

### Step 4 — Halve the rate limit mid-run [Build] [Design]

```bash
$ python replay.py --passengers data/storm_500.jsonl --rate 60 --throttle-at 250 --throttle-to 10
```

At passenger 250, the reservation server's limit drops from 20 to 10 requests per second.

**Checkpoint:** compare the metrics with Step 3. Describe how the system degraded: Did holds expire? Did cases queue for people? Did any reissue happen without a hold? Was any passenger lost (no case update for over an hour)?

### Step 5 — Trace one passenger [Build] [Design]

```bash
$ python replay.py --show-case <case-id>
```

Pick a passenger whose case went through all three agents **and** a person. Save the case history.

### Step 6 — Deploy the agents to Agent Runtime [Build]

```bash
$ ./deploy_agents.sh
```

The script deploys the three agents with `adk deploy agent_engine`, each configured with the case store and the reservation server's URL (the script also deploys the simulator to Cloud Run). Run a small replay against the deployed agents:

```bash
$ python replay.py --passengers data/storm_500.jsonl --limit 50 --target cloud
```

**Checkpoint:** the 50-passenger metrics are in line with Step 3. Note the latency difference from your local run.

### Step 7 — Clean up

```bash
$ ./cleanup.sh
```

This deletes the Agent Runtime deployments, the simulator service and the Firestore database. **Agent Runtime deployments cost money while they exist** — check the console's Agent Runtime page afterwards. Stop the reservation server with Ctrl+C.

---

## Deliverable

1. The metrics table from Steps 3 and 4.
2. The trace of one passenger's case through all three agents and a person.
3. One paragraph: **where is the design weakest?**

**Design track:** your instructor provides replay results. Do Steps 4 (description) and 5, and the deliverable. Use `surge.py` to estimate how many people would be needed if self-service fell to 50%.

## Troubleshooting

| Problem | Fix |
|---|---|
| Firestore errors on setup | Firestore needs a location; set `FIRESTORE_LOCATION` in `.env` (for example `nam5`). |
| Many reissues refused | Holds expire after 10 minutes in the simulator; check the rebooking agent reissues soon after holding. |
| Replay stops with `429` | Lower `--rate`. The script resumes from the last completed passenger. |
| A passenger is handled by two agents at once | `hand_off` must update the stage and owner in one transaction. |
