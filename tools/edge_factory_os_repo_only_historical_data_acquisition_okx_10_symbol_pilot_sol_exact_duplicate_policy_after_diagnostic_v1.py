from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_exact_duplicate_policy_after_diagnostic_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "5ae6c01"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_DUPLICATE_"
    "DIAGNOSTIC_EXACT_DUPLICATE_POLICY_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_EXACT_DUPLICATE_"
    "POLICY_APPROVED_POLICY_CLEAN_BUILD_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_EXACT_DUPLICATE_"
    "POLICY_FAILED_REVIEW"
)

TARGET_SYMBOL = "SOL-USDT-SWAP"
DUPLICATE_OPEN_TIME = 1_697_108_400_000
DUPLICATE_OPEN_TIME_UTC = "2023-10-12T11:00:00+00:00"
DUPLICATE_SOURCE_DATE = "2023-10-12"
DUPLICATE_SOURCE_FILE = "SOL-USDT-SWAP-candlesticks-2023-10-12.csv"
DUPLICATE_RESOLUTION_POLICY = "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROW_KEEP_ONE_CANONICAL_ROW"
EXACT_DUPLICATE_EXTRA_ROWS_TO_DROP = 1
SOL_EXPECTED_CLEAN_SOURCE_ROWS = 1_516_320
SOL_EXPECTED_OUTPUT_ROWS = 25_272
SOL_EXPECTED_COMPLETE_ROWS = 25_272
SOL_EXPECTED_INCOMPLETE_ROWS = 0

BTC_OUTPUT_ROWS = 25_272
BTC_COMPLETE_ROWS = 25_271
BTC_INCOMPLETE_ROWS = 1
ETH_OUTPUT_ROWS = 25_272
ETH_COMPLETE_ROWS = 25_271
ETH_INCOMPLETE_ROWS = 1
ETH_EXACT_DUPLICATE_ROWS_TO_DROP = 327
ETH_MATERIAL_CONFLICT_ROWS_TO_QUARANTINE = 2
ETH_CLEAN_SOURCE_ROWS_AFTER_POLICY = 1_516_319
REMAINING_7_SYMBOLS = [
    "XRP-USDT-SWAP",
    "DOGE-USDT-SWAP",
    "ADA-USDT-SWAP",
    "AVAX-USDT-SWAP",
    "LINK-USDT-SWAP",
    "LTC-USDT-SWAP",
    "DOT-USDT-SWAP",
]
REMAINING_7_OUTPUT_ROWS = 176_904
NOMINAL_TOTAL_PILOT_OUTPUT_ROWS = 252_720
EXPECTED_TOTAL_COMPLETE_1H_ROWS_AFTER_POLICY = 252_718
EXPECTED_TOTAL_INCOMPLETE_1H_ROWS_AFTER_POLICY = 2
ACTIVE_P1_ATTENTION_COUNT = 12

AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_EXACT_DUPLICATE_"
    "POLICY_APPROVED_POLICY_CLEAN_BUILD_READY"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_after_sol_exact_duplicate_policy_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_exact_duplicate_policy_blocked_record_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

SOL_DIAGNOSTIC_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_duplicate_diagnostic_after_policy_clean_build_anomaly_v1"
)
SOL_ANOMALY_RECORD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_eth_material_policy_v1"
)
ETH_MATERIAL_POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_material_duplicate_conflict_policy_after_residual_diagnostic_v1"
)
BTC_POLICY_SUMMARY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_"
    "policy_clean_pipeline_summary_after_rebuild_validator_v1"
)

ARTIFACTS = {
    "sol_diagnostic_summary": SOL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_summary.json",
    "sol_diagnostic": SOL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic.json",
    "sol_raw_rows": SOL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_sol_duplicate_raw_rows_report.json",
    "sol_field_diff": SOL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_sol_duplicate_field_diff_report.json",
    "sol_diagnostic_approval": SOL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_approval_record.json",
    "sol_anomaly_summary": SOL_ANOMALY_RECORD_DIR / f"{SOL_ANOMALY_RECORD_DIR.name}_latest.json",
    "sol_anomaly_blocked_record": SOL_ANOMALY_RECORD_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record_after_eth_policy.json",
    "eth_material_policy_summary": ETH_MATERIAL_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_summary.json",
    "eth_material_policy": ETH_MATERIAL_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy.json",
    "eth_policy_counts": ETH_MATERIAL_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_duplicate_group_policy_counts.json",
    "btc_policy_clean_summary": BTC_POLICY_SUMMARY_DIR
    / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary.json",
}

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "full_csv_read_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "rebuild_execution_performed_now": False,
    "dedupe_execution_performed_now": False,
    "output_1h_csv_created_now": False,
    "output_csv_created": False,
    "modified_source_output_created_now": False,
    "row_modification_performed_now": False,
    "choose_conflicting_row_performed_now": False,
    "average_conflicting_rows_performed_now": False,
    "merge_conflicting_rows_performed_now": False,
    "ohlcv_modification_performed_now": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_candidate_touched": False,
    "edge_profit_claim_made": False,
    "full_universe_ready_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class PolicyBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-C",
            str(REPO_ROOT),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def repo_has_only_this_tool_change() -> bool:
    status = run_git(["status", "--short"]).splitlines()
    if not status:
        return True
    approved_rel = APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()
    return all(line[3:].replace("\\", "/") == approved_rel for line in status)


def tracked_python_count() -> int:
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PolicyBlocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> dict[str, Any]:
    exists[label] = path.exists()
    require(path.exists(), f"missing artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise PolicyBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(data, dict), f"artifact {label} is not a JSON object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_false(payload: dict[str, Any], keys: list[str], label: str) -> None:
    for key in keys:
        require(payload.get(key) is False, f"{label}.{key} must be false")


def validate_sol_diagnostic(payload: dict[str, Any], label: str) -> None:
    require(
        payload.get("historical_data_acquisition_okx_10_symbol_pilot_sol_duplicate_diagnostic_status")
        == PREVIOUS_STATUS,
        f"{label} status mismatch",
    )
    require(payload.get("diagnostic_performed") is True, f"{label} diagnostic not performed")
    require(payload.get("target_symbol") == TARGET_SYMBOL, f"{label} target mismatch")
    require(payload.get("duplicate_open_time_count_total") == 1, f"{label} duplicate count mismatch")
    require(payload.get("diagnostic_duplicate_extra_row_count") == 1, f"{label} extra row count mismatch")
    require(payload.get("duplicate_open_time_group_count") == 1, f"{label} group count mismatch")
    require(payload.get("conflict_open_time") == DUPLICATE_OPEN_TIME, f"{label} open_time mismatch")
    require(payload.get("conflict_open_time_utc") == DUPLICATE_OPEN_TIME_UTC, f"{label} open_time UTC mismatch")
    require(payload.get("duplicate_source_date") == DUPLICATE_SOURCE_DATE, f"{label} source date mismatch")
    require(payload.get("duplicate_source_file") == DUPLICATE_SOURCE_FILE, f"{label} source file mismatch")
    require(payload.get("duplicate_row_count") == 2, f"{label} duplicate row count mismatch")
    require(payload.get("differing_field_count") == 0, f"{label} differing field count mismatch")
    require(payload.get("differing_fields") == [], f"{label} differing fields mismatch")
    require(payload.get("duplicate_classification") == "EXACT_DUPLICATE", f"{label} classification mismatch")
    require(payload.get("exact_duplicate") is True, f"{label} exact duplicate flag mismatch")
    require(payload.get("confirm_only_conflict") is False, f"{label} confirm conflict mismatch")
    require(payload.get("ohlcv_material_conflict") is False, f"{label} material conflict mismatch")
    require(payload.get("symbol_or_schema_conflict") is False, f"{label} symbol/schema conflict mismatch")
    require(payload.get("unknown_conflict") is False, f"{label} unknown conflict mismatch")
    require(payload.get("active_p0_blocker_count") == 0, f"{label} P0 mismatch")
    require(payload.get("active_p1_attention_count") == 0, f"{label} P1 mismatch")
    require(payload.get("next_module") == REQUESTED_MODULE, f"{label} next module mismatch")
    if label == "sol_diagnostic_summary":
        require(payload.get("replacement_checks_all_true") is True, f"{label} replacement checks mismatch")
    validate_false(
        payload,
        [
            "data_build_performed",
            "aggregation_performed_now",
            "output_csv_created",
            "output_valid_for_research_backtest",
            "output_valid_for_edge_claim",
            "safe_for_full_universe_acquisition",
            "broad_acquisition_ready",
            "approval_grants_rebuild_now",
            "approval_grants_dedupe_now",
        ],
        label,
    )


def validate_prior_artifacts(artifacts: dict[str, dict[str, Any]]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved SOL exact duplicate policy module")

    validate_sol_diagnostic(artifacts["sol_diagnostic_summary"], "sol_diagnostic_summary")
    validate_sol_diagnostic(artifacts["sol_diagnostic"], "sol_diagnostic")

    raw_rows = artifacts["sol_raw_rows"]
    field_diff = artifacts["sol_field_diff"]
    approval = artifacts["sol_diagnostic_approval"]
    anomaly_summary = artifacts["sol_anomaly_summary"]
    anomaly_blocked = artifacts["sol_anomaly_blocked_record"]
    eth_summary = artifacts["eth_material_policy_summary"]
    eth_policy = artifacts["eth_material_policy"]
    eth_counts = artifacts["eth_policy_counts"]
    btc_summary = artifacts["btc_policy_clean_summary"]

    require(raw_rows.get("raw_duplicate_rows_captured") is True, "SOL raw rows not captured")
    require(raw_rows.get("duplicate_row_count") == 2, "SOL raw row count mismatch")
    require(raw_rows.get("conflict_open_time") == DUPLICATE_OPEN_TIME, "SOL raw rows open_time mismatch")
    require(raw_rows.get("duplicate_source_file") == DUPLICATE_SOURCE_FILE, "SOL raw rows source file mismatch")
    duplicate_rows = raw_rows.get("duplicate_rows")
    require(isinstance(duplicate_rows, list) and len(duplicate_rows) == 2, "SOL raw duplicate rows incomplete")
    require(
        duplicate_rows[0].get("canonical_values") == duplicate_rows[1].get("canonical_values"),
        "SOL duplicate canonical rows are not identical",
    )
    require(field_diff.get("field_diff_report_created") is True, "SOL field diff report missing")
    require(field_diff.get("differing_field_count") == 0, "SOL field diff count mismatch")
    require(field_diff.get("differing_fields") == [], "SOL field diff fields mismatch")
    require(field_diff.get("exact_duplicate_group") is True, "SOL exact group flag mismatch")
    require(field_diff.get("conflicting_duplicate_group") is False, "SOL conflicting group flag mismatch")
    require(approval.get("approval_grants_future_policy_next") is True, "SOL future policy approval missing")
    require(approval.get("approval_grants_rebuild_now") is False, "SOL diagnostic rebuild approval mismatch")
    require(approval.get("approval_grants_dedupe_now") is False, "SOL diagnostic dedupe approval mismatch")
    require(anomaly_summary.get("anomaly_symbol") == TARGET_SYMBOL, "SOL anomaly target mismatch")
    require(anomaly_summary.get("duplicate_open_time_count_total") == 1, "SOL anomaly duplicate count mismatch")
    require(anomaly_summary.get("partial_output_quarantined") is True, "SOL anomaly quarantine mismatch")
    require(anomaly_blocked.get("eth_material_policy_applied_before_block") is True, "ETH material policy not preserved in SOL anomaly")
    require(anomaly_blocked.get("partial_output_quarantined") is True, "partial output quarantine missing")

    require(eth_summary.get("material_conflict_policy_created") is True, "ETH material policy not created")
    require(eth_summary.get("eth_exact_duplicate_extra_rows_to_drop") == ETH_EXACT_DUPLICATE_ROWS_TO_DROP, "ETH exact drop count mismatch")
    require(eth_summary.get("eth_material_conflict_rows_to_quarantine") == ETH_MATERIAL_CONFLICT_ROWS_TO_QUARANTINE, "ETH quarantine count mismatch")
    require(eth_summary.get("eth_expected_clean_source_rows_after_policy") == ETH_CLEAN_SOURCE_ROWS_AFTER_POLICY, "ETH clean source count mismatch")
    require(eth_summary.get("eth_expected_complete_1h_rows_after_policy") == ETH_COMPLETE_ROWS, "ETH complete rows mismatch")
    require(eth_summary.get("eth_expected_incomplete_1h_rows_after_policy") == ETH_INCOMPLETE_ROWS, "ETH incomplete rows mismatch")
    require(eth_summary.get("approval_grants_future_10_symbol_eth_material_policy_clean_build_next") is True, "ETH future build approval missing")
    require(eth_summary.get("replacement_checks_all_true") is True, "ETH replacement checks mismatch")
    require(eth_policy.get("choose_conflicting_row_allowed") is False, "ETH policy conflict choice mismatch")
    require(eth_policy.get("ohlcv_modification_allowed") is False, "ETH policy OHLCV modification mismatch")
    require(eth_counts.get("policy_counts_complete") is True, "ETH policy counts incomplete")

    require(btc_summary.get("target_symbol") == "BTC-USDT-SWAP", "BTC summary target mismatch")
    require(btc_summary.get("output_1h_row_count") == BTC_OUTPUT_ROWS, "BTC output row count mismatch")
    require(btc_summary.get("complete_1h_row_count") == BTC_COMPLETE_ROWS, "BTC complete row count mismatch")
    require(btc_summary.get("incomplete_1h_row_count") == BTC_INCOMPLETE_ROWS, "BTC incomplete row count mismatch")
    require(btc_summary.get("output_valid_for_pipeline_validation") is True, "BTC pipeline validation flag mismatch")
    validate_false(
        btc_summary,
        [
            "output_valid_for_research_backtest",
            "output_valid_for_edge_claim",
            "broad_acquisition_ready",
            "synthetic_fill_used",
            "forward_fill_used",
            "backfill_used",
        ],
        "btc_policy_clean_summary",
    )


def shared_policy_fields() -> dict[str, Any]:
    return {
        "sol_exact_duplicate_policy_created": True,
        "duplicate_resolution_policy": DUPLICATE_RESOLUTION_POLICY,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_open_time": DUPLICATE_OPEN_TIME,
        "duplicate_open_time_utc": DUPLICATE_OPEN_TIME_UTC,
        "duplicate_source_date": DUPLICATE_SOURCE_DATE,
        "duplicate_source_file": DUPLICATE_SOURCE_FILE,
        "exact_duplicate_extra_rows_to_drop": EXACT_DUPLICATE_EXTRA_ROWS_TO_DROP,
        "material_conflict_present": False,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "ohlcv_modification_allowed": False,
        "synthetic_fill_allowed": False,
        "forward_fill_allowed": False,
        "backfill_allowed": False,
        "exact_duplicate_drop_allowed": True,
        "policy_clean_build_preview_created": True,
        "policy_clean_build_approval_record_created": True,
        "btc_policy_clean_reuse_required": True,
        "eth_material_policy_required": True,
        "sol_exact_dedupe_required": True,
        "future_build_must_fail_closed_on_new_material_conflicts": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_10_symbol_policy_clean_build_next": True,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": ACTIVE_P1_ATTENTION_COUNT,
        "current_evidence_chain_quality_after_policy": AFTER_QUALITY,
        "next_module": NEXT_MODULE_PASS,
    }


def build_payloads(generated_at: str, exists: dict[str, bool], valid: dict[str, bool]) -> tuple[dict[str, Any], dict[str, Any]]:
    shared = shared_policy_fields()
    future_counts = {
        "btc_output_rows": BTC_OUTPUT_ROWS,
        "btc_complete_rows": BTC_COMPLETE_ROWS,
        "btc_incomplete_rows": BTC_INCOMPLETE_ROWS,
        "eth_output_rows": ETH_OUTPUT_ROWS,
        "eth_complete_rows": ETH_COMPLETE_ROWS,
        "eth_incomplete_rows": ETH_INCOMPLETE_ROWS,
        "sol_expected_clean_source_rows": SOL_EXPECTED_CLEAN_SOURCE_ROWS,
        "sol_expected_output_rows": SOL_EXPECTED_OUTPUT_ROWS,
        "sol_expected_complete_rows": SOL_EXPECTED_COMPLETE_ROWS,
        "sol_expected_incomplete_rows": SOL_EXPECTED_INCOMPLETE_ROWS,
        "remaining_7_symbols": REMAINING_7_SYMBOLS,
        "remaining_7_symbols_output_rows": REMAINING_7_OUTPUT_ROWS,
        "nominal_total_pilot_output_rows": NOMINAL_TOTAL_PILOT_OUTPUT_ROWS,
        "expected_total_complete_1h_rows_after_policy": EXPECTED_TOTAL_COMPLETE_1H_ROWS_AFTER_POLICY,
        "expected_total_incomplete_1h_rows_after_policy": EXPECTED_TOTAL_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "all_symbols_complete": False,
        "all_symbols_complete_reason": "BTC and ETH each retain one incomplete policy-clean hour",
    }
    policy = {
        "policy_scope": "SOL_USDT_SWAP_EXACT_DUPLICATE_POLICY_FOR_FUTURE_10_SYMBOL_POLICY_CLEAN_BUILD",
        "policy_created_from_exact_duplicate_diagnostic": True,
        "drop_rule": {
            "drop_only_exact_duplicate_extra_row": True,
            "keep_one_canonical_row_for_duplicate_open_time": True,
            "drop_count": EXACT_DUPLICATE_EXTRA_ROWS_TO_DROP,
            "drop_only_if_all_canonical_fields_identical": True,
            "canonical_fields": [
                "instrument_name",
                "open",
                "high",
                "low",
                "close",
                "vol",
                "vol_ccy",
                "vol_quote",
                "open_time",
                "confirm",
            ],
        },
        "forbidden_resolution_actions": {
            "choose_conflicting_row_allowed": False,
            "average_conflicting_rows_allowed": False,
            "merge_conflicting_rows_allowed": False,
            "ohlcv_modification_allowed": False,
            "synthetic_fill_allowed": False,
            "forward_fill_allowed": False,
            "backfill_allowed": False,
        },
        "execution_performed_now": False,
        **future_counts,
        **shared,
    }
    drop_policy = {
        "sol_exact_duplicate_drop_policy_created": True,
        "drop_policy_type": "EXACT_DUPLICATE_EXTRA_ROW_ONLY",
        "future_build_drop_exact_duplicate_extra_rows": True,
        "future_build_drop_exact_duplicate_extra_rows_count": EXACT_DUPLICATE_EXTRA_ROWS_TO_DROP,
        "future_build_keep_one_canonical_row": True,
        "future_build_must_audit_dropped_exact_duplicate_row": True,
        "dedupe_execution_performed_now": False,
        **shared,
    }
    build_preview = {
        "policy_clean_build_preview_created": True,
        "preview_only": True,
        "future_build_may_reuse_btc_policy_clean_output_after_revalidation": True,
        "future_build_must_apply_eth_material_duplicate_policy": True,
        "future_build_eth_exact_duplicate_rows_to_drop": ETH_EXACT_DUPLICATE_ROWS_TO_DROP,
        "future_build_eth_material_conflict_rows_to_quarantine": ETH_MATERIAL_CONFLICT_ROWS_TO_QUARANTINE,
        "future_build_must_apply_sol_exact_duplicate_policy": True,
        "future_build_sol_exact_duplicate_extra_rows_to_drop": EXACT_DUPLICATE_EXTRA_ROWS_TO_DROP,
        "future_build_remaining_7_symbols_only_if_clean": REMAINING_7_SYMBOLS,
        "future_build_fail_closed_on_new_duplicate": True,
        "future_build_fail_closed_on_new_material_conflicts": True,
        "future_build_fail_closed_on_missing_minute": True,
        "future_build_fail_closed_on_schema_mismatch": True,
        "future_build_fail_closed_on_symbol_mismatch": True,
        "future_output_pilot_pipeline_validation_only": True,
        "future_output_valid_for_research_backtest": False,
        "future_output_valid_for_edge_claim": False,
        "future_full_universe_or_broad_acquisition_ready": False,
        **future_counts,
        **shared,
    }
    approval_record = {
        "policy_clean_build_approval_record_created": True,
        "approval_scope": "NEXT_SEPARATE_10_SYMBOL_POLICY_CLEAN_BUILD_AFTER_SOL_EXACT_DUPLICATE_POLICY",
        "approval_grants_policy_now": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_10_symbol_policy_clean_build_next": True,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE_PASS,
        **shared,
    }
    self_validator = {
        "sol_exact_duplicate_policy_self_validator_created": True,
        "preflight_passed": True,
        "required_source_artifacts_exist": all(exists.values()),
        "required_source_artifacts_valid_json": all(valid.values()),
        "policy_matches_exact_duplicate_diagnostic": True,
        "drop_policy_confined_to_one_exact_duplicate_extra_row": True,
        "eth_material_policy_counts_preserved": True,
        "btc_policy_clean_reuse_required": True,
        "future_counts_match_expected": future_counts["nominal_total_pilot_output_rows"]
        == BTC_OUTPUT_ROWS + ETH_OUTPUT_ROWS + SOL_EXPECTED_OUTPUT_ROWS + REMAINING_7_OUTPUT_ROWS
        and future_counts["expected_total_complete_1h_rows_after_policy"]
        == BTC_COMPLETE_ROWS + ETH_COMPLETE_ROWS + SOL_EXPECTED_COMPLETE_ROWS + REMAINING_7_OUTPUT_ROWS
        and future_counts["expected_total_incomplete_1h_rows_after_policy"]
        == BTC_INCOMPLETE_ROWS + ETH_INCOMPLETE_ROWS + SOL_EXPECTED_INCOMPLETE_ROWS,
        "no_forbidden_actions_now": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_valid": NEXT_MODULE_PASS.endswith("policy_clean_build_execution_after_sol_exact_duplicate_policy_v1.py"),
    }
    replacement_checks = {
        "policy_created": shared["sol_exact_duplicate_policy_created"] is True,
        "duplicate_policy_valid": shared["duplicate_resolution_policy"] == DUPLICATE_RESOLUTION_POLICY,
        "target_symbol_sol": shared["target_symbol"] == TARGET_SYMBOL,
        "duplicate_open_time_valid": shared["duplicate_open_time"] == DUPLICATE_OPEN_TIME
        and shared["duplicate_open_time_utc"] == DUPLICATE_OPEN_TIME_UTC,
        "duplicate_source_valid": shared["duplicate_source_date"] == DUPLICATE_SOURCE_DATE
        and shared["duplicate_source_file"] == DUPLICATE_SOURCE_FILE,
        "drop_count_one": shared["exact_duplicate_extra_rows_to_drop"] == 1,
        "no_material_conflict": shared["material_conflict_present"] is False,
        "conflict_resolution_forbidden": shared["choose_conflicting_row_allowed"] is False
        and shared["average_conflicting_rows_allowed"] is False
        and shared["merge_conflicting_rows_allowed"] is False
        and shared["ohlcv_modification_allowed"] is False,
        "fill_forbidden": shared["synthetic_fill_allowed"] is False
        and shared["forward_fill_allowed"] is False
        and shared["backfill_allowed"] is False,
        "exact_drop_allowed": shared["exact_duplicate_drop_allowed"] is True,
        "preview_and_approval_created": shared["policy_clean_build_preview_created"] is True
        and shared["policy_clean_build_approval_record_created"] is True,
        "future_policy_chain_required": shared["btc_policy_clean_reuse_required"] is True
        and shared["eth_material_policy_required"] is True
        and shared["sol_exact_dedupe_required"] is True,
        "future_fail_closed": shared["future_build_must_fail_closed_on_new_material_conflicts"] is True,
        "future_counts_valid": self_validator["future_counts_match_expected"] is True,
        "approval_future_build_next_only": approval_record["approval_grants_policy_now"] is True
        and shared["approval_grants_future_10_symbol_policy_clean_build_next"] is True
        and shared["approval_grants_rebuild_now"] is False,
        "no_build_aggregation_output": shared["data_build_performed"] is False
        and shared["aggregation_performed_now"] is False
        and shared["output_csv_created"] is False,
        "not_research_backtest_edge_full_universe_broad": shared["output_valid_for_research_backtest"] is False
        and shared["output_valid_for_edge_claim"] is False
        and shared["safe_for_full_universe_acquisition"] is False
        and shared["broad_acquisition_ready"] is False,
        "p0_clear_p1_attention": shared["active_p0_blocker_count"] == 0
        and shared["active_p1_attention_count"] >= ACTIVE_P1_ATTENTION_COUNT,
        "next_module_valid": shared["next_module"] == NEXT_MODULE_PASS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_sol_exact_duplicate_policy_status": PASS_STATUS,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "tracked_python_count_at_policy_run": tracked_python_count(),
        **future_counts,
        **shared,
    }
    payloads = {
        "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy.json": policy,
        "historical_okx_10_symbol_pilot_sol_exact_duplicate_drop_policy.json": drop_policy,
        "historical_okx_10_symbol_pilot_policy_clean_build_preview_after_sol_policy.json": build_preview,
        "historical_okx_10_symbol_pilot_policy_clean_build_approval_record_after_sol_policy.json": approval_record,
        "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy_summary.json": summary,
        f"{MODULE_NAME}_latest.json": summary,
    }
    require(replacement_checks_all_true, f"replacement checks failed: {replacement_checks}")
    return summary, payloads


def validate_written_artifacts(summary: dict[str, Any]) -> dict[str, bool]:
    required_files = [
        "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy.json",
        "historical_okx_10_symbol_pilot_sol_exact_duplicate_drop_policy.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_preview_after_sol_policy.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_approval_record_after_sol_policy.json",
        "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy_self_validator.json",
        "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy_summary.json",
    ]
    loaded: dict[str, Any] = {}
    for filename in required_files:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing written artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))
    policy = loaded["historical_okx_10_symbol_pilot_sol_exact_duplicate_policy.json"]
    preview = loaded["historical_okx_10_symbol_pilot_policy_clean_build_preview_after_sol_policy.json"]
    approval = loaded[
        "historical_okx_10_symbol_pilot_policy_clean_build_approval_record_after_sol_policy.json"
    ]
    validator = loaded["historical_okx_10_symbol_pilot_sol_exact_duplicate_policy_self_validator.json"]
    checks = {
        "required_artifacts_exist": True,
        "policy_artifact_created": policy.get("sol_exact_duplicate_policy_created") is True,
        "drop_policy_valid": policy.get("exact_duplicate_extra_rows_to_drop") == 1
        and policy.get("exact_duplicate_drop_allowed") is True,
        "approval_exists_and_future_build_only": approval.get("policy_clean_build_approval_record_created") is True
        and approval.get("approval_grants_future_10_symbol_policy_clean_build_next") is True
        and approval.get("approval_grants_rebuild_now") is False,
        "preview_exists": preview.get("policy_clean_build_preview_created") is True,
        "validator_passed": validator.get("no_forbidden_actions_now") is True
        and validator.get("future_counts_match_expected") is True,
        "summary_replacement_checks_all_true": summary.get("replacement_checks_all_true") is True,
        "dangerous_flags_all_false": summary.get("dangerous_flags_all_false") is True,
        "next_module_valid": summary.get("next_module") == NEXT_MODULE_PASS,
    }
    checks["written_artifacts_valid"] = all(checks.values())
    return checks


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    artifacts = {label: load_json(path, label, exists, valid) for label, path in ARTIFACTS.items()}
    validate_prior_artifacts(artifacts)
    summary, payloads = build_payloads(generated_at, exists, valid)
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)
    written = validate_written_artifacts(summary)
    require(written["written_artifacts_valid"] is True, f"written artifact validation failed: {written}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except PolicyBlocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_sol_exact_duplicate_policy_status": BLOCKED_STATUS,
            "sol_exact_duplicate_policy_created": False,
            "duplicate_resolution_policy": DUPLICATE_RESOLUTION_POLICY,
            "target_symbol": TARGET_SYMBOL,
            "duplicate_open_time": DUPLICATE_OPEN_TIME,
            "duplicate_open_time_utc": DUPLICATE_OPEN_TIME_UTC,
            "duplicate_source_date": DUPLICATE_SOURCE_DATE,
            "duplicate_source_file": DUPLICATE_SOURCE_FILE,
            "exact_duplicate_extra_rows_to_drop": EXACT_DUPLICATE_EXTRA_ROWS_TO_DROP,
            "material_conflict_present": False,
            "choose_conflicting_row_allowed": False,
            "average_conflicting_rows_allowed": False,
            "merge_conflicting_rows_allowed": False,
            "ohlcv_modification_allowed": False,
            "exact_duplicate_drop_allowed": False,
            "policy_clean_build_preview_created": False,
            "policy_clean_build_approval_record_created": False,
            "btc_policy_clean_reuse_required": False,
            "eth_material_policy_required": False,
            "sol_exact_dedupe_required": False,
            "future_build_must_fail_closed_on_new_material_conflicts": True,
            "approval_grants_rebuild_now": False,
            "approval_grants_future_10_symbol_policy_clean_build_next": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_full_universe_acquisition": False,
            "broad_acquisition_ready": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "current_evidence_chain_quality_after_policy": PREVIOUS_STATUS,
            "next_module": NEXT_MODULE_BLOCKED,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy_summary.json", blocked)
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
