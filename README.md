# Edge Factory OS: Autonomous Crypto Signal Research Pipeline

## Overview

Edge Factory OS is a research and evaluation pipeline for systematic crypto signal discovery across 81 symbols. The signal evaluation and closure workflow (preregistration -> execution -> evaluation -> closure) has been run end-to-end and produced verified results across 33 strategy evaluations and 27 formal closures. A fully autonomous orchestration layer (automatic triggering without manual execution) was also built but has not yet been exercised end-to-end.

**Strategy families (one live paper logger per family):**
1. Impulse Event Long (`impulse_event_long_live_paper_logger.py`)
2. Impulse Long Gate-Aware (`impulse_long_gate_aware_live_paper_logger.py`)
3. OKX Event Impulse (`okx_event_impulse_live_paper_logger.py`)
4. Session Ret60 Reversal (`session_ret60_reversal_live_paper_logger.py`)
5. Market Relative (`market_relative_live_paper_logger.py`)
6. Session Short Gate-Aware (`session_short_gate_aware_live_paper_logger.py`)
7. Old Short Gate-Aware (`old_short_gate_aware_live_paper_logger.py`)
8. Weak Market Breakdown Short (`weak_market_breakdown_short_live_paper_logger.py`)

The pipeline manages its own research queue, tracks signal lifecycle state (candidate → sandbox paper → promotion review → retired), and enforces risk gates before any capital allocation.

## Architecture

### State Management *(not yet exercised — see Verified vs. Unverified section)*
- `edge_factory_os_orchestrator.py` / `_v2.py`: top-level loop coordinating research queue, signal lifecycle, and approval routing
- `edge_factory_autonomous_research_queue.py`: queues new candidate signals; prioritizes by evidence score
- `edge_factory_family_lifecycle_engine.py`: tracks each signal family through stages (research → sandbox → paper → live)
- `edge_factory_os_decision_ledger.py`: append-only audit log of every promotion/retirement decision

### Risk Gates *(not yet exercised — see Verified vs. Unverified section)*
- `edge_factory_capital_governor.py` / `adaptive_capital_governor_v2.py`: enforces per-signal and global capital limits
- `edge_factory_kill_switch_controller.py`: halts live allocation on drawdown breach
- `global_paper_risk_manager.py` (v1–v4): cross-signal paper portfolio risk; prevents correlated over-allocation
- `edge_factory_os_drift_gate_controller.py`: blocks promotion if live vs. backtest drift exceeds threshold

### Validator Chain
Before any signal advances, it must pass a sequential validator chain:
1. `edge_factory_coin_subset_validator.py`: confirms symbol universe is valid and liquid
2. `edge_factory_execution_realism_checker.py`: checks slippage and fill assumptions
3. `edge_factory_rolling_oos_validator.py` / `_v2.py`: rolling out-of-sample pass required
4. `edge_factory_research_candidate_validator.py`: final evidence synthesis gate
5. `edge_factory_native_bps_validator.py`: net-of-cost profitability check in bps

**`tools/` folder**: 837 governance and introspection scripts; see "Tools Directory" section below for a categorized breakdown.

## Verified vs. Unverified Components

**Verified (executed, produced real output):**
- Signal evaluation pipeline: 33 strategy evaluations executed with real performance metrics. Example candidate: 17,716 signals tested across 34 months (Jan 2023 - Oct 2025), net -19.13 bps after costs, 33.6% win rate.
- Closure/rejection workflow: 27 strategies formally closed via `artifacts/strategy_closures/`, all hash-verified (SHA-256 chain linking each closure to its source execution and evaluation artifacts). All 27 closed as rejected after cost-adjusted evaluation.
- Evidence: `artifacts/strategy_evaluations/` (33 files), `artifacts/strategy_closures/` (27 files)

**Built but not yet exercised:**
- Fully autonomous orchestration (`edge_factory_os_orchestrator.py` / `_v2.py`): code exists and has been imported, but no evidence of a full autonomous run (research queue -> auto-execution -> auto-promotion without manual triggering). All 35 executions found in artifacts were triggered directly via `tools/` scripts, not via the orchestrator.
- Live paper trading (8 strategy-specific loggers in `src/`): code exists, imported, but no evidence of any executed paper trade or output file.

This distinction matters: the research and evaluation methodology is real and produced real (negative) findings. The autonomous orchestration and live-trading layers are unexercised infrastructure, built preemptively in case a signal had passed validation.

## Key Findings

- **`institutional_size_classification_pilot.py`**: tested whether large-lot order flow predicts short-term direction; result: no statistically significant edge after BH-FDR correction across the 81-symbol universe
- **General outcome**: the autonomous pipeline has not surfaced a promotable signal as of the current state; the majority of candidates exited at the rolling OOS validator or the native bps validator gate
- The pipeline infrastructure itself (state management, validator chain, approval gates) is production-grade; the absence of edge is a research finding, not a system failure

## Repository Structure

```
edge_factory_os_repo/
├── src/                    # Core pipeline: orchestrators, governors, validators, live loggers
│   ├── edge_factory_os_orchestrator*.py       # Top-level control loop
│   ├── edge_factory_*_governor*.py            # Capital and risk governors
│   ├── edge_factory_*_validator*.py           # Validator chain components
│   ├── edge_factory_os_decision_ledger.py     # Immutable audit log
│   ├── *_live_paper_logger.py                 # Per-strategy paper trading loggers
│   └── global_paper_risk_manager*.py          # Cross-signal risk manager
├── tools/                  # 837 governance scripts — see Tools Directory section below
└── README.md
```

## Tools Directory (Internal Governance Utilities)

Total: 837 files across 10 functional groups. Files are named `edge_factory_os_[repo_only_]<signal_or_subsystem>_<verb>_v<N>.py`; the `_repo_only_` infix means the script is read-only (no live capital, no API orders).

### Pre-registration Contracts (35 files)
Frozen hypothesis specifications written before a backtest is run. Each file records the exact signal definition, entry/exit rules, cost assumptions, and expected direction — so the result cannot be retrofitted after the fact. Examples: `*_preregistration_contract_v1.py`, `*_preregistration_v1.py` (e.g., `crypto_15m_liquidity_sweep_reversal_preregistration_v1.py`, `binance_okx_overlap_funding_crowding_reversal_full_range_preregistration_contract_v1.py`).

### Research Contract Builders (29 files)
Scripts that assemble a standardized research contract JSON artifact by consuming a framework router spec, plugin config, data-quality guard output, and lesson memory. These replaced one-off per-signal contract builders with a generic framework. Examples: `edge_factory_os_generic_research_contract_builder_v1.py`, `edge_factory_os_exit_risk_shape_contract_builder_v1.py`.

### Evaluators (80 files)
Read-only scripts that interpret execution artifacts and produce a structured evaluation JSON — pass/fail verdict, key metrics, BH-corrected p-values. Each evaluator has a corresponding `_runner_` and `_closure_` partner in the same signal namespace. Examples: `*_evaluator_v1.py` under `binance_okx_overlap_*`, `crypto_15m_*`, `okx_88_symbol_*`, `lucifer_15m_*`.

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
