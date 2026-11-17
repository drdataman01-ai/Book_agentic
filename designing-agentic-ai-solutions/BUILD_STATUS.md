# Repository build status

Each lab README is the specification for its folder. This file lists, per lab, the files the README's folder tree names, and whether each exists yet. Regenerate it with `python tools/build_status.py`.

Legend: ✅ present · ⬜ still to build

**46 of 212 listed items exist.** `vendor/` folders are filled by each lab's `setup.sh` from Google's `adk-samples` at the pinned commit.


## ch01

- ✅ `README.md`
- ✅ `.env.example`
- ✅ `requirements.txt`
- ✅ `quote_desk/`
- ✅ `quote_desk/__init__.py`
- ✅ `quote_desk/agent.py`
- ✅ `pricing_server/`
- ✅ `pricing_server/server.py`
- ✅ `pricing_server/data/items.csv`
- ✅ `tests/`
- ✅ `tests/test_pricing_server.py`
- ✅ `cleanup.sh`
- ✅ `NOTES_TEMPLATE.md`

## ch02

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `data/`
- ⬜ `data/returns_200.jsonl`
- ⬜ `data/warranty_table.csv`
- ⬜ `stubs/`
- ⬜ `stubs/erp_server.py`
- ⬜ `stubs/shipping_server.py`
- ⬜ `router/`
- ⬜ `run_router.py`
- ⬜ `safe_zone.py`
- ⬜ `tests/test_safe_zone.py`
- ⬜ `simulate.py`
- ⬜ `sweep_threshold.py`
- ✅ `tradeoff.py`
- ⬜ `results/`

## ch03

- ✅ `README.md`
- ⬜ `requirements.txt`
- ⬜ `data/`
- ⬜ `data/returns_12m.csv`
- ⬜ `data/audit_sample.csv`
- ⬜ `baseline.ipynb`
- ✅ `value_case.py`
- ✅ `templates/`
- ✅ `templates/go_no_go.md`
- ✅ `templates/memo.md`

## ch04

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `setup.sh`
- ⬜ `cleanup.sh`
- ⬜ `vendor/rag-agent-search/`
- ⬜ `terraform/`
- ⬜ `data/`
- ⬜ `data/policies/`
- ⬜ `data/manifest_d1.jsonl`
- ⬜ `data/manifest_d2.jsonl`
- ⬜ `data/eval_240.jsonl`
- ⬜ `data/profiles.jsonl`
- ⬜ `data/policy_update/`
- ⬜ `app/`
- ⬜ `app/agent.py`
- ⬜ `app/tools.py`
- ⬜ `tests/test_tools.py`
- ⬜ `run_eval.py`
- ✅ `rag_metrics.py`
- ⬜ `freshness_test.py`

## ch05

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `vendor/customer-service/`
- ⬜ `data/orders_500.jsonl`
- ⬜ `token_issuer.py`
- ✅ `returns_server.py`
- ⬜ `tests/test_returns_server.py`
- ⬜ `returns_agent.py`
- ⬜ `adversarial/`
- ⬜ `run_adversarial.py`
- ✅ `unit_economics.py`
- ⬜ `Dockerfile`
- ⬜ `deploy_server.sh`
- ⬜ `cleanup.sh`

## ch06

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `vendor/ambient-expense-agent/`
- ⬜ `terraform/`
- ⬜ `data/`
- ⬜ `data/erp/`
- ⬜ `data/invoices_9500.jsonl`
- ⬜ `data/test_expenses.jsonl`
- ✅ `invoice_flow/`
- ⬜ `invoice_flow/controls.py`
- ✅ `invoice_flow/decision.py`
- ⬜ `invoice_flow/workflow.py`
- ⬜ `tests/test_controls.py`
- ⬜ `publish_invoices.py`
- ✅ `review_policy.py`
- ⬜ `control_attacks.py`
- ⬜ `cleanup.sh`

## ch07

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `vendor/software-bug-assistant/`
- ⬜ `telemetry_server/`
- ⬜ `telemetry_server/server.py`
- ⬜ `telemetry_server/incidents/`
- ⬜ `triage_agent/`
- ⬜ `triage_agent/agent.py`
- ⬜ `triage_agent/brief.py`
- ✅ `catalog.py`
- ⬜ `replay.py`
- ⬜ `abuse/`
- ⬜ `dashboard/dashboard.json`
- ⬜ `cleanup.sh`

## ch08

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `data/`
- ⬜ `data/transactions_18m.parquet`
- ⬜ `data/labels.parquet`
- ⬜ `train.py`
- ⬜ `scoring_server/`
- ⬜ `scoring_server/server.py`
- ⬜ `case_agent/`
- ⬜ `case_agent/agent.py`
- ✅ `faithfulness.py`
- ⬜ `run_summaries.py`
- ✅ `fraud_policy.py`
- ⬜ `label_delay.py`
- ⬜ `tests/`
- ⬜ `deploy_server.sh`
- ⬜ `cleanup.sh`
- ⬜ `templates/validation_report.md`

## ch09

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `setup.sh`
- ⬜ `cleanup.sh`
- ⬜ `reservation_server/`
- ⬜ `reservation_server/server.py`
- ✅ `case.py`
- ⬜ `case_store.py`
- ✅ `eu261.py`
- ⬜ `agents/`
- ⬜ `agents/intake.py`
- ⬜ `agents/rebooking.py`
- ⬜ `agents/care.py`
- ⬜ `replay.py`
- ⬜ `data/storm_500.jsonl`
- ✅ `surge.py`
- ⬜ `tests/`

## ch10

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `vendors/`
- ⬜ `vendors/identity_mock.py`
- ⬜ `vendors/sanctions_mock.py`
- ⬜ `data/applications_300/`
- ⬜ `doc_agent/`
- ⬜ `doc_agent/agent.py`
- ⬜ `doc_agent/schema.py`
- ⬜ `reconcile.py`
- ⬜ `routing.py`
- ✅ `audit_log.py`
- ⬜ `run_onboarding.py`
- ⬜ `evidence.py`
- ⬜ `deploy.sh`
- ⬜ `cleanup.sh`
- ⬜ `tests/`

## ch11

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `data/`
- ⬜ `data/sales_2y.parquet`
- ⬜ `data/calendar.parquet`
- ⬜ `data/products.csv`
- ⬜ `backtest.py`
- ⬜ `models/`
- ⬜ `models/baselines.py`
- ⬜ `models/tsfm.py`
- ⬜ `decide.py`
- ⬜ `forecast_server/`
- ⬜ `forecast_server/server.py`
- ✅ `replenish.py`
- ⬜ `measure_throughput.py`
- ⬜ `job/`
- ⬜ `tests/`

## ch12

- ✅ `README.md`
- ⬜ `.env.example`
- ⬜ `requirements.txt`
- ⬜ `data/deals/`
- ⬜ `calc_server/`
- ⬜ `calc_server/server.py`
- ⬜ `calc_server/Dockerfile`
- ⬜ `memo_workflow/`
- ⬜ `memo_workflow/agent.py`
- ⬜ `memo_workflow/checklist.yaml`
- ⬜ `guardrails/`
- ⬜ `guardrails/numbers_trace.py`
- ⬜ `guardrails/citations.py`
- ⬜ `run_drafts.py`
- ⬜ `usage_report.py`
- ✅ `tco.py`
- ⬜ `deploy.sh`
- ⬜ `cleanup.sh`
- ⬜ `tests/`

## ch13

- ✅ `README.md`
- ⬜ `templates/`
- ⬜ `starter/`
- ⬜ `starter/mcp_server/`
- ⬜ `starter/workflow_agent/`
- ⬜ `starter/a2a_agent/`
- ⬜ `starter/eval/`
- ⬜ `starter/deploy.sh`
- ⬜ `starter/cleanup.sh`
- ✅ `release_gate.py`
- ⬜ `examples/harbor_order_desk/`
