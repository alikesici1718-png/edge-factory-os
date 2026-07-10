# Tools Directory — Script Inventory

Total: 839 files across 11 functional groups. Files are named
`edge_factory_os_[repo_only_]<signal_or_subsystem>_<verb>_v<N>.py`; the
`_repo_only_` infix means the script is read-only (no live capital, no API orders).

## Pre-registration Contracts (35 files)

Frozen hypothesis specifications written before a backtest is run. Each file
records the exact signal definition, entry/exit rules, cost assumptions, and
expected direction — so the result cannot be retrofitted after the fact.
Examples: `*_preregistration_contract_v1.py`, `*_preregistration_v1.py`
(e.g., `crypto_15m_liquidity_sweep_reversal_preregistration_v1.py`,
`binance_okx_overlap_funding_crowding_reversal_full_range_preregistration_contract_v1.py`).

## Research Contract Builders (29 files)

Scripts that assemble a standardized research contract JSON artifact by
consuming a framework router spec, plugin config, data-quality guard output,
and lesson memory. These replaced one-off per-signal contract builders with a
generic framework. Examples: `edge_factory_os_generic_research_contract_builder_v1.py`,
`edge_factory_os_exit_risk_shape_contract_builder_v1.py`.

## Evaluators (80 files)

Read-only scripts that interpret execution artifacts and produce a structured
evaluation JSON — pass/fail verdict, key metrics, null-baseline percentile.
Each evaluator has a corresponding `_runner_` and `_closure_` partner in the
same signal namespace. Examples: `*_evaluator_v1.py` under
`binance_okx_overlap_*`, `crypto_15m_*`, `okx_88_symbol_*`, `ema9_pivot_15m_*`.

## Runners and Executors (177 files)

Scripts that execute a backtest, data pipeline step, or governance workflow
and write a result artifact to `artifacts/`. Runners are sequenced by the
orchestrator; each has an `_after_<prior_step>` suffix that encodes the
required predecessor artifact. Examples:
`edge_factory_os_generic_research_runner_v1.py`,
`*_execution_v1.py` across all signal families.

## Hypothesis Closures (42 files)

Terminal artifacts for a hypothesis: record whether the signal was accepted
(promoted to paper), rejected (retired), or sent back for redesign. Written
only after evaluator pass/fail verdict. Examples: `*_closure_v1.py` for every
tested signal variant (funding carry, liquidity sweep, residual sweep, OI
crowding, etc.).

## Historical Data Acquisition Pipeline (105 files)

Step-by-step OKX / Binance USDT-perpetual data download and panel-build
pipeline. Highly granular: each step (preview → approval → execution →
validator → summary) is a separate file so any failure can be isolated and
resumed. Examples: `*_okx_single_symbol_30_day_download_*`,
`*_okx_full_usdt_swap_first_chunk_download_*`,
`*_binance_data_vision_um_metrics_*`.

## Status Refresh and Backlog Management (92 files, combined)

Two tightly coupled groups: (a) `*_status_refresh_*` / `*_status_review_*`
scripts snapshot the full pipeline state (24 files); (b)
`*_development_queue_*` / `*_backlog_refresh_*` /
`*_next_action_selector_*` scripts select the highest-priority unblocked
work item from the backlog and queue it (68 files). The suffix chain
`_after_<prior_step>` on many filenames encodes the exact execution order.
Examples: `edge_factory_os_repo_only_standard_os_status_refresh_v1.py`,
`edge_factory_os_repo_only_development_queue_selector_v1.py`.

## Approval and Gate Records (60 files)

Human-in-the-loop checkpoints. Each `_approval_` file records a manual
approval decision (written to an artifact JSON) that unlocks the next
automated step. `_gate_` files enforce that the approval artifact exists and
is fresh before proceeding. Examples: `*_approval_gate_v1.py`,
`*_manual_approval_record_v1.py`, `*_release_gate_v*.py`.

## Diagnostics, Audits, and Repairs (104 files)

Ad-hoc investigation and fix scripts generated when a step fails or a data
anomaly is found. Sub-patterns: `*_diagnostic_*` (inspect an artifact or
panel), `*_audit_*` (whole-system checks), `*_repair_*` / `*_patch_*` (apply
targeted fixes with preview → approval → apply cycle). Examples:
`*_bom_syntax_repair_*`, `*_gate_metadata_patch_*`,
`*_impulse_long_row_level_diagnostic_*`.

## Cycle Operators and Self-Improvement Planners (11 files)

Top-level loop orchestration tools that schedule which governance module runs
next in the autonomous research cycle. `cycle_operator_v*.py` files (v1–v4)
read the scheduler policy and invoke control tower;
`self_improvement_planner_v*.py` files propose structural changes to the
pipeline itself. Examples: `edge_factory_os_cycle_operator_v1.py`,
`edge_factory_os_self_improvement_planner_v4.py`.

## Policy and Guard Enforcement (57 files)

Stateless policy engines that enforce research budget limits,
multiple-testing corrections, month-stability requirements, and action
prerequisites. Guards block downstream steps if their invariant is violated;
policy files define the rules that guards enforce. Examples:
`edge_factory_os_global_multiple_testing_ledger_*`,
`edge_factory_os_strict_month_stability_policy_guard_*`,
`edge_factory_os_action_prerequisite_guard_v1.py`.
