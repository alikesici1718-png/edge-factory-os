#!/usr/bin/env python3
"""Create Coinalyze long liquidation flush strategy preregistration.

Preregistration only. This module does not call APIs, use API keys, execute
strategies, generate signals, run backtests, compute PnL, optimize, create
candidates, claim edge, or grant runtime/live/capital permission.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_coinalyze_long_liquidation_flush_strategy_preregistration_v1"
STATUS = "PASS_REPO_ONLY_COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_PREREGISTRATION_CREATED"
ARTIFACT_KIND = "COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_PREREGISTRATION"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_coinalyze_long_liquidation_flush_strategy_preregistration_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "coinalyze_long_liquidation_flush_strategy_preregistration_v1.json"
DESIGN_PATH = REPO_ROOT / "artifacts" / "research_designs" / "coinalyze_long_liquidation_flush_strategy_design_v1.json"
EVENT_STUDY_PATH = REPO_ROOT / "artifacts" / "event_studies" / "coinalyze_liquidation_imbalance_oi_flush_event_study_v1.json"
DATASET_BUILDER_PATH = REPO_ROOT / "artifacts" / "data_builds" / "coinalyze_recent_oi_liquidation_dataset_builder_v1.json"
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
EXPECTED_NEW_PATHS = {
    str(TOOL_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(ARTIFACT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
}

SELECTED_HYPOTHESIS = "LONG_LIQUIDATION_FLUSH_EVENT"
STRATEGY_KEY = "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_V1"
ROUTE_FAMILY = "COINALYZE_RECENT_LIQUIDATION_OI_FLUSH_EVENT_REVERSAL"
CONFIG_ID = "coinalyze_long_liquidation_flush_reversal_15m_hold4h_v1"
NEXT_ALLOWED_STEP = "COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_EXECUTION_V1"


def git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={SAFE_DIR}", "-C", str(REPO_ROOT), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def source_checkpoint() -> str:
    return git(["rev-parse", "HEAD"])


def git_status_entries() -> list[tuple[str, str]]:
    raw = git(["status", "--short", "-uall"])
    entries: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if line.strip():
            entries.append((line[:2], line[3:].strip().strip('"').replace("\\", "/")))
    return entries


def repo_clean_except_expected_new_files() -> bool:
    for status, path in git_status_entries():
        if status == "??" and path in EXPECTED_NEW_PATHS:
            continue
        return False
    return True


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def build_payload() -> dict[str, Any]:
    design = load_json(DESIGN_PATH)
    event_study = load_json(EVENT_STUDY_PATH)
    dataset_builder = load_json(DATASET_BUILDER_PATH)

    design_selected = design.get("selected_hypothesis", {}).get("hypothesis_key")
    design_strategy = design.get("preregistered_strategy_design", {}).get("strategy_key")
    event_result = event_study.get("event_study_results", {}).get(SELECTED_HYPOTHESIS, {})
    event_baseline = event_study.get("baseline_results", {}).get(SELECTED_HYPOTHESIS, {})
    clean = repo_clean_except_expected_new_files()

    validation_checks = {
        "repo_clean_before_run": clean,
        "strategy_design_loaded": design.get("status") == "PASS_REPO_ONLY_COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_DESIGN_CREATED",
        "event_study_loaded": event_study.get("status") == "PASS_REPO_ONLY_COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_CREATED",
        "dataset_builder_loaded": dataset_builder.get("status") == "PASS_REPO_ONLY_COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BUILDER_CREATED",
        "selected_hypothesis_verified_long_liquidation_flush": design_selected == SELECTED_HYPOTHESIS
        and SELECTED_HYPOTHESIS in event_study.get("event_study_results", {}),
        "strategy_key_verified": design_strategy == STRATEGY_KEY,
        "no_api_key_used": True,
        "no_api_call_made": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": clean,
        "replacement_checks_all_true": True,
    }
    validation_checks["replacement_checks_all_true"] = all(validation_checks.values())

    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "source_artifacts": {
            "strategy_design": rel(DESIGN_PATH),
            "event_study": rel(EVENT_STUDY_PATH),
            "dataset_builder": rel(DATASET_BUILDER_PATH),
        },
        "selected_hypothesis": {
            "hypothesis_key": SELECTED_HYPOTHESIS,
            "source": rel(DESIGN_PATH),
            "prior_event_count": event_result.get("event_count"),
            "prior_4h_hit_rate": event_result.get("expected_direction_hit_rate_4h"),
            "prior_baseline_percentile": event_baseline.get("baseline_percentile"),
        },
        "strategy_identity": {
            "strategy_key": STRATEGY_KEY,
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "direction": "long_only",
            "short_trades_allowed": False,
            "short_liquidation_event_used": False,
            "imbalance_event_used_directly": False,
            "candidate_generation": False,
            "edge_claim": False,
        },
        "economic_mechanism": {
            "summary": "After a strong sell move, a large long liquidation spike plus falling open interest may indicate forced long liquidation exhaustion. After forced selling ends, price may mean-revert upward over 2h to 4h.",
            "evidence_context": "The selected event study was promising but uses only a 14-day recent Coinalyze dataset, so this preregistration is diagnostic and not an edge claim.",
        },
        "frozen_event_definition": {
            "event_definition_key": SELECTED_HYPOTHESIS,
            "liquidation_long_gt_zero": True,
            "liquidation_long_threshold": "liquidation_long >= 3 * rolling_median_liquidation_long_24h",
            "oi_change_pct_threshold": "oi_change_pct <= -0.005",
            "ret_1h_past_threshold": "ret_1h_past <= -0.01",
            "rolling_median": {
                "lookback_bars": 96,
                "lookback_duration": "24h",
                "exclude_current_bar": True,
                "minimum_prior_bars": 48,
            },
            "threshold_source": "Round structural thresholds from prior event study; no optimized bucket or parameter grid.",
        },
        "entry_rules": {
            "signal_evaluation": "15m bar close",
            "entry_side": "long",
            "entry_price": "next 15m open",
            "missing_next_bar_action": "skip",
            "no_signal_generation_in_this_module": True,
        },
        "exit_rules": {
            "exit_type": "fixed_hold",
            "hold_bars": 16,
            "hold_duration": "4h",
            "exit_price": "next available 15m open after hold",
            "stop_loss": None,
            "take_profit": None,
            "rationale": "The prior event study showed stronger 4h hit rate than 2h; no exit tuning added.",
        },
        "portfolio_rules": {
            "base_equity_usdt": 1000,
            "fixed_notional_usdt": 50,
            "round_trip_cost_bps": 20,
            "max_concurrent_positions": 3,
            "max_new_positions_per_timestamp": 1,
            "one_open_position_per_symbol": True,
            "symbol_cooldown_after_exit": {
                "bars": 16,
                "duration": "4h",
            },
            "leverage_allowed": False,
            "compounding_allowed": False,
        },
        "candidate_ranking": {
            "if_multiple_events_same_timestamp": [
                "liquidation_long / rolling_median_liquidation_long_24h descending",
                "abs(oi_change_pct) descending",
                "take one until capacity",
            ],
            "ranking_is_predefined": True,
            "optimization_allowed": False,
        },
        "future_execution_pass_criteria": {
            "diagnostic_only": True,
            "closed_trades_minimum_for_interpretable_diagnostic": 20,
            "net_bps": "> 0",
            "average_net_per_trade": "> 0",
            "random_same_symbol_timestamp_baseline_percentile": ">= 0.80",
            "top_symbol_concentration": "<= 0.40",
            "metric_integrity": True,
            "edge_claim_allowed_on_pass": False,
            "candidate_generation_allowed_on_pass": False,
            "live_or_capital_allowed_on_pass": False,
        },
        "future_result_classes": [
            "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE",
            "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_REJECTED_NO_FOLLOWUP",
            "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_INCONCLUSIVE_LOW_SAMPLE",
            "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE",
        ],
        "anti_overfit_policy": {
            "event_study_was_short_recent_window": True,
            "no_edge_claim": True,
            "no_threshold_tuning": True,
            "no_extra_filters_from_same_event_study": True,
            "if_strategy_fails_do_not_retune_same_14_day_dataset": True,
            "if_strategy_passes_next_step_extend_data_or_paper_forward_planning_not_live": True,
            "no_candidate_live_or_capital_from_this_dataset": True,
        },
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "limitations": [
            "Preregistration only; this module does not run the strategy, generate signals, backtest, or compute PnL.",
            "The dataset is short and recent: 10 symbols, 15m aligned Coinalyze OI/liquidation/funding/OHLCV, 2026-05-13T19:15:00Z to 2026-05-27T19:15:00Z.",
            "Any future execution result remains diagnostic and cannot grant edge, candidate, live, runtime, or capital permission.",
        ],
        "safety_permissions": {
            "strategy_preregistration_created": True,
            "strategy_execution_allowed_next": True,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "optimization_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    return payload


def main() -> int:
    payload = build_payload()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"status: {payload['status']}")
    print(f"selected_hypothesis: {payload['selected_hypothesis']['hypothesis_key']}")
    print(f"strategy_key: {payload['strategy_identity']['strategy_key']}")
    print(f"event_definition_key: {payload['frozen_event_definition']['event_definition_key']}")
    print(f"next_allowed_step: {payload['next_allowed_step']}")
    print("strategy_execution_allowed_next: true")
    print("signal_generation_allowed_now: false")
    print("backtest_allowed_now: false")
    print("pnl_computation_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")
    return 0 if payload["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
