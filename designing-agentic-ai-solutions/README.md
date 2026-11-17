# Designing Agentic AI Solutions — Companion Repository

Labs, code and data for **Designing Agentic AI Solutions: Ten Business Cases with RAG, Agents, and MCP — from Whiteboard to Production** by Chris Kuo (Innovation Press).

Every chapter has a lab. Each lab lives in its own folder (`ch01/` … `ch13/`) and starts with a `README.md` that walks you through it step by step. **Always read the lab's README first, then follow it in order.**

---

## Start here

1. **Set up once** — follow [`setup/README.md`](setup/README.md). It covers installing the tools, signing up for the Google Cloud free trial, and creating your course project. Allow about 30 minutes.
2. **Open a lab folder** — for example `ch01/` — and read its `README.md`.
3. **Run the lab** — each step has a command to run and a *Checkpoint* telling you what you should see before moving on.
4. **Hand in** — the *Deliverable* section of each README lists exactly what to submit.
5. **Clean up** — every cloud lab ends with `./cleanup.sh`. Run it. Resources left running are what use up your free-trial credit.

---

## The labs

| Lab | Chapter | Title | Cloud needed? | Time |
|---|---|---|---|---|
| [1](ch01/README.md) | From Building Agents to Designing Solutions | A First Quote Assistant | Gemini only | 1 h |
| [2](ch02/README.md) | The Designer's Toolkit | Measuring Two Designs | Gemini only | 1.5 h |
| [3](ch03/README.md) | The Business of AI Solutions | A Value Case You Can Defend | None | 1.5 h |
| [4](ch04/README.md) | Case: A Company Policy Assistant | Deploy and Measure the Policy Assistant | Yes | 3 h |
| [5](ch05/README.md) | Case: Customer Support Triage | Tools You Can Trust | Yes | 3 h |
| [6](ch06/README.md) | Case: Invoice to Payment | A Checkpoint That Holds | Yes | 3 h |
| [7](ch07/README.md) | Case: IT Incident Response | An Agent You Can Watch | Yes | 2.5 h |
| [8](ch08/README.md) | Case: Credit Card Fraud Review | Evaluating What Matters | Yes | 3 h |
| [9](ch09/README.md) | Case: Airline Disruption Rebooking | Surviving the Storm | Yes | 3 h |
| [10](ch10/README.md) | Case: KYC and AML Onboarding | Controls You Can Show an Examiner | Yes | 2.5 h |
| [11](ch11/README.md) | Case: Demand Forecasting and Replenishment | Beat the Baseline | Optional (CPU) | 3 h |
| [12](ch12/README.md) | Case: Commercial Loan Underwriting Memo | Decide Where It Runs | Yes | 3 h |
| [13](ch13/README.md) | Capstone: Cross-Department Operations | Capstone Project | Yes | Several weeks |

*"Gemini only"* means the lab runs on your computer and calls Gemini models through your course project; nothing is deployed. Lab 11 runs on your computer; deploying its batch as a Cloud Run job is optional.

---

## Two tracks

- **Build track** — do every step.
- **Design track** (no programming) — do the steps marked **[Design]** in each README, and read the outputs your instructor provides for the steps marked **[Build]**. Each README says what design-track students hand in.

---

## Conventions used in every lab

| Convention | Meaning |
|---|---|
| `$` at the start of a line | A command to type in a terminal, from the lab folder unless stated otherwise |
| `.venv` | Each lab has its own virtual environment. Activate it (`source .venv/bin/activate`, or `.venv\Scripts\activate` on Windows) every time you open a new terminal |
| **Checkpoint** | What you should see before you continue. If you don't see it, check the lab's *Troubleshooting* section |
| `.env.example` → `.env` | Each lab's settings. Copy it to `.env` and fill it in. **Never commit `.env`** |
| `MODEL_NAME` | Pinned in `.env.example`. Don't change it unless the lab asks you to |
| `--rate N` | Option on every evaluation script: at most *N* model requests per minute. Use it if you hit quota errors on the free trial |
| `./setup.sh` / `./cleanup.sh` | Create and delete the lab's cloud resources |
| `vendor/` | A Google ADK sample copied at a pinned commit, under its Apache 2.0 license. Don't edit it; the lab tells you what to copy out of it |

---

## Folder layout

```
designing-agentic-ai-solutions/
├── README.md              ← you are here
├── setup/                 ← one-time setup (tools, free trial, project)
├── templates/             ← solution graph, node card, trade-off table, decision record, memo
├── common/                ← shared helpers used by several labs (rate limiter, eval records)
├── ch01/ … ch13/          ← one folder per lab
│   ├── README.md          ← read first
│   ├── .env.example
│   ├── requirements.txt   ← pinned dependencies
│   ├── data/              ← synthetic data (all labs use synthetic data only)
│   ├── tests/
│   ├── setup.sh, cleanup.sh   (cloud labs)
│   └── ...                ← lab code; files you complete are marked TODO
├── tools/build_status.py  ← for maintainers: which files each README expects
└── BUILD_STATUS.md
```

---

## Data

**All data in this repository is synthetic.** It was generated to resemble the companies in the book's cases and contains no real people, customers or transactions. Do not substitute real company or personal data — particularly if you use the Gemini API free tier, whose inputs may be used to improve Google's products.

## Versions

Agent frameworks, models and cloud services change often. Each lab pins the versions it was tested with in its `requirements.txt` and `.env.example`, and its README records the date it was last tested. If something has changed since, check the repository's issues page before changing pinned versions.

## Getting help

- Each README ends with a *Troubleshooting* section for that lab.
- [`setup/README.md`](setup/README.md) covers account, permission and model-name problems.
- Report errors in a lab by opening an issue with the lab number, the step, the command and the full error message.
