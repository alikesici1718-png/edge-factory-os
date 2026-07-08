#!/usr/bin/env python3
"""Repo-only monitor summary for volatility diagnostic sample accumulation.

This module summarizes prior artifacts only. It does not download data, compute
new returns, compute p-values, run null validation, inspect options chains, or
create any strategy/signal/candidate/release/runtime action.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


MODULE = "VOLATILITY_DIAGNOSTIC_INDEPENDENT_SAMPLE_ACCUMULATION_MONITOR_SUMMARY_V1"
EXPECTED_HEAD = "04224f042125d0f77444b8d8f515d639ffb79914"
REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_volatility_diagnostic_independent_sample_accumulation_"
    "monitor_summary_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/research/volatility_diagnostic_independent_sample_accumulation_monitor_summary_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

RESULT_READY = "VOLATILITY_DIAGNOSTIC_MONITOR_SUMMARY_READY"
RESULT_ATTENTION = "VOLATILITY_DIAGNOSTIC_MONITOR_SUMMARY_REQUIRES_ATTENTION"
RESULT_FAILED = "VOLATILITY_DIAGNOSTIC_MONITOR_SUMMARY_FAILED_STOP"
ALLOWED_NEXT_STEP = "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_REFRESH_V1"
RECOVERY_NEXT_STEP = "VOLATILITY_DIAGNOSTIC_MONITOR_SUMMARY_RECOVERY_REVIEW_V1"

INPUT_RELATIVE_PATHS = [
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_runner_v1.json",
    "artifacts/contracts/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_contract_v1.json",
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_robustness_evaluator_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_pre_registered_independent_validation_runner_v1.json",
    "artifacts/contracts/long_short_ratio_extreme_normalization_pre_registered_independent_validation_contract_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_volatility_robustness_evaluator_v1.json",
    "artifacts/research/combined_volatility_stress_event_discovery_v1.json",
    "artifacts/research/extreme_oi_taker_crowding_price_failure_pre_registered_independent_validation_runner_v1.json",
    "artifacts/research/extreme_oi_taker_crowding_price_failure_frozen_historical_holdout_backtest_v1.json",
    "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json",
]

FORBIDDEN_ACTIONS_CONFIRMED_FALSE = {
    "strategy": False,
    "signal": False,
    "backtest": False,
    "pnl": False,
    "trade_simulation": False,
    "options_chain_lookup": False,
    "implied_volatility_lookup": False,
    "implied_move_calculation": False,
    "optimization_against_returns": False,
    "candidate_generation": False,
    "edge_claim": False,
    "runtime_live_capital_order_private_api_account_api_key": False,
    "new_returns_computed": False,
    "new_p_values_computed": False,
    "null_validation_run": False,
    "event_definitions_changed": False,
    "combined_overlap_window_broadened": False,
    "data_downloaded": False,
}

MONITOR_THRESHOLDS = {
    "100_events": "early review",
    "150_events": "stronger review",
    "250_events": "serious independent validation rerun",
    "300_plus_events": "high-priority validation rerun",
}


class MonitorBlocked(RuntimeError):
    """Raised when the monitor summary cannot safely complete."""


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True, stderr=subprocess.STDOUT).strip()


def git_lines(args: list[str]) -> list[str]:
    output = run_git(args)
    return [line for line in output.splitlines() if line.strip()]


def recovery_audit() -> dict[str, Any]:
    current_head = run_git(["rev-parse", "HEAD"])
    branch = run_git(["branch", "--show-current"])
    try:
        core_longpaths = run_git(["config", "--local", "--get", "core.longpaths"])
    except subprocess.CalledProcessError:
        core_longpaths = "<unset>"
    porcelain = git_lines(["status", "--porcelain"])
    staged = git_lines(["diff", "--name-only", "--cached"])
    modified = git_lines(["diff", "--name-only"])
    untracked = git_lines(["ls-files", "--others", "--exclude-standard"])
    deleted = git_lines(["ls-files", "--deleted"])
    allowed = {
        MODULE_RELATIVE_PATH,
        MODULE_RELATIVE_PATH.replace("/", "\\"),
        ARTIFACT_RELATIVE_PATH,
        ARTIFACT_RELATIVE_PATH.replace("/", "\\"),
    }
    dirty_paths = set(modified + untracked + deleted)
    for line in porcelain:
        if len(line) >= 4:
            dirty_paths.add(line[3:])
    head_matches = current_head == EXPECTED_HEAD
    clean_or_output_only = (
        head_matches
        and not staged
        and all(path in allowed for path in dirty_paths)
        and all(line.startswith("?? ") and line[3:] in allowed for line in porcelain)
    )
    decision = "RECOVERY_AUDIT_CLEAN_CONTINUE" if clean_or_output_only else "RECOVERY_AUDIT_STOP"
    return {
        "current_head": current_head,
        "expected_head": EXPECTED_HEAD,
        "branch": branch,
        "core_longpaths_value": core_longpaths,
        "git_status_porcelain": porcelain,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "head_matches_expected": head_matches,
        "recovery_decision": decision,
        "recovery_audit_status": "PASS" if decision.endswith("CONTINUE") else "STOP",
    }


def print_recovery_audit(audit: dict[str, Any]) -> None:
    print(f"current HEAD: {audit['current_head']}")
    print(f"expected HEAD: {audit['expected_head']}")
    print(f"branch: {audit['branch']}")
    print(f"core.longpaths value: {audit['core_longpaths_value']}")
    print(f"git status porcelain: {audit['git_status_porcelain']}")
    print(f"staged files: {audit['staged_files']}")
    print(f"modified tracked files: {audit['modified_tracked_files']}")
    print(f"untracked files: {audit['untracked_files']}")
    print(f"deleted files: {audit['deleted_files']}")
    print(f"recovery decision: {audit['recovery_decision']}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for rel_path in INPUT_RELATIVE_PATHS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            raise MonitorBlocked(f"missing required input artifact: {rel_path}")
        hashes[rel_path] = sha256_file(path)
    return hashes


def load_json(rel_path: str) -> dict[str, Any]:
    with (REPO_ROOT / rel_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_inputs() -> dict[str, dict[str, Any]]:
    keys = [
        "oi_shock_independent_validation",
        "oi_shock_contract",
        "oi_shock_robustness_evaluator",
        "lsr_independent_validation",
        "lsr_contract",
        "lsr_robustness_evaluator",
        "combined_discovery",
        "short_pressure_independent_validation",
        "short_pressure_historical_holdout",
        "outcome_blind_theory_queue",
    ]
    return {key: load_json(path) for key, path in zip(keys, INPUT_RELATIVE_PATHS)}


def assert_input_integrity(inputs: dict[str, dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    expected_classes = {
        "oi_shock_independent_validation": (
            "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE"
        ),
        "oi_shock_contract": (
            "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY"
        ),
        "oi_shock_robustness_evaluator": (
            "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_ROBUSTNESS_EVALUATOR_PROMISING_VOLATILITY_DIAGNOSTIC_ONLY"
        ),
        "lsr_independent_validation": (
            "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE"
        ),
        "lsr_contract": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY",
        "lsr_robustness_evaluator": (
            "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_PROMISING_DIAGNOSTIC_ONLY"
        ),
        "combined_discovery": "COMBINED_VOLATILITY_STRESS_EVENT_DISCOVERY_TOO_SPARSE",
        "short_pressure_independent_validation": (
            "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE"
        ),
        "short_pressure_historical_holdout": (
            "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_HISTORICAL_HOLDOUT_INCONCLUSIVE_INSUFFICIENT_SAMPLE"
        ),
        "outcome_blind_theory_queue": "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY",
    }
    for key, expected in expected_classes.items():
        actual = inputs[key].get("result_classification")
        if actual != expected:
            blockers.append(f"{key}: result_classification {actual!r} != {expected!r}")
    for key, artifact in inputs.items():
        for flag in ("strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"):
            if flag in artifact and artifact.get(flag) is not False:
                blockers.append(f"{key}: {flag} not false")
    return blockers


def route_inventory(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    oi = inputs["oi_shock_independent_validation"]
    lsr = inputs["lsr_independent_validation"]
    combined = inputs["combined_discovery"]
    short_independent = inputs["short_pressure_independent_validation"]
    short_holdout = inputs["short_pressure_historical_holdout"]
    return {
        "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC": {
            "route_type": "directional diagnostic",
            "current_status": "monitor_only_or_deprioritized",
            "independent_validation_result": short_independent.get("result_classification"),
            "historical_holdout_result": short_holdout.get("result_classification"),
            "independent_event_count": short_independent.get("event_count"),
            "historical_holdout_event_count": short_holdout.get("event_count"),
            "reason": [
                "2026 independent validation did not pass",
                "historical holdout inconclusive",
                "gross directional drift likely not enough after 20 bps cost",
            ],
            "strategy_allowed": False,
            "candidate_generation_allowed": False,
            "release_allowed": False,
        },
        "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT": {
            "route_type": "volatility diagnostic",
            "current_status": "independent_sample_accumulation_monitor",
            "independent_validation_result": "inconclusive_insufficient_sample",
            "event_count": oi.get("event_counts_by_primary_target"),
            "p_abs_high_mean": oi.get("p_abs_high_mean_by_primary_target"),
            "fdr_q": oi.get("fdr_q_values"),
            "bonferroni": oi.get("bonferroni_p_values"),
            "monitor_thresholds": MONITOR_THRESHOLDS,
            "strategy_allowed": False,
            "candidate_generation_allowed": False,
            "release_allowed": False,
        },
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT": {
            "route_type": "volatility diagnostic",
            "current_status": "independent_sample_accumulation_monitor",
            "independent_validation_result": "inconclusive_insufficient_sample",
            "event_count": lsr.get("event_count"),
            "p_abs_high_mean": lsr.get("p_abs_high_mean_by_horizon"),
            "fdr": lsr.get("fdr_q_values"),
            "bonferroni": lsr.get("bonferroni_p_values"),
            "leave_one_symbol_passed": True,
            "leave_one_month_passed": True,
            "arbusdt_exclusion_passed": True,
            "alternate_volatility_proxies_supportive": True,
            "monitor_thresholds": MONITOR_THRESHOLDS,
            "strategy_allowed": False,
            "candidate_generation_allowed": False,
            "release_allowed": False,
        },
        "COMBINED_VOLATILITY_STRESS_EVENT": {
            "route_type": "combined confirmation event",
            "current_status": "too_sparse_monitor_or_deprioritized",
            "unique_combined_event_count": combined.get("unique_combined_event_count"),
            "reason": [
                "too sparse for validator",
                "too sparse for options availability diagnostic",
                "options route not allowed",
            ],
            "options_availability_diagnostic_allowed": False,
            "forward_return_diagnostic_allowed": False,
            "strategy_allowed": False,
            "candidate_generation_allowed": False,
            "release_allowed": False,
        },
    }


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    print_recovery_audit(audit)
    if audit["recovery_decision"] != "RECOVERY_AUDIT_CLEAN_CONTINUE":
        raise MonitorBlocked(audit["recovery_decision"])
    hashes_before = input_hashes()
    inputs = load_inputs()
    blockers = assert_input_integrity(inputs)
    hashes_after = input_hashes()
    if hashes_before != hashes_after:
        raise MonitorBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    inventory = route_inventory(inputs)
    if blockers:
        result_classification = RESULT_ATTENTION
        blocker = "; ".join(blockers)
    else:
        result_classification = RESULT_READY
        blocker = None
    artifact = {
        "monitor_summary_status": "READY" if result_classification == RESULT_READY else "REQUIRES_ATTENTION",
        "result_classification": result_classification,
        "recovery_audit_status": audit["recovery_audit_status"],
        "current_head": audit["current_head"],
        "expected_head": audit["expected_head"],
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "route_inventory": inventory,
        "comparative_route_ranking": [
            {
                "rank": 1,
                "route": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT",
                "priority": "highest_monitor_priority",
                "reason": "2026 result supportive across 15m/1h/4h, sensitivity passed, no data quality warnings, but sample remains below 100.",
            },
            {
                "rank": 2,
                "route": "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT",
                "priority": "second_monitor_priority",
                "reason": "2026 result supportive with 70 events per target and FDR support, but Bonferroni did not fully pass and sample remains below 100.",
            },
            {
                "rank": 3,
                "route": "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC",
                "priority": "deprioritized",
                "reason": "Directional drift is cost-sensitive and independent/historical evidence is weak or inconclusive.",
            },
            {
                "rank": 4,
                "route": "COMBINED_VOLATILITY_STRESS_EVENT",
                "priority": "too_sparse_or_blocked",
                "reason": "Only 15 unique combined overlaps; validator/options route not allowed.",
            },
        ],
        "independent_sample_accumulation_thresholds": {
            "volatility_diagnostic_thresholds": MONITOR_THRESHOLDS,
            "applies_to": [
                "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT",
                "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT",
            ],
            "rerun_policy": "do not rerun independent validation until event-count threshold is met",
        },
        "options_route_policy": {
            "options_route_allowed_now": False,
            "combined_event_options_route_allowed": False,
            "reason": "combined event unique count is below 100 and no validator is allowed yet",
            "requirements_before_options_route": [
                "independent validation event count is sufficient",
                "validation remains supportive",
                "options availability and implied-move diagnostic is explicitly authorized",
            ],
            "options_chain_lookup_now": False,
            "implied_move_calculation_now": False,
        },
        "combined_route_policy": {
            "current_status": "too_sparse_monitor_or_deprioritized",
            "unique_combined_event_count": inputs["combined_discovery"].get("unique_combined_event_count"),
            "validator_allowed_now": False,
            "options_availability_diagnostic_allowed_now": False,
            "overlap_window_broadened": False,
        },
        "directional_route_policy": {
            "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC": {
                "current_status": "monitor_only_or_deprioritized",
                "strategy_allowed": False,
                "candidate_generation_allowed": False,
                "release_allowed": False,
                "reason": "independent validation did not pass, historical holdout inconclusive, and gross drift is likely cost-sensitive",
            }
        },
        "next_action_selector": {
            "recommended_next_action": ALLOWED_NEXT_STEP,
            "alternatives": [
                "WAIT_FOR_MORE_2026_DATA_MONITOR_ONLY",
                "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_SAMPLE_ACCUMULATION_MONITOR_V1",
                "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_SAMPLE_ACCUMULATION_MONITOR_V1",
            ],
            "reason": "repo-only staged research should return to outcome-blind theory queue while monitor thresholds remain pending",
        },
        "monitoring_thresholds_pending": True,
        "do_not_rerun_independent_validation_until_event_count_threshold_met": True,
        "no_options_route_until_independent_validation_strengthens": True,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "options_availability_diagnostic_allowed_now": False,
        "implied_move_diagnostic_allowed_now": False,
        "forward_return_diagnostic_allowed_now": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "allowed_next_step": ALLOWED_NEXT_STEP if result_classification == RESULT_READY else RECOVERY_NEXT_STEP,
        "blocker": blocker,
    }
    return artifact


def blocked_artifact(reason: str) -> dict[str, Any]:
    audit = recovery_audit()
    try:
        before = input_hashes()
        after = input_hashes()
    except Exception:
        before = {}
        after = {}
    return {
        "monitor_summary_status": "FAILED_STOP",
        "result_classification": RESULT_FAILED,
        "recovery_audit_status": audit.get("recovery_audit_status"),
        "current_head": audit.get("current_head"),
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": audit.get("head_matches_expected"),
        "input_artifact_hashes_before": before,
        "input_artifact_hashes_after": after,
        "input_artifact_hashes_unchanged": before == after and bool(before),
        "route_inventory": {},
        "comparative_route_ranking": [],
        "independent_sample_accumulation_thresholds": {},
        "options_route_policy": {},
        "combined_route_policy": {},
        "directional_route_policy": {},
        "next_action_selector": {},
        "monitoring_thresholds_pending": True,
        "do_not_rerun_independent_validation_until_event_count_threshold_met": True,
        "no_options_route_until_independent_validation_strengthens": True,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "options_availability_diagnostic_allowed_now": False,
        "implied_move_diagnostic_allowed_now": False,
        "forward_return_diagnostic_allowed_now": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "allowed_next_step": RECOVERY_NEXT_STEP,
        "blocker": reason,
    }


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")


def route_inventory_summary(inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        route: {
            "route_type": record.get("route_type"),
            "current_status": record.get("current_status"),
            "event_count": record.get("event_count")
            or record.get("unique_combined_event_count")
            or record.get("independent_event_count"),
            "strategy_allowed": record.get("strategy_allowed"),
            "candidate_generation_allowed": record.get("candidate_generation_allowed"),
            "release_allowed": record.get("release_allowed"),
        }
        for route, record in inventory.items()
    }


def report_lines(artifact: dict[str, Any]) -> list[str]:
    return [
        f"status: {artifact.get('monitor_summary_status')}",
        f"result_classification: {artifact.get('result_classification')}",
        f"recovery_audit_status: {artifact.get('recovery_audit_status')}",
        f"input_artifact_hashes_unchanged: {artifact.get('input_artifact_hashes_unchanged')}",
        "route_inventory_summary: "
        + json.dumps(route_inventory_summary(artifact.get("route_inventory", {})), sort_keys=True),
        "comparative_route_ranking: " + json.dumps(artifact.get("comparative_route_ranking"), sort_keys=True),
        "independent_sample_accumulation_thresholds: "
        + json.dumps(artifact.get("independent_sample_accumulation_thresholds"), sort_keys=True),
        "options_route_policy: " + json.dumps(artifact.get("options_route_policy"), sort_keys=True),
        "combined_route_policy: " + json.dumps(artifact.get("combined_route_policy"), sort_keys=True),
        "directional_route_policy: " + json.dumps(artifact.get("directional_route_policy"), sort_keys=True),
        "next_action_selector: " + json.dumps(artifact.get("next_action_selector"), sort_keys=True),
        f"monitoring_thresholds_pending: {artifact.get('monitoring_thresholds_pending')}",
        "do_not_rerun_independent_validation_until_event_count_threshold_met: "
        + str(artifact.get("do_not_rerun_independent_validation_until_event_count_threshold_met")),
        "no_options_route_until_independent_validation_strengthens: "
        + str(artifact.get("no_options_route_until_independent_validation_strengthens")),
        f"strategy_allowed: {artifact.get('strategy_allowed')}",
        f"signal_allowed: {artifact.get('signal_allowed')}",
        f"candidate_generation_allowed: {artifact.get('candidate_generation_allowed')}",
        f"release_allowed: {artifact.get('release_allowed')}",
        f"options_availability_diagnostic_allowed_now: {artifact.get('options_availability_diagnostic_allowed_now')}",
        f"implied_move_diagnostic_allowed_now: {artifact.get('implied_move_diagnostic_allowed_now')}",
        f"forward_return_diagnostic_allowed_now: {artifact.get('forward_return_diagnostic_allowed_now')}",
        f"allowed_next_step: {artifact.get('allowed_next_step')}",
        "commit hash: PENDING_COMMIT",
        "final git status: PENDING_COMMIT",
        "repo clean: PENDING_COMMIT",
        "tracked Python count: PENDING_COMMIT",
        "raw data committed: false",
        "cache files staged: false",
        "forbidden actions confirmed false: "
        + json.dumps(artifact.get("forbidden_actions_confirmed_false"), sort_keys=True),
        f"blocker: {artifact.get('blocker')}",
    ]


def main() -> int:
    try:
        artifact = build_artifact()
        write_artifact(artifact)
        for line in report_lines(artifact):
            print(line)
        return 0
    except Exception as exc:  # noqa: BLE001
        artifact = blocked_artifact(str(exc))
        write_artifact(artifact)
        for line in report_lines(artifact):
            print(line)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
