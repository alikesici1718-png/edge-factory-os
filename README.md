# Edge Factory OS: Autonomous Crypto Signal Research Pipeline

## Overview

Edge Factory OS is a self-managing research pipeline for systematic crypto signal discovery across 81 symbols. It autonomously proposes, tests, validates, and promotes (or retires) trading signal candidates across 6 strategy families, with human-approval gates at promotion checkpoints.

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

### State Management
- `edge_factory_os_orchestrator.py` / `_v2.py`: top-level loop coordinating research queue, signal lifecycle, and approval routing
- `edge_factory_autonomous_research_queue.py`: queues new candidate signals; prioritizes by evidence score
- `edge_factory_family_lifecycle_engine.py`: tracks each signal family through stages (research → sandbox → paper → live)
- `edge_factory_os_decision_ledger.py`: append-only audit log of every promotion/retirement decision

### Risk Gates
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

**`tools/` folder**: 892 governance and introspection scripts; see "Tools Directory" section below for a categorized breakdown.

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
├── tools/                  # 892 governance scripts — see Tools Directory section below
└── README.md
```

## Tools Directory (Internal Governance Utilities)

Total: 892 files across 11 functional groups. Files are named `edge_factory_os_[repo_only_]<signal_or_subsystem>_<verb>_v<N>.py`; the `_repo_only_` infix means the script is read-only (no live capital, no API orders).

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

### Old Short Clean Room (55 files)
Isolated reconstruction workbench for the `old_short_gate_aware` strategy family, which lost its original backtest data. Scripts attempt to rebuild evidence from scratch using bounded synthetic fixtures, behavioral validators, and schema-matched dry runs — without touching live runtime. Examples: `*_old_short_clean_room_bounded_behavioral_validation_*`, `*_old_short_clean_room_direct_backtest_*`, `*_old_short_clean_room_threshold_reconstruction_*`.

### Cycle Operators and Self-Improvement Planners (11 files)
Top-level loop orchestration tools that schedule which governance module runs next in the autonomous research cycle. `cycle_operator_v*.py` files (v1–v4) read the scheduler policy and invoke control tower; `self_improvement_planner_v*.py` files propose structural changes to the pipeline itself. Examples: `edge_factory_os_cycle_operator_v1.py`, `edge_factory_os_self_improvement_planner_v4.py`.

### Policy and Guard Enforcement (57 files)
Stateless policy engines that enforce research budget limits, multiple-testing corrections, month-stability requirements, and action prerequisites. Guards block downstream steps if their invariant is violated; policy files define the rules that guards enforce. Examples: `edge_factory_os_global_multiple_testing_ledger_*`, `edge_factory_os_strict_month_stability_policy_guard_*`, `edge_factory_os_action_prerequisite_guard_v1.py`.
