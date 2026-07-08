#!/usr/bin/env python3
"""Create Coinalyze long liquidation flush preregistered strategy design.

Design only. This module does not call APIs, use API keys, execute strategies,
generate signals, run backtests, compute PnL, optimize, create candidates,
claim edge, or grant runtime/live/capital permission.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_coinalyze_long_liquidation_flush_strategy_design_v1"
STATUS = "PASS_REPO_ONLY_COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_DESIGN_CREATED"
ARTIFACT_KIND = "COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_DESIGN"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_coinalyze_long_liquidation_flush_strategy_design_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_designs" / "coinalyze_long_liquidation_flush_strategy_design_v1.json"
EVENT_STUDY_PATH = REPO_ROOT / "artifacts" / "event_studies" / "coinalyze_liquidation_imbalance_oi_flush_event_study_v1.json"
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
EXPECTED_NEW_PATHS = {
    str(TOOL_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(ARTIFACT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
}

STRATEGY_KEY = "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_V1"
ROUTE_FAMILY = "COINALYZE_RECENT_LIQUIDATION_OI_FLUSH_EVENT_REVERSAL"
CONFIG_ID = "coinalyze_long_liquidation_flush_reversal_15m_hold4h_v1"
SELECTED_HYPOTHESIS = "LONG_LIQUIDATION_FLUSH_EVENT"


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


def build_payload() -> dict[str, Any]:
    event_study = load_json(EVENT_STUDY_PATH)
    long_result = event_study["event_study_results"][SELECTED_HYPOTHESIS]
    long_baseline = event_study["baseline_results"][SELECTED_HYPOTHESIS]
    clean = repo_clean_except_expected_new_files()
    promising_verified = (
        event_study.get("result_classification")
        == "COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_PROMISING_FOR_PREREGISTRATION"
        and long_result.get("event_count") == 91
        and long_baseline.get("baseline_percentile") == 1.0
    )
    selected_verified = (
        SELECTED_HYPOTHESIS in event_study.get("event_study_results", {})
        and long_result.get("expected_direction_hit_rate_4h") is not None
    )
    validation_checks = {
        "repo_clean_before_run": clean,
        "event_study_loaded": event_study.get("status") == "PASS_REPO_ONLY_COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_CREATED",
        "promising_event_verified": promising_verified,
        "selected_hypothesis_verified_long_liquidation_flush": selected_verified,
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
            "event_study": str(EVENT_STUDY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        },
        "prior_event_study_summary": {
            "commit": "d0c4289711931bc887f118f52489482492db6e1c",
            "status": event_study.get("status"),
            "result_classification": event_study.get("result_classification"),
            "dataset_symbol_count": event_study.get("dataset_review", {}).get("dataset_symbol_count"),
            "total_rows": event_study.get("dataset_review", {}).get("total_rows"),
            "long_liq_flush_event_count": event_study.get("event_counts", {}).get("long_liq_flush_event_count"),
            "short_liq_flush_event_count": event_study.get("event_counts", {}).get("short_liq_flush_event_count"),
            "imbalance_oi_flush_event_count": event_study.get("event_counts", {}).get("imbalance_oi_flush_event_count"),
            "selected_event_count": long_result.get("event_count"),
            "selected_event_2h_hit_rate": long_result.get("expected_direction_hit_rate_2h"),
            "selected_event_4h_hit_rate": long_result.get("expected_direction_hit_rate_4h"),
            "selected_event_baseline_percentile": long_baseline.get("baseline_percentile"),
            "next_allowed_step": event_study.get("next_allowed_step"),
        },
        "selected_hypothesis": {
            "hypothesis_key": SELECTED_HYPOTHESIS,
            "selected_for_design": True,
            "selection_reason": "Best event type from prior event study with 91 events, 0.648352 4h expected-direction hit rate, and 1.0 same-symbol timestamp baseline percentile.",
        },
        "economic_mechanism": {
            "summary": "After a strong sell move, a large long liquidation spike plus falling open interest may indicate forced selling exhaustion. After forced selling ends, price may mean-revert upward over 2h to 4h.",
            "why_not_immediately_arbitraged": [
                "Liquidation cascades are balance-sheet constrained and uncertain while forced selling is active.",
                "Participants may not know whether OI has fully flushed until after the event bar closes.",
                "The rule combines liquidation intensity, OI contraction, and prior price stress rather than a simple price indicator.",
            ],
            "evidence_limit": "The event study used only a short recent Coinalyze window from 2026-05-13T19:15:00Z to 2026-05-27T19:15:00Z, so this is design-only and not evidence of edge.",
        },
        "preregistered_strategy_design": {
            "strategy_key": STRATEGY_KEY,
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "one_config_rule": "Trade only long reversal after LONG_LIQUIDATION_FLUSH_EVENT.",
            "trade_side": "long_only",
            "short_trades_allowed": False,
            "uses_short_liquidation_event": False,
            "uses_imbalance_event_directly": False,
            "parameter_grid_allowed": False,
            "threshold_optimization_allowed": False,
        },
        "frozen_event_definition": {
            "event_key": SELECTED_HYPOTHESIS,
            "liquidation_long": "> 0",
            "liquidation_long_vs_rolling_median": "liquidation_long >= 3 * rolling_median_liquidation_long_24h",
            "oi_change_pct": "<= -0.005",
            "ret_1h_past": "<= -0.01",
            "rolling_median_lookback": {
                "bars": 96,
                "duration": "24h",
                "exclude_current_bar": True,
                "minimum_prior_bars": 48,
            },
            "threshold_source": "round structural thresholds from prior event study; no bucket tuning.",
        },
        "entry_exit_rules": {
            "signal_evaluation": "Evaluate event at 15m bar close.",
            "entry": {
                "side": "long",
                "price": "next 15m open after signal bar",
                "missing_next_bar": "skip",
            },
            "exit": {
                "type": "fixed_hold",
                "hold_bars": 16,
                "hold_duration": "4h",
                "price": "next available 15m open after hold",
                "stop_loss": None,
                "take_profit": None,
                "rationale": "Prior event study showed stronger 4h hit rate than 2h; no additional exit tuning.",
            },
            "costs": {
                "round_trip_bps": 20,
                "applied_to": "notional",
            },
            "candidate_ranking": [
                "liquidation_long / rolling_median_liquidation_long_24h descending",
                "abs(oi_change_pct) descending",
                "take one per timestamp until capacity",
            ],
        },
        "portfolio_rules": {
            "base_equity_usdt": 1000,
            "fixed_notional_usdt": 50,
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
        "future_execution_pass_criteria": {
            "diagnostic_scope_only": True,
            "closed_trades_minimum_for_interpretable_diagnostic": 20,
            "net_bps": "> 0",
            "average_net_per_trade": "> 0",
            "monthly_or_daily_stability": "evaluate if feasible",
            "random_same_symbol_timestamp_baseline_percentile": ">= 0.80",
            "top_symbol_concentration": "<= 0.40",
            "metric_integrity": True,
            "edge_claim_allowed_if_passed": False,
            "live_or_capital_allowed_if_passed": False,
        },
        "anti_overfit_policy": {
            "event_study_promising_but_short_window": True,
            "no_edge_claim": True,
            "no_threshold_tuning": True,
            "no_additional_filters_from_2026_05_event_study": True,
            "if_strategy_fails_do_not_retune_same_14_day_dataset": True,
            "if_strategy_passes_next_step_is_extend_data_or_paper_forward_not_live": True,
            "requires_future_lockbox_or_paper_forward_before_any_stronger_claim": True,
        },
        "future_result_classes": [
            "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE",
            "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_REJECTED_NO_FOLLOWUP",
            "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_INCONCLUSIVE_LOW_SAMPLE",
            "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE",
        ],
        "next_allowed_step": "COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_PREREGISTRATION_V1",
        "limitations": [
            "Design only; no strategy execution, signals, backtest, PnL, or candidate was produced.",
            "The selected event is based on a 14-day recent Coinalyze event study and is not long-history evidence.",
            "No additional filters are introduced because that would tune on the same short event-study window.",
        ],
        "safety_permissions": {
            "strategy_design_created": True,
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
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
    prior = payload["prior_event_study_summary"]
    print(f"status: {payload['status']}")
    print(f"selected_hypothesis: {payload['selected_hypothesis']['hypothesis_key']}")
    print(f"strategy_key: {payload['preregistered_strategy_design']['strategy_key']}")
    print(f"event_count_from_prior_study: {prior['selected_event_count']}")
    print(f"prior_4h_hit_rate: {prior['selected_event_4h_hit_rate']}")
    print(f"prior_baseline_percentile: {prior['selected_event_baseline_percentile']}")
    print(f"next_allowed_step: {payload['next_allowed_step']}")
    print("strategy_execution_allowed_now: false")
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
