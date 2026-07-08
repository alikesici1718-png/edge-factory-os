# Edge Factory OS

This is not a trading bot repository. This is a research pipeline built to
systematically generate, test, and reject crypto trading hypotheses at scale
— with an emphasis on not fooling myself about whether a signal is real.

## What This Project Accomplished

- 81 symbols tested (Binance/OKX perpetual futures)
- 34 months of historical data (January 2023 – October 2025)
- 33 strategy evaluations executed, each with real out-of-sample performance metrics
- 27 hypotheses formally closed via a hash-verified audit trail
- 27 rejected after cost-adjusted evaluation (all closures denied every permission: no edge claim, no capital, no family release)
- 240 JSON research artifacts generated (full audit trail of every decision)

**Result: no statistically significant, cost-adjusted edge was found in any
of the 7 research hypothesis families tested (grouped by route:
binance_okx_overlap, binance_okx_group2, binance_spot_perp,
crypto_15m_idiosyncratic_sweep_short, crypto_15m_residual_sweep/confluence,
crypto_15m_liquidity_sweep, and one additional 15m momentum family).**

## Research Philosophy

The goal of this project was not to find a profitable strategy. The goal
was to build a system capable of rigorously rejecting weak hypotheses —
with pre-registration (to avoid post-hoc rationalization), cost-inclusive
backtesting (to avoid reporting fantasy returns), and an immutable decision
log (to avoid quietly re-running a test until it looks good).

Most of the value in this repository is not "did it find alpha" — it didn't.
The value is the discipline of the rejection process itself.

## Research Flow

```
Idea
  |
  v
Pre-registration (hypothesis + success criteria locked before testing)
  |
  v
Execution (backtest against historical data)
  |
  v
Evaluation (cost-adjusted performance metrics computed)
  |
  v
Closure (accept / reject decision, hash-linked to source artifacts)
```

## Example Result

The best-performing strategy candidate out of 33 evaluated
("crypto_15m_idiosyncratic_sweep_short_trap_quality_time_exit_only") looked
genuinely promising on the surface:

- Validation net return: +474.5 bps
- Holdout net return: +760.2 bps
- 454 total closed trades (short-only, high-volatility sweep pattern)

But it was still rejected. Why: the pipeline's null-baseline test — checking
whether a result this good could plausibly arise from noise given the number
of candidates tested — placed this result at the 84th percentile of the null
distribution. The threshold for acceptance is the 95th percentile. In other
words, a result this strong is not rare enough, given how many strategies
were tried, to be trusted as a real edge rather than a lucky draw.

This is the core discipline the pipeline enforces: a good-looking backtest
is necessary but not sufficient. All 33 evaluated strategies were ultimately
rejected, several (like this one) despite double- or triple-digit apparent
returns, because they failed the same null-baseline bar.

## Verified vs. Unverified Components

**Verified (executed, produced real output):**
- Signal evaluation pipeline: 33 strategy evaluations executed with real performance metrics
- Closure/rejection workflow: 27 strategies formally closed via `artifacts/strategy_closures/`, hash-verified (SHA-256 chain linking each closure to its source execution and evaluation artifacts)

**Built but not yet exercised:**
- Fully autonomous orchestration (`edge_factory_os_orchestrator.py` / `_v2.py`): code exists and has been imported, but no evidence of a full autonomous run without manual triggering. All executions found in artifacts were triggered directly via `tools/` scripts.
- Live paper trading (8 strategy-specific loggers in `src/`): code exists, imported, but no evidence of any executed paper trade or output file.

## Tooling

The repository contains 839 automation scripts under `tools/`, grouped into:

- Pre-registration contracts
- Research contract builders
- Evaluators
- Runners / executors
- Hypothesis closures
- Historical data acquisition
- Status refresh / backlog management
- Approval and gate records
- Diagnostics, audits, repairs
- Cycle operators / self-improvement
- Policy and guard enforcement

### Pre-registration Contracts (35 files)
Frozen hypothesis specifications written before a backtest is run. Each file records the exact signal definition, entry/exit rules, cost assumptions, and expected direction — so the result cannot be retrofitted after the fact. Examples: `*_preregistration_contract_v1.py`, `*_preregistration_v1.py` (e.g., `crypto_15m_liquidity_sweep_reversal_preregistration_v1.py`, `binance_okx_overlap_funding_crowding_reversal_full_range_preregistration_contract_v1.py`).

### Research Contract Builders (29 files)
Scripts that assemble a standardized research contract JSON artifact by consuming a framework router spec, plugin config, data-quality guard output, and lesson memory. These replaced one-off per-signal contract builders with a generic framework. Examples: `edge_factory_os_generic_research_contract_builder_v1.py`, `edge_factory_os_exit_risk_shape_contract_builder_v1.py`.

### Evaluators (80 files)
Read-only scripts that interpret execution artifacts and produce a structured evaluation JSON — pass/fail verdict, key metrics, null-baseline percentile. Each evaluator has a corresponding `_runner_` and `_closure_` partner in the same signal namespace. Examples: `*_evaluator_v1.py` under `binance_okx_overlap_*`, `crypto_15m_*`, `okx_88_symbol_*`, `lucifer_15m_*`.

### Runners and Executors (177 files)
Scripts that execute a backtest, data pipeline step, or governance workflow and write a result artifact to `artifacts/`. Runners are sequenced by the orchestrator; each has an `_after_<prior_step>` suffix that encodes the required predecessor artifact. Examples: `edge_factory_os_generic_research_runner_v1.py`, `*_execution_v1.py` across all signal families.

### Hypothesis Closures (42 files)
Terminal artifacts for a hypothesis: record whether the signal was accepted (promoted to paper), rejected (retired), or sent back for redesign. Written only after evaluator pass/fail verdict. Examples: `*_closure_v1.py` for every tested signal variant (funding carry, liquidity sweep, residual sweep, OI crowding, etc.).

### Historical Data Acquisition Pipeline (105 files)
Step-by-step OKX / Binance USDT-perpetual data download and panel-build pipeline. Highly granular: each step (preview → approval → execution → validator → summary) is a separate file so any failure can be isolated and resumed. Examples: `*_okx_single_symbol_30_day_download_*`, `*_okx_full_usdt_swap_first_chunk_download_*`, `*_binance_data_vision_um_metrics_*`.

### Status Refresh and Backlog Management (92 files, combined)
Two tightly coupled groups: (a) `*_status_refresh_*` / `*_status_review_*` scripts snapshot the full pipeline state (24 files); (b) `*_development_queue_*` / `*_backlog_refresh_*` / `*_next_action_selector_*` scripts select the highest-priority unblocked work item from the backlog and queue it (68 files). The suffix chain `_after_<prior_step>` on many filenames encodes the exact execution order. Examples: `edge_factory_os_repo_only_standard_os_status_refresh_v1.py`, `edge_factory_os_repo_only_development_queue_selector_v1.py`.

### Approval and Gate Records (60 files)
Human-in-the-loop checkpoints. Each `_approval_` file records a manual approval decision (written to an artifact JSON) that unlocks the next automated step. `_gate_` files enforce that the approval artifact exists and is fresh before proceeding. Examples: `*_approval_gate_v1.py`, `*_manual_approval_record_v1.py`, `*_release_gate_v*.py`.

### Diagnostics, Audits, and Repairs (104 files)
Ad-hoc investigation and fix scripts generated when a step fails or a data anomaly is found. Sub-patterns: `*_diagnostic_*` (inspect an artifact or panel), `*_audit_*` (whole-system checks), `*_repair_*` / `*_patch_*` (apply targeted fixes with preview → approval → apply cycle). Examples: `*_bom_syntax_repair_*`, `*_gate_metadata_patch_*`, `*_impulse_long_row_level_diagnostic_*`.

### Cycle Operators and Self-Improvement Planners (11 files)
Top-level loop orchestration tools that schedule which governance module runs next in the autonomous research cycle. `cycle_operator_v*.py` files (v1–v4) read the scheduler policy and invoke control tower; `self_improvement_planner_v*.py` files propose structural changes to the pipeline itself. Examples: `edge_factory_os_cycle_operator_v1.py`, `edge_factory_os_self_improvement_planner_v4.py`.

### Policy and Guard Enforcement (57 files)
Stateless policy engines that enforce research budget limits, multiple-testing corrections, month-stability requirements, and action prerequisites. Guards block downstream steps if their invariant is violated; policy files define the rules that guards enforce. Examples: `edge_factory_os_global_multiple_testing_ledger_*`, `edge_factory_os_strict_month_stability_policy_guard_*`, `edge_factory_os_action_prerequisite_guard_v1.py`.

## Repository Structure

- `src/` — Core pipeline: orchestrators, governors, validators, live loggers
- `tools/` — Governance and automation utilities (see Tooling above)
- `artifacts/` — Append-only audit trail (contracts, evaluations, closures)
- `edge_factory_os_framework/` — Schema/policy/contract definitions (declarative config layer)
- `scripts/` — System launchers (paper trading, not live capital)
- `docs/` — Detailed documentation and script inventory

## Methodology

- Cost-inclusive backtesting (all reported returns are net of realistic transaction costs)
- Pre-registered hypotheses (success criteria locked before testing)
- Immutable, hash-linked decision audit trail

## Requirements

```
pip install pandas numpy ccxt
```
