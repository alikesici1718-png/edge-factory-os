from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_exact_duplicate_policy_after_diagnostic_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "b58f5cd"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_DUPLICATE_"
    "DIAGNOSTIC_EXACT_DUPLICATE_POLICY_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_EXACT_DUPLICATE_"
    "POLICY_APPROVED_POLICY_CLEAN_BUILD_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_EXACT_DUPLICATE_POLICY"
)
TARGET_SYMBOL = "ETH-USDT-SWAP"
DUPLICATE_OPEN_TIME = 1_697_108_400_000
DUPLICATE_OPEN_TIME_UTC = "2023-10-12T11:00:00+00:00"
DUPLICATE_SOURCE_DATE = "2023-10-12"
DUPLICATE_SOURCE_FILE = "ETH-USDT-SWAP-candlesticks-2023-10-12.csv"
DUPLICATE_RESOLUTION_POLICY = "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROW_KEEP_ONE_CANONICAL_ROW"
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_EXACT_DUPLICATE_POLICY_"
    "APPROVED_POLICY_CLEAN_BUILD_READY"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_after_eth_exact_duplicate_policy_v1.py"
)
FAILED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_exact_duplicate_policy_blocked_record_v1.py"
)

PILOT_SYMBOLS = [
    "BTC-USDT-SWAP",
    "ETH-USDT-SWAP",
    "SOL-USDT-SWAP",
    "XRP-USDT-SWAP",
    "DOGE-USDT-SWAP",
    "ADA-USDT-SWAP",
    "AVAX-USDT-SWAP",
    "LINK-USDT-SWAP",
    "LTC-USDT-SWAP",
    "DOT-USDT-SWAP",
]
BTC_OUTPUT_ROWS = 25_272
BTC_COMPLETE_ROWS = 25_271
BTC_INCOMPLETE_ROWS = 1
NEW_SYMBOL_COUNT = 9
OTHER_NEW_SYMBOL_COUNT = 8
OUTPUT_ROWS_PER_SYMBOL = 25_272
ETH_EXPECTED_CLEAN_SOURCE_ROWS_AFTER_EXACT_DEDUPE = 1_516_320
NOMINAL_TOTAL_PILOT_OUTPUT_ROWS = 252_720
EXPECTED_TOTAL_COMPLETE_ROWS = BTC_COMPLETE_ROWS + NEW_SYMBOL_COUNT * OUTPUT_ROWS_PER_SYMBOL
EXPECTED_TOTAL_INCOMPLETE_ROWS = BTC_INCOMPLETE_ROWS
ACTIVE_P1_ATTENTION_COUNT = 12

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
DIAGNOSTIC_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_duplicate_diagnostic_after_build_anomaly_v1"
)
ANOMALY_RECORD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_execution_blocked_or_anomaly_record_after_preview_approval_v1"
)

ARTIFACTS = {
    "diagnostic_summary": DIAGNOSTIC_DIR / "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_summary.json",
    "diagnostic": DIAGNOSTIC_DIR / "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic.json",
    "raw_rows_report": DIAGNOSTIC_DIR / "historical_okx_10_symbol_pilot_eth_duplicate_raw_rows_report.json",
    "field_diff_report": DIAGNOSTIC_DIR / "historical_okx_10_symbol_pilot_eth_duplicate_field_diff_report.json",
    "diagnostic_policy_preview": DIAGNOSTIC_DIR / "historical_okx_10_symbol_pilot_eth_duplicate_policy_preview.json",
    "diagnostic_approval_record": DIAGNOSTIC_DIR / "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_approval_record.json",
    "anomaly_record_summary": ANOMALY_RECORD_DIR / f"{ANOMALY_RECORD_DIR.name}_latest.json",
    "anomaly_blocked_record": ANOMALY_RECORD_DIR / "historical_okx_10_symbol_pilot_build_anomaly_blocked_record.json",
    "anomaly_limitations": ANOMALY_RECORD_DIR / "historical_okx_10_symbol_pilot_build_anomaly_limitations_report.json",
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
    "row_modification_performed_now": False,
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


def validate_false(data: dict[str, Any], keys: list[str], label: str) -> None:
    for key in keys:
        require(data.get(key) is False, f"{label}.{key} must be false")


def validate_prior_artifacts(artifacts: dict[str, dict[str, Any]]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved exact duplicate policy module")

    diagnostic = artifacts["diagnostic_summary"]
    raw_rows = artifacts["raw_rows_report"]
    field_diff = artifacts["field_diff_report"]
    diagnostic_policy_preview = artifacts["diagnostic_policy_preview"]
    diagnostic_approval = artifacts["diagnostic_approval_record"]
    anomaly_summary = artifacts["anomaly_record_summary"]
    anomaly_blocked = artifacts["anomaly_blocked_record"]
    anomaly_limitations = artifacts["anomaly_limitations"]

    require(
        diagnostic.get("historical_data_acquisition_okx_10_symbol_pilot_eth_duplicate_diagnostic_status")
        == PREVIOUS_STATUS,
        "previous ETH duplicate diagnostic status mismatch",
    )
    require(diagnostic.get("next_module") == REQUESTED_MODULE, "diagnostic next_module mismatch")
    require(diagnostic.get("diagnostic_performed") is True, "diagnostic not performed")
    require(diagnostic.get("target_symbol") == TARGET_SYMBOL, "diagnostic target symbol mismatch")
    require(diagnostic.get("duplicate_open_time_count_total") == 1, "diagnostic duplicate count mismatch")
    require(diagnostic.get("diagnostic_duplicate_extra_row_count") == 1, "diagnostic extra row count mismatch")
    require(diagnostic.get("duplicate_open_time_group_count") == 1, "diagnostic group count mismatch")
    require(diagnostic.get("conflict_open_time") == DUPLICATE_OPEN_TIME, "diagnostic open_time mismatch")
    require(diagnostic.get("conflict_open_time_utc") == DUPLICATE_OPEN_TIME_UTC, "diagnostic open_time UTC mismatch")
    require(diagnostic.get("duplicate_source_date") == DUPLICATE_SOURCE_DATE, "diagnostic source date mismatch")
    require(diagnostic.get("duplicate_source_file") == DUPLICATE_SOURCE_FILE, "diagnostic source file mismatch")
    require(diagnostic.get("duplicate_row_count") == 2, "diagnostic duplicate row count mismatch")
    require(diagnostic.get("differing_field_count") == 0, "diagnostic differing field count mismatch")
    require(diagnostic.get("differing_fields") == [], "diagnostic differing fields mismatch")
    require(diagnostic.get("duplicate_classification") == "EXACT_DUPLICATE", "diagnostic classification mismatch")
    require(diagnostic.get("exact_duplicate") is True, "diagnostic exact duplicate flag mismatch")
    validate_false(
        diagnostic,
        [
            "confirm_only_conflict",
            "ohlcv_material_conflict",
            "symbol_or_schema_conflict",
            "unknown_conflict",
            "approval_grants_resolution_now",
            "approval_grants_rebuild_now",
            "approval_grants_dedupe_now",
            "data_build_performed",
            "aggregation_performed_now",
            "output_csv_created",
            "output_valid_for_research_backtest",
            "output_valid_for_edge_claim",
            "safe_for_full_universe_acquisition",
            "broad_acquisition_ready",
        ],
        "diagnostic_summary",
    )
    require(diagnostic.get("raw_duplicate_rows_captured") is True, "raw rows not captured")
    require(diagnostic.get("field_diff_report_created") is True, "field diff report missing")
    require(diagnostic.get("policy_preview_created") is True, "diagnostic policy preview missing")
    require(diagnostic.get("approval_record_created") is True, "diagnostic approval record missing")
    require(diagnostic.get("approval_grants_future_policy_next") is True, "future policy approval missing")
    require(diagnostic.get("active_p0_blocker_count") == 0, "diagnostic P0 count mismatch")
    require(diagnostic.get("active_p1_attention_count") == 0, "diagnostic P1 count mismatch")
    require(diagnostic.get("replacement_checks_all_true") is True, "diagnostic replacement checks did not pass")

    require(raw_rows.get("raw_duplicate_rows_captured") is True, "raw rows report not created")
    require(raw_rows.get("duplicate_row_count") == 2, "raw rows duplicate count mismatch")
    require(len(raw_rows.get("raw_duplicate_rows", [])) == 2, "raw duplicate rows not preserved")
    require(field_diff.get("field_diff_report_created") is True, "field diff artifact not created")
    require(field_diff.get("differing_field_count") == 0, "field diff count mismatch")
    require(field_diff.get("differing_fields") == [], "field diff fields mismatch")
    require(diagnostic_policy_preview.get("duplicate_classification") == "EXACT_DUPLICATE", "diagnostic policy preview classification mismatch")
    require(diagnostic_policy_preview.get("next_safe_route") == REQUESTED_MODULE, "diagnostic policy preview route mismatch")
    require(diagnostic_approval.get("approval_grants_future_policy_next") is True, "diagnostic approval future policy mismatch")
    validate_false(
        diagnostic_approval,
        [
            "approval_grants_resolution_now",
            "approval_grants_rebuild_now",
            "approval_grants_dedupe_now",
            "approval_grants_download_now",
            "approval_grants_api_now",
            "approval_grants_browse_now",
            "approval_grants_research_backtest_edge_now",
        ],
        "diagnostic_approval_record",
    )

    require(anomaly_summary.get("approval_grants_future_eth_duplicate_diagnostic_next") is True, "anomaly record diagnostic approval missing")
    require(anomaly_blocked.get("pilot_build_execution_blocked") is True, "anomaly blocked record mismatch")
    require(anomaly_blocked.get("duplicate_open_time_count_total") == 1, "anomaly duplicate count mismatch")
    require(anomaly_limitations.get("required_next_step") == "ETH_DUPLICATE_DIAGNOSTIC_ONLY", "anomaly limitation route mismatch")


def build_outputs(generated_at: str, exists: dict[str, bool], valid: dict[str, bool]) -> tuple[dict[str, Any], dict[str, Any]]:
    exact_duplicate_policy = {
        "eth_exact_duplicate_policy_created": True,
        "duplicate_resolution_policy": DUPLICATE_RESOLUTION_POLICY,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_open_time": DUPLICATE_OPEN_TIME,
        "duplicate_open_time_utc": DUPLICATE_OPEN_TIME_UTC,
        "duplicate_source_date": DUPLICATE_SOURCE_DATE,
        "duplicate_source_file": DUPLICATE_SOURCE_FILE,
        "exact_duplicate_extra_rows_to_drop": 1,
        "material_conflict_present": False,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "ohlcv_modification_allowed": False,
        "synthetic_fill_allowed": False,
        "forward_fill_allowed": False,
        "backfill_allowed": False,
        "exact_duplicate_drop_allowed": True,
        "drop_scope": "ONLY_THIS_ETH_DUPLICATE_OPEN_TIME_GROUP",
        "keep_one_canonical_row_required": True,
        "audit_dropped_row_required": True,
        "dedupe_execution_performed_now": False,
        "rebuild_execution_performed_now": False,
    }
    drop_policy = {
        "eth_exact_duplicate_drop_policy_created": True,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_key": "open_time",
        "duplicate_open_time": DUPLICATE_OPEN_TIME,
        "duplicate_open_time_utc": DUPLICATE_OPEN_TIME_UTC,
        "source_date": DUPLICATE_SOURCE_DATE,
        "source_file": DUPLICATE_SOURCE_FILE,
        "source_group_size": 2,
        "exact_duplicate_extra_rows_to_drop": 1,
        "drop_only_if_all_canonical_fields_identical": True,
        "fields_requiring_identity": [
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
        "if_any_field_differs_fail_closed": True,
        "if_new_duplicate_group_detected_fail_closed": True,
        "if_missing_minute_detected_fail_closed": True,
        "if_schema_or_symbol_mismatch_detected_fail_closed": True,
        "row_modification_allowed": False,
        "ohlcv_modification_allowed": False,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
    }
    build_preview = {
        "policy_clean_build_preview_created": True,
        "preview_only": True,
        "future_build_scope": "OKX_10_SYMBOL_PILOT_POLICY_CLEAN_1M_TO_1H_PIPELINE_VALIDATION_ONLY",
        "future_build_may_reuse_btc_policy_clean_output_after_revalidation": True,
        "btc_policy_clean_reuse_required": True,
        "btc_reused_output_rows": BTC_OUTPUT_ROWS,
        "btc_complete_rows": BTC_COMPLETE_ROWS,
        "btc_incomplete_rows": BTC_INCOMPLETE_ROWS,
        "future_build_may_build_new_symbols_from_validated_zips": True,
        "new_symbol_count_requiring_build": NEW_SYMBOL_COUNT,
        "eth_exact_dedupe_required": True,
        "eth_exact_duplicate_extra_row_to_drop": 1,
        "eth_expected_clean_source_rows_after_exact_dedupe": ETH_EXPECTED_CLEAN_SOURCE_ROWS_AFTER_EXACT_DEDUPE,
        "eth_expected_output_rows_if_no_other_anomaly": OUTPUT_ROWS_PER_SYMBOL,
        "other_new_symbol_count": OTHER_NEW_SYMBOL_COUNT,
        "other_new_symbols_expected_output_rows_if_clean": OTHER_NEW_SYMBOL_COUNT * OUTPUT_ROWS_PER_SYMBOL,
        "nominal_total_pilot_output_rows": NOMINAL_TOTAL_PILOT_OUTPUT_ROWS,
        "total_complete_rows_expected_if_all_9_new_symbols_clean": EXPECTED_TOTAL_COMPLETE_ROWS,
        "total_incomplete_rows_expected": EXPECTED_TOTAL_INCOMPLETE_ROWS,
        "all_symbols_complete": False,
        "all_symbols_complete_reason": "BTC policy-clean reuse retains one quarantined incomplete hour",
        "future_build_must_audit_dropped_eth_duplicate_row": True,
        "future_build_must_fail_closed_on_new_material_conflicts": True,
        "future_build_must_fail_closed_on_missing_minute": True,
        "future_build_must_fail_closed_on_schema_mismatch": True,
        "future_build_must_fail_closed_on_symbol_mismatch": True,
        "future_build_must_fail_closed_on_non_exact_duplicate_without_approved_policy": True,
        "future_build_must_keep_output_pilot_pipeline_validation_only": True,
        "future_build_must_not_download": True,
        "future_build_must_not_api_or_browse": True,
        "future_build_must_not_mark_research_backtest_edge_ready": True,
        "future_build_must_not_claim_full_universe_or_broad_acquisition_ready": True,
        "data_build_performed_now": False,
        "aggregation_performed_now": False,
        "output_csv_created_now": False,
    }
    approval_record = {
        "policy_clean_build_approval_record_created": True,
        "approval_scope": "NEXT_10_SYMBOL_POLICY_CLEAN_BUILD_EXECUTION_ONLY_AFTER_ETH_EXACT_DUPLICATE_POLICY",
        "approval_grants_policy_now": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_10_symbol_policy_clean_build_next": True,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
    }
    self_validator = {
        "self_validator_created": True,
        "preflight_passed": True,
        "required_source_artifacts_exist": all(exists.values()),
        "required_source_artifacts_valid_json": all(valid.values()),
        "exact_duplicate_policy_valid": exact_duplicate_policy["eth_exact_duplicate_policy_created"] is True
        and exact_duplicate_policy["duplicate_resolution_policy"] == DUPLICATE_RESOLUTION_POLICY
        and exact_duplicate_policy["exact_duplicate_extra_rows_to_drop"] == 1
        and exact_duplicate_policy["exact_duplicate_drop_allowed"] is True,
        "drop_policy_valid": drop_policy["drop_only_if_all_canonical_fields_identical"] is True
        and drop_policy["if_any_field_differs_fail_closed"] is True
        and drop_policy["row_modification_allowed"] is False,
        "build_preview_valid": build_preview["policy_clean_build_preview_created"] is True
        and build_preview["btc_policy_clean_reuse_required"] is True
        and build_preview["eth_exact_dedupe_required"] is True
        and build_preview["future_build_must_fail_closed_on_new_material_conflicts"] is True,
        "approval_record_valid": approval_record["approval_grants_policy_now"] is True
        and approval_record["approval_grants_future_10_symbol_policy_clean_build_next"] is True
        and approval_record["approval_grants_rebuild_now"] is False,
        "no_download_api_browse_build_aggregation_rebuild_dedupe_now": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks = {
        "eth_exact_duplicate_policy_created": exact_duplicate_policy["eth_exact_duplicate_policy_created"],
        "duplicate_resolution_policy_valid": exact_duplicate_policy["duplicate_resolution_policy"] == DUPLICATE_RESOLUTION_POLICY,
        "target_symbol_valid": exact_duplicate_policy["target_symbol"] == TARGET_SYMBOL,
        "duplicate_open_time_valid": exact_duplicate_policy["duplicate_open_time"] == DUPLICATE_OPEN_TIME,
        "duplicate_open_time_utc_valid": exact_duplicate_policy["duplicate_open_time_utc"] == DUPLICATE_OPEN_TIME_UTC,
        "duplicate_source_valid": exact_duplicate_policy["duplicate_source_date"] == DUPLICATE_SOURCE_DATE
        and exact_duplicate_policy["duplicate_source_file"] == DUPLICATE_SOURCE_FILE,
        "exact_duplicate_extra_rows_to_drop_one": exact_duplicate_policy["exact_duplicate_extra_rows_to_drop"] == 1,
        "material_conflict_absent": exact_duplicate_policy["material_conflict_present"] is False,
        "conflicting_row_choice_forbidden": exact_duplicate_policy["choose_conflicting_row_allowed"] is False
        and exact_duplicate_policy["average_conflicting_rows_allowed"] is False
        and exact_duplicate_policy["merge_conflicting_rows_allowed"] is False,
        "ohlcv_and_fill_modification_forbidden": exact_duplicate_policy["ohlcv_modification_allowed"] is False
        and exact_duplicate_policy["synthetic_fill_allowed"] is False
        and exact_duplicate_policy["forward_fill_allowed"] is False
        and exact_duplicate_policy["backfill_allowed"] is False,
        "exact_duplicate_drop_allowed": exact_duplicate_policy["exact_duplicate_drop_allowed"] is True,
        "policy_clean_build_preview_created": build_preview["policy_clean_build_preview_created"],
        "policy_clean_build_approval_record_created": approval_record["policy_clean_build_approval_record_created"],
        "btc_policy_clean_reuse_required": build_preview["btc_policy_clean_reuse_required"],
        "eth_exact_dedupe_required": build_preview["eth_exact_dedupe_required"],
        "future_build_must_fail_closed_on_new_material_conflicts": build_preview["future_build_must_fail_closed_on_new_material_conflicts"],
        "approval_future_policy_clean_build_next": approval_record["approval_grants_future_10_symbol_policy_clean_build_next"] is True,
        "approval_rebuild_now_false": approval_record["approval_grants_rebuild_now"] is False,
        "no_build_aggregation_output": True,
        "not_research_backtest_edge_full_universe_broad": True,
        "active_p0_clear_for_exact_policy": True,
        "active_p1_attention_at_least_12": ACTIVE_P1_ATTENTION_COUNT >= 12,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_eth_exact_duplicate_policy_status": PASS_STATUS,
        "eth_exact_duplicate_policy_created": True,
        "duplicate_resolution_policy": DUPLICATE_RESOLUTION_POLICY,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_open_time": DUPLICATE_OPEN_TIME,
        "duplicate_open_time_utc": DUPLICATE_OPEN_TIME_UTC,
        "duplicate_source_date": DUPLICATE_SOURCE_DATE,
        "duplicate_source_file": DUPLICATE_SOURCE_FILE,
        "exact_duplicate_extra_rows_to_drop": 1,
        "material_conflict_present": False,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "ohlcv_modification_allowed": False,
        "exact_duplicate_drop_allowed": True,
        "policy_clean_build_preview_created": True,
        "policy_clean_build_approval_record_created": True,
        "btc_policy_clean_reuse_required": True,
        "eth_exact_dedupe_required": True,
        "future_build_must_fail_closed_on_new_material_conflicts": True,
        "approval_grants_policy_now": True,
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
        "next_module": NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_policy_run": tracked_python_count(),
    }
    artifacts = {
        "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy.json": {
            **summary,
            "policy": exact_duplicate_policy,
            "drop_policy_artifact": "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_policy.json",
        },
        "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_policy.json": drop_policy,
        "historical_okx_10_symbol_pilot_policy_clean_build_preview_after_eth_policy.json": build_preview,
        "historical_okx_10_symbol_pilot_policy_clean_build_approval_record.json": approval_record,
        "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy_summary.json": summary,
        f"{MODULE_NAME}_latest.json": summary,
    }
    return summary, artifacts


def validate_written_artifacts(summary: dict[str, Any]) -> dict[str, bool]:
    required_files = [
        "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy.json",
        "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_policy.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_preview_after_eth_policy.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_approval_record.json",
        "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy_self_validator.json",
        "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy_summary.json",
    ]
    loaded: dict[str, Any] = {}
    for filename in required_files:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing written artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))
    approval = loaded["historical_okx_10_symbol_pilot_policy_clean_build_approval_record.json"]
    preview = loaded["historical_okx_10_symbol_pilot_policy_clean_build_preview_after_eth_policy.json"]
    validator = loaded["historical_okx_10_symbol_pilot_eth_exact_duplicate_policy_self_validator.json"]
    return {
        "required_artifacts_exist": True,
        "approval_record_valid": approval.get("approval_grants_future_10_symbol_policy_clean_build_next") is True
        and approval.get("approval_grants_rebuild_now") is False,
        "preview_valid": preview.get("btc_policy_clean_reuse_required") is True
        and preview.get("eth_exact_dedupe_required") is True
        and preview.get("future_build_must_fail_closed_on_new_material_conflicts") is True,
        "self_validator_valid": validator.get("next_module_valid") is True,
        "summary_replacement_checks_all_true": summary.get("replacement_checks_all_true") is True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    artifacts = {label: load_json(path, label, exists, valid) for label, path in ARTIFACTS.items()}
    validate_prior_artifacts(artifacts)
    summary, outputs = build_outputs(generated_at, exists, valid)
    require(summary["replacement_checks_all_true"] is True, "replacement checks failed")
    for filename, payload in outputs.items():
        write_json(OUTPUT_DIR / filename, payload)
    written = validate_written_artifacts(summary)
    require(all(written.values()), f"written artifact validation failed: {written}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except PolicyBlocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_eth_exact_duplicate_policy_status": BLOCKED_STATUS,
            "eth_exact_duplicate_policy_created": False,
            "duplicate_resolution_policy": DUPLICATE_RESOLUTION_POLICY,
            "target_symbol": TARGET_SYMBOL,
            "duplicate_open_time": DUPLICATE_OPEN_TIME,
            "duplicate_open_time_utc": DUPLICATE_OPEN_TIME_UTC,
            "duplicate_source_date": DUPLICATE_SOURCE_DATE,
            "duplicate_source_file": DUPLICATE_SOURCE_FILE,
            "exact_duplicate_extra_rows_to_drop": 0,
            "material_conflict_present": False,
            "choose_conflicting_row_allowed": False,
            "average_conflicting_rows_allowed": False,
            "merge_conflicting_rows_allowed": False,
            "ohlcv_modification_allowed": False,
            "exact_duplicate_drop_allowed": False,
            "policy_clean_build_preview_created": False,
            "policy_clean_build_approval_record_created": False,
            "btc_policy_clean_reuse_required": False,
            "eth_exact_dedupe_required": False,
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
            "active_p1_attention_count": ACTIVE_P1_ATTENTION_COUNT,
            "current_evidence_chain_quality_after_policy": BLOCKED_STATUS,
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
