# One-Time Setup

Do this once, before Lab 1. It follows **Appendix A** of the book. Allow about 30 minutes.

You will:
1. install the local tools,
2. sign up for the Google Cloud free trial,
3. create a course project,
4. check that everything works.

---

## 1. Install the local tools

| Tool | Version | Check with |
|---|---|---|
| Python | 3.11 or later | `python3 --version` |
| Git | any recent | `git --version` |
| Google Cloud CLI (`gcloud`) | latest | `gcloud --version` |
| Node.js (only for the MCP Inspector) | 20 or later | `node --version` |

Install the Google Cloud CLI by following Google's instructions for your operating system: https://cloud.google.com/sdk/docs/install

Clone this repository:
```bash
$ git clone <repository-url> designing-agentic-ai-solutions
$ cd designing-agentic-ai-solutions
```

**Checkpoint:** all four checks in the table print a version number.

---

## 2. Sign up for the Google Cloud free trial

The course uses Google Cloud's **free trial**: new customers receive a **$300 credit for 90 days**. If the credit is used up or 90 days pass, the trial account **closes and stops its resources — you are not billed.**

> **When to sign up:** the 90 days start at signup and cannot be paused. In a 14-week course, sign up **at the start of week 2 or 3** so the credit lasts through the capstone. In a 10-week course, sign up in week 1. Until you sign up, do Labs 1–2 with a free Gemini API key from AI Studio (the local route in [section 6](#6-if-you-cannot-use-the-free-trial)); Lab 3 needs no model at all. Switch `setup/course.env` to your project once the trial is active.

1. Go to https://cloud.google.com/free and choose to start for free.
2. Use a **personal Google account** (unless your instructor says your university account works with Google Cloud).
3. Enter a payment method. Google uses it to verify your identity; it is **not charged** during the trial.
4. **Do not upgrade to a paid account.** Upgrading removes the automatic stop at $300 and 90 days.

**Checkpoint:** the Google Cloud console's Billing page shows a Free Trial account with $300 of credit and an end date.

> **Can't use the free trial?** (You used one before, or you don't want to enter a payment method.) See [section 6](#6-if-you-cannot-use-the-free-trial).

---

## 3. Sign in from your computer

```bash
$ gcloud auth login
$ gcloud auth application-default login
```

The first command signs in the `gcloud` CLI. The second creates the credentials that ADK and the Python libraries use. Both open a browser window.

---

## 4. Create the course project

```bash
$ export PROJECT=agentic-course-$RANDOM
$ gcloud projects create $PROJECT
$ gcloud config set project $PROJECT
$ gcloud billing accounts list
```

Copy the **ACCOUNT_ID** of the Free Trial billing account from the last command, then:

```bash
$ gcloud billing projects link $PROJECT --billing-account=XXXXXX-XXXXXX-XXXXXX
$ ./setup/enable_apis.sh
```

`enable_apis.sh` enables the services the labs share (the list is in `setup/apis.txt`). Individual labs enable anything extra in their own `setup.sh`.

Now save your settings for all labs:

```bash
$ cp setup/course.env.example setup/course.env
```

Edit `setup/course.env`:

```bash
GOOGLE_CLOUD_PROJECT=agentic-course-12345     # your project ID
GOOGLE_CLOUD_LOCATION=us-central1             # or the region your instructor gives
GOOGLE_GENAI_USE_VERTEXAI=True                # call Gemini through your project (uses the trial credit)
```

Every lab's `.env.example` reads these values, so you set them only once.

> **Important:** keep `GOOGLE_GENAI_USE_VERTEXAI=True`. The trial credit **does not** pay for the Gemini API used with an AI Studio API key; it does pay for Gemini called through your project.

---

## 5. Check that everything works

```bash
$ cd setup
$ python3 -m venv .venv
$ source .venv/bin/activate      # Windows: .venv\Scripts\activate
$ pip install -r requirements.txt
$ python check_setup.py
```

`check_setup.py` checks your Python version, your credentials, that the project is linked to billing, that the APIs are enabled, and makes one small Gemini call.

**Checkpoint:** every line reads `OK`, and the last line prints a one-sentence reply from Gemini.

### Set a budget alert (recommended)

```bash
$ gcloud billing budgets create --billing-account=XXXXXX-XXXXXX-XXXXXX \
    --display-name="course budget" --budget-amount=100USD \
    --threshold-rule=percent=0.5 --threshold-rule=percent=0.9 \
    --threshold-rule=percent=1.0
```

A budget sends e-mail alerts; it does not stop spending. On the free trial, the $300 cap is the hard stop.

---

## 6. If you cannot use the free trial

**Option A — local route (no cloud account).** Most of each lab — the tool design, tests, evaluation and business parts — runs on your laptop. For model calls:

1. Get a free API key at https://aistudio.google.com.
2. In `setup/course.env` set:
   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=False
   GOOGLE_API_KEY=your-key
   ```
3. Run evaluation scripts with `--rate 5` or lower; free-tier limits are low.

Content sent on the free tier may be used to improve Google's products. That is acceptable for these labs **only because all data here is synthetic**. You will skip the deploy steps and answer them as a written plan; each README says what to submit instead.

**Option B — your own paid account.** Use it as above with `GOOGLE_GENAI_USE_VERTEXAI=True`, set the budget alert, and run every `cleanup.sh`.

---

## Free-trial limits that affect the labs

| Limit | Effect | What to do |
|---|---|---|
| No GPUs | Lab 11's foundation model can't use a GPU | Run it on CPU; the lab is sized for this |
| No quota increases | Default model request rates only | Use `--rate` on evaluation scripts if you see quota (429) errors |
| Google models only | Partner models aren't covered by the credit | Keep `MODEL_NAME` on the pinned Gemini model |
| Not the AI Studio Gemini API | The credit doesn't pay for API-key usage | Keep `GOOGLE_GENAI_USE_VERTEXAI=True` |

---

## Keeping your credit

- Run `./cleanup.sh` at the end of **every** cloud lab, then check the console's resource list.
- Look at the Billing page **once a week**.
- Never upgrade the trial account.
- Agent Runtime deployments, search data stores and databases cost money **while they exist**, even when nobody uses them.

Run `./setup/list_resources.sh` at any time to list everything in your project that can cost money.

---

## Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| `PERMISSION_DENIED` | Wrong identity or project. Run `gcloud auth list` and `gcloud config get project`. Re-run `gcloud auth application-default login`. |
| `API ... has not been used in project ... or it is disabled` | Run `./setup/enable_apis.sh` again, wait two minutes, retry. |
| `Model ... not found` | Check `MODEL_NAME` in the lab's `.env` against `.env.example`, and your region. |
| `429` / `RESOURCE_EXHAUSTED` | You hit a rate quota. Wait a minute and rerun with `--rate 10` (or lower). |
| Billing account not found | The trial isn't active yet, or you signed up with a different Google account than `gcloud auth login`. |
| Works locally, fails after deploy | A missing environment variable or secret, or the service account lacks a permission. The lab's Troubleshooting section lists which. |
