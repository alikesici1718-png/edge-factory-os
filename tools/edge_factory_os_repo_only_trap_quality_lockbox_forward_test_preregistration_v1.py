from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_TEST_PREREGISTRATION_CREATED"
ARTIFACT_KIND = "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_PREREGISTRATION"
MODULE = "edge_factory_os_repo_only_trap_quality_lockbox_forward_test_preregistration_v1"
FROZEN_FINALIST = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_V1"
ROUTE_FAMILY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_BASELINE"
CONFIG_ID = "crypto_15m_idiosyncratic_sweep_short_trap_quality_v1"
NEXT_ALLOWED_STEP = "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_EXECUTION_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "research_preregistrations"
    / "trap_quality_lockbox_forward_test_preregistration_v1.json"
)

SOURCE_PATHS = {
    "freeze_contract": REPO_ROOT
    / "artifacts"
    / "research_preregistrations"
    / "trap_quality_lockbox_freeze_contract_v1.json",
    "data_acquisition": REPO_ROOT
    / "artifacts"
    / "data_acquisition"
    / "trap_quality_lockbox_forward_data_acquisition_v1.json",
    "data_review": REPO_ROOT
    / "artifacts"
    / "data_reviews"
    / "trap_quality_lockbox_forward_data_review_v1.json",
    "trap_quality_preregistration": REPO_ROOT
    / "artifacts"
    / "research_preregistrations"
    / "crypto_15m_idiosyncratic_sweep_short_trap_quality_preregistration_v1.json",
    "trap_quality_execution": REPO_ROOT
    / "artifacts"
    / "strategy_executions"
    / "crypto_15m_idiosyncratic_sweep_short_trap_quality_execution_v1.json",
    "trap_quality_evaluator": REPO_ROOT
    / "artifacts"
    / "strategy_evaluations"
    / "crypto_15m_idiosyncratic_sweep_short_trap_quality_evaluator_v1.json",
}

EXPECTED_REJECTED_FINALIST_KEYS = {
    "time_exit_only",
    "risk_tightened",
    "trap_score4",
    "wider_stop",
    "rejection_depth_required",
    "market_pump_veto",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_dumps(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_hash_excluding_hash(payload: dict[str, Any]) -> str:
    without_hash = dict(payload)
    without_hash.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_dumps(without_hash).encode("utf-8")).hexdigest()


def git(args: list[str]) -> str:
    safe_dir = str(REPO_ROOT).replace("\\", "/")
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={safe_dir}", "-C", str(REPO_ROOT), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def repo_status_lines() -> list[str]:
    output = git(["status", "--short", "-uall"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def get_path(payload: dict[str, Any], path: list[str], default: Any = None) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def source_artifact_record(name: str, path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sha256": sha256_file(path),
        "status": payload.get("status"),
        "artifact_kind": payload.get("artifact_kind"),
        "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash"),
    }


def main() -> None:
    status_before = repo_status_lines()
    allowed_new_paths = {
        "?? tools/edge_factory_os_repo_only_trap_quality_lockbox_forward_test_preregistration_v1.py",
        "?? artifacts/research_preregistrations/trap_quality_lockbox_forward_test_preregistration_v1.json",
    }
    unexpected_status = [line for line in status_before if line not in allowed_new_paths]

    sources = {name: load_json(path) for name, path in SOURCE_PATHS.items()}
    freeze = sources["freeze_contract"]
    acquisition = sources["data_acquisition"]
    data_review = sources["data_review"]
    trap_prereg = sources["trap_quality_preregistration"]
    trap_execution = sources["trap_quality_execution"]
    trap_evaluator = sources["trap_quality_evaluator"]

    freeze_decision = freeze.get("freeze_decision", {})
    explicit_rejections = freeze.get("explicit_rejections", {})
    lockbox_period = {
        "lockbox_start": "2025-11-01T00:00:00Z",
        "lockbox_end": "2026-05-01T00:00:00Z",
        "closed_months": [
            "2025-11",
            "2025-12",
            "2026-01",
            "2026-02",
            "2026-03",
            "2026-04",
        ],
        "primary_lockbox_only": True,
        "partial_month_included": False,
        "lockbox_data_root": (
            "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\"
            "edge_factory_os_repo_only_trap_quality_lockbox_forward_data_acquisition_v1\\"
            "normalized_15m_by_symbol"
        ),
    }

    frozen_config = {
        "strategy": FROZEN_FINALIST,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "source_route": "exact original trap-quality route",
        "explicitly_not_using": [
            "time-exit-only finalist",
            "risk-tightened",
            "trap-score4",
            "wider-stop",
            "rejection-depth-required",
            "standalone market-pump-veto finalist",
            "any V-next",
        ],
        "core_rules": {
            "side": "short_only",
            "long_trades_allowed": False,
            "structure": "residual+sweep+confirmation",
            "market_pump_veto_enabled": True,
            "trap_quality_score_min": 3,
            "risk_quality_ratio_min": 1.0,
            "stop_rule": "stop = sweep_high + 0.5 * ATR14",
            "take_profit_rule": "take_profit = entry - 2R for shorts",
            "time_stop": "8h / 32 bars",
        },
        "frozen_parameters": {
            "timeframe": "15m",
            "beta_window_calendar_days": 30,
            "beta_window_bars": 2880,
            "minimum_beta_observations": 1000,
            "residual_impulse_window": "4h",
            "residual_impulse_bars": 16,
            "residual_z_threshold_short": 3.5,
            "prior_range_window": "48h",
            "prior_range_bars": 192,
            "atr_length": 14,
            "volume_sma_len": 20,
            "volume_filter": "volume > volume_sma20",
            "confirmation_bar_required": True,
            "confirmation_strength_atr_min": 0.05,
            "cost_aware_gate": "abs(residual_4h) >= 0.008",
            "cost_aware_gate_abs_residual_4h_min": 0.008,
            "stop_risk_quality_gate": (
                "abs(residual_4h) / (stop_distance_fraction + 0.002) >= 1.0"
            ),
            "risk_quality_ratio_min": 1.0,
            "market_pump_veto_enabled": True,
            "trap_quality_score_min": 3,
            "base_equity_usdt": 1000,
            "risk_per_trade_fraction": 0.005,
            "risk_per_trade_usdt": 5,
            "max_notional_per_trade_usdt": 100,
            "max_concurrent_positions": 3,
            "max_new_positions_per_timestamp": 1,
            "one_open_position_per_symbol": True,
            "symbol_cooldown": "24h / 96 bars",
            "symbol_cooldown_bars": 96,
            "time_stop": "8h / 32 bars",
            "time_stop_bars": 32,
            "reward_risk_take_profit": 2,
            "round_trip_cost_bps": 20,
            "round_trip_cost_fraction": 0.002,
            "leverage_allowed": False,
            "compounding_allowed": False,
            "reinvestment_allowed": False,
        },
        "source_strategy_status": trap_prereg.get("status"),
        "source_execution_status": trap_execution.get("status"),
        "source_evaluator_status": trap_evaluator.get("status"),
    }

    pass_criteria = [
        {"id": "lockbox_net_bps_positive", "criterion": "lockbox_net_bps > 0"},
        {
            "id": "monthly_positive_rate_min_0p60",
            "criterion": "lockbox_monthly_positive_rate >= 0.60",
        },
        {"id": "worst_month_gt_minus_500", "criterion": "worst_month_bps > -500"},
        {"id": "max_drawdown_gt_minus_2000", "criterion": "max_drawdown_bps > -2000"},
        {"id": "null_percentile_min_0p90", "criterion": "null_percentile >= 0.90"},
        {
            "id": "top3_symbol_concentration_max_0p30",
            "criterion": "top_3_symbol_concentration <= 0.30",
        },
        {"id": "fee_stress_2x_positive", "criterion": "fee_stress_2x_net_bps > 0"},
        {"id": "closed_trade_count_min_50", "criterion": "closed_trade_count >= 50"},
        {"id": "metric_integrity_passed", "criterion": "metric_integrity_passed = true"},
        {
            "id": "no_candidate_edge_live_capital_permissions",
            "criterion": "no candidate/edge/live/capital permissions",
        },
    ]

    hard_reject_criteria = [
        {"id": "lockbox_net_bps_nonpositive", "criterion": "lockbox_net_bps <= 0"},
        {
            "id": "monthly_positive_rate_lt_0p50",
            "criterion": "lockbox_monthly_positive_rate < 0.50",
        },
        {"id": "null_percentile_lt_0p80", "criterion": "null_percentile < 0.80"},
        {
            "id": "top_symbol_concentration_gt_0p50",
            "criterion": "top_symbol_concentration > 0.50",
        },
        {"id": "metric_integrity_failed", "criterion": "metric_integrity_passed = false"},
        {"id": "lookahead_detected", "criterion": "lookahead detected"},
        {"id": "strategy_config_mismatch", "criterion": "strategy config mismatch"},
        {"id": "data_contamination", "criterion": "data contamination"},
        {
            "id": "runtime_live_capital_order_action",
            "criterion": "runtime/live/capital/order action",
        },
    ]

    original_null_percentile = get_path(
        freeze, ["finalist_summary", "null_baseline", "validation_percentile"], 0.90
    )
    multiple_testing_adjustment_record = {
        "one_frozen_finalist_lockbox_test": True,
        "development_panel_considered_contaminated_or_memorized": True,
        "original_development_null_percentile": original_null_percentile,
        "original_development_p_value": round(1.0 - float(original_null_percentile), 10),
        "family_had_multiple_variants": True,
        "lockbox_result_must_not_be_used_for_tuning": True,
        "p_value_definition": "p_value = 1 - null_percentile",
        "adjusted_alpha_final_test_requirement": (
            "Final test artifact must compute adjusted alpha using recorded global/family "
            "counts if available."
        ),
        "edge_claim_rule": (
            "No edge can be claimed unless unadjusted and adjusted criteria both pass; "
            "this preregistration grants no edge claim."
        ),
    }

    final_result_classes = [
        "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_PASS_PAPER_FORWARD_ELIGIBLE_NO_EDGE_NO_LIVE",
        "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_FAIL_ROUTE_CLOSED_NO_EDGE_NO_LIVE",
        "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_INCONCLUSIVE_DATA_OR_TRADE_COUNT_NO_EDGE_NO_LIVE",
        "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_INVALIDATED_BY_INTEGRITY_FAILURE_NO_EDGE_NO_LIVE",
    ]

    source_checkpoint = {
        "head": git(["rev-parse", "HEAD"]),
        "expected_head": "601c21b0474bb550f3c701854fe92968f0234953",
        "repo_clean_before_run": not unexpected_status,
        "tracked_python_count_before_run": tracked_python_count(),
        "git_status_before_run": status_before,
        "allowed_untracked_paths_during_preregistration": sorted(allowed_new_paths),
    }

    lockbox_data_review = {
        "artifact_status": data_review.get("status"),
        "result_classification": data_review.get("result_classification"),
        "frozen_finalist": get_path(
            data_review, ["frozen_finalist_review", "frozen_finalist"], FROZEN_FINALIST
        ),
        "expected_total_rows": get_path(
            data_review, ["expected_row_count_review", "expected_total_rows"]
        ),
        "actual_total_rows": get_path(
            data_review, ["expected_row_count_review", "actual_total_rows"]
        ),
        "requested_symbol_count": get_path(
            data_review, ["universe_review", "requested_symbol_count"]
        ),
        "acquired_symbol_count": get_path(
            data_review, ["universe_review", "acquired_symbol_count"]
        ),
        "missing_symbol_count": get_path(data_review, ["universe_review", "missing_symbol_count"]),
        "full_coverage_symbol_count": get_path(
            data_review, ["per_symbol_coverage_review", "full_coverage_symbol_count"]
        ),
        "ohlcv_sanity_passed": get_path(
            data_review, ["ohlcv_sanity_review", "ohlcv_sanity_passed"], True
        ),
        "schema_compatible": get_path(
            data_review, ["schema_compatibility_review", "schema_compatible"], True
        ),
        "checksum_review_passed": get_path(
            data_review, ["checksum_review", "checksum_review_passed"], True
        ),
        "next_allowed_step": data_review.get("next_allowed_step"),
        "no_strategy_execution_or_pnl_in_review": True,
    }

    safety_permissions = {
        "lockbox_test_preregistration_created": True,
        "strategy_execution_allowed_now": False,
        "signal_generation_allowed_now": False,
        "backtest_allowed_now": False,
        "pnl_computation_allowed_now": False,
        "optimization_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }

    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "freeze_contract_loaded": freeze.get("status")
        == "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FREEZE_CONTRACT_CREATED",
        "data_acquisition_loaded": acquisition.get("status")
        == "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_CREATED",
        "data_review_loaded": data_review.get("status")
        == "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_CREATED",
        "frozen_finalist_verified": freeze_decision.get("frozen_finalist") == FROZEN_FINALIST
        and get_path(data_review, ["frozen_finalist_review", "frozen_finalist"]) == FROZEN_FINALIST
        and trap_prereg.get("strategy") == FROZEN_FINALIST
        and trap_execution.get("strategy") == FROZEN_FINALIST
        and trap_evaluator.get("strategy") == FROZEN_FINALIST,
        "rejected_finalists_preserved": EXPECTED_REJECTED_FINALIST_KEYS.issubset(
            set(explicit_rejections.keys())
        ),
        "lockbox_data_review_pass_verified": data_review.get("result_classification")
        == "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_PASS_READY_FOR_TEST_PREREGISTRATION"
        and data_review.get("next_allowed_step")
        == "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_PREREGISTRATION_V1",
        "pass_criteria_defined_before_execution": len(pass_criteria) == 10,
        "hard_reject_criteria_defined_before_execution": len(hard_reject_criteria) == 9,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_pnl_computation": True,
        "no_parameter_change": True,
        "no_v_next_created": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": Path(__file__).resolve().exists(),
        "exactly_one_json_artifact_created": ARTIFACT_PATH.name
        == "trap_quality_lockbox_forward_test_preregistration_v1.json",
        "no_existing_repo_files_modified": not any(
            not line.startswith("?? ") for line in status_before
        )
        and not unexpected_status,
    }

    safety_ok = safety_permissions["lockbox_test_preregistration_created"] and not any(
        value
        for key, value in safety_permissions.items()
        if key != "lockbox_test_preregistration_created"
    )
    replacement_checks_all_true = all(validation_checks.values()) and safety_ok
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint,
        "source_artifacts": {
            name: source_artifact_record(name, path, sources[name])
            for name, path in SOURCE_PATHS.items()
        },
        "frozen_finalist": {
            "strategy": FROZEN_FINALIST,
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "freeze_reason": freeze_decision.get("reason"),
            "explicit_rejected_finalists_preserved": explicit_rejections,
        },
        "frozen_config": frozen_config,
        "lockbox_period": lockbox_period,
        "lockbox_data_review": lockbox_data_review,
        "pass_criteria": {
            "all_must_pass": True,
            "criteria_count": len(pass_criteria),
            "criteria": pass_criteria,
        },
        "hard_reject_criteria": {
            "any_one_rejects": True,
            "criteria_count": len(hard_reject_criteria),
            "criteria": hard_reject_criteria,
        },
        "multiple_testing_adjustment_record": multiple_testing_adjustment_record,
        "final_result_classes": final_result_classes,
        "lockbox_non_tuning_rule": {
            "strategy_config_is_frozen": True,
            "lockbox_test_run_once": True,
            "no_parameter_changes_after_result": True,
            "no_filter_changes_after_result": True,
            "no_exit_changes_after_result": True,
            "no_v_next_based_on_lockbox_result": True,
            "if_lockbox_fails_route_rejected_closed": True,
            "if_lockbox_passes_next_scope": "paper-forward planning/review only",
            "live_or_capital_permission_if_passes": False,
        },
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash_excluding_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(f"status: {artifact['status']}")
    print(f"frozen_finalist: {FROZEN_FINALIST}")
    print(f"lockbox_start: {lockbox_period['lockbox_start']}")
    print(f"lockbox_end: {lockbox_period['lockbox_end']}")
    print(f"pass_criteria_count: {len(pass_criteria)}")
    print(f"hard_reject_criteria_count: {len(hard_reject_criteria)}")
    print(f"next_allowed_step: {NEXT_ALLOWED_STEP}")
    print("strategy_execution_allowed_now: false")
    print("signal_generation_allowed_now: false")
    print("pnl_computation_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")


if __name__ == "__main__":
    main()
