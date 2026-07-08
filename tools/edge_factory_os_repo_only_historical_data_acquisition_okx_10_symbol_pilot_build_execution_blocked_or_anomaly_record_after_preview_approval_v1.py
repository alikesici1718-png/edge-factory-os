from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_execution_blocked_or_anomaly_record_after_preview_approval_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "f29e0e7"
PREVIOUS_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_EXECUTION_ANOMALY"
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_ANOMALY_RECORD_"
    "ETH_DUPLICATE_DIAGNOSTIC_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_ANOMALY_RECORD_"
    "FAILED_REVIEW"
)
BLOCK_REASON = "NEW_SYMBOL_DUPLICATE_OPEN_TIME_ROWS"
ANOMALY_SYMBOL = "ETH-USDT-SWAP"
ANOMALY_OPEN_TIME_MS = 1_697_108_400_000
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_BLOCKED_"
    "ETH_DUPLICATE_DIAGNOSTIC_READY"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_duplicate_diagnostic_after_build_anomaly_v1.py"
)
FAILED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_anomaly_record_failed_review_v1.py"
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
DATE_RANGE_START = "2023-07-01"
DATE_RANGE_END = "2026-05-18"
EXPECTED_TOTAL_PILOT_FILE_COUNT = 10_530
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_NEW_SYMBOL_FILE_COUNT = 9_477
EXPECTED_REUSED_BTC_FILE_COUNT = 1_053
NOMINAL_TOTAL_SOURCE_ROWS = 15_163_200
NOMINAL_TOTAL_PILOT_OUTPUT_ROWS = 252_720
ACTIVE_P1_ATTENTION_COUNT = 0

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
BUILD_EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_execution_after_preview_approval_v1"
)
BUILD_PREVIEW_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_preview_after_download_validator_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)

ARTIFACTS = {
    "build_execution_summary": BUILD_EXECUTION_DIR / "historical_okx_10_symbol_pilot_build_execution_summary.json",
    "build_execution_report": BUILD_EXECUTION_DIR / "historical_okx_10_symbol_pilot_build_execution_report.json",
    "gap_duplicate_report": BUILD_EXECUTION_DIR / "historical_okx_10_symbol_pilot_gap_duplicate_report.json",
    "schema_validation_report": BUILD_EXECUTION_DIR / "historical_okx_10_symbol_pilot_schema_validation_report.json",
    "output_manifest": BUILD_EXECUTION_DIR / "historical_okx_10_symbol_pilot_1m_to_1h_output_manifest.json",
    "output_provenance_report": BUILD_EXECUTION_DIR / "historical_okx_10_symbol_pilot_output_provenance_report.json",
    "build_compliance_report": BUILD_EXECUTION_DIR / "historical_okx_10_symbol_pilot_build_execution_compliance_report.json",
    "build_preview_summary": BUILD_PREVIEW_DIR / f"{BUILD_PREVIEW_DIR.name}_latest.json",
    "build_preview": BUILD_PREVIEW_DIR / "historical_okx_10_symbol_pilot_build_preview.json",
    "build_approval_record": BUILD_PREVIEW_DIR / "historical_okx_10_symbol_pilot_build_approval_record.json",
    "download_validator_summary": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json",
    "download_hash_validation_report": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_hash_validation_report.json",
}

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "full_csv_read_performed_now": False,
    "new_data_build_performed_now": False,
    "aggregation_performed_now": False,
    "output_1h_csv_created_now": False,
    "output_manifest_created_now": False,
    "dedupe_execution_performed_now": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_edge_claim_made": False,
    "full_universe_ready_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class Blocked(RuntimeError):
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
        raise Blocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> dict[str, Any]:
    exists[label] = path.exists()
    require(path.exists(), f"missing artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise Blocked(f"invalid JSON artifact {label}: {exc}") from exc
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
    require(repo_has_only_this_tool_change(), "repo dirty outside approved anomaly record module")

    summary = artifacts["build_execution_summary"]
    report = artifacts["build_execution_report"]
    gap = artifacts["gap_duplicate_report"]
    schema = artifacts["schema_validation_report"]
    manifest = artifacts["output_manifest"]
    provenance = artifacts["output_provenance_report"]
    compliance = artifacts["build_compliance_report"]
    preview_summary = artifacts["build_preview_summary"]
    preview = artifacts["build_preview"]
    approval = artifacts["build_approval_record"]
    download_summary = artifacts["download_validator_summary"]
    hash_report = artifacts["download_hash_validation_report"]

    require(
        summary.get("historical_data_acquisition_okx_10_symbol_pilot_build_execution_status") == PREVIOUS_STATUS,
        "prior build execution status mismatch",
    )
    require(report.get("historical_data_acquisition_okx_10_symbol_pilot_build_execution_status") == PREVIOUS_STATUS, "prior execution report status mismatch")
    require(summary.get("next_module") == REQUESTED_MODULE, "prior build next_module mismatch")
    require(summary.get("build_execution_performed") is False, "prior blocked build unexpectedly marked performed")
    require(summary.get("pilot_symbol_count") == len(PILOT_SYMBOLS), "pilot symbol count mismatch")
    require(summary.get("pilot_symbols") == PILOT_SYMBOLS, "pilot symbols mismatch")
    require(summary.get("date_range_start") == DATE_RANGE_START, "date range start mismatch")
    require(summary.get("date_range_end") == DATE_RANGE_END, "date range end mismatch")
    require(summary.get("file_count_total") == EXPECTED_TOTAL_PILOT_FILE_COUNT, "pilot file count mismatch")
    require(summary.get("btc_reused_file_count") == EXPECTED_REUSED_BTC_FILE_COUNT, "BTC reused file count mismatch")
    require(summary.get("new_symbol_file_count") == EXPECTED_NEW_SYMBOL_FILE_COUNT, "new symbol file count mismatch")
    require(summary.get("nominal_total_source_rows") == NOMINAL_TOTAL_SOURCE_ROWS, "nominal source row count mismatch")
    require(summary.get("nominal_total_pilot_output_rows") == NOMINAL_TOTAL_PILOT_OUTPUT_ROWS, "nominal output row count mismatch")
    require(summary.get("new_symbol_anomaly_detected") is True, "new symbol anomaly flag mismatch")
    require(summary.get("anomaly_symbol_count") == 1, "anomaly symbol count mismatch")
    require(summary.get("anomaly_symbols") == [ANOMALY_SYMBOL], "anomaly symbols mismatch")
    require(summary.get("duplicate_open_time_count_total") == 1, "duplicate open_time count mismatch")
    require(summary.get("missing_minute_count_total") == 0, "missing minute count mismatch")
    require(summary.get("schema_mismatch_count") == 0, "schema mismatch count mismatch")
    require(summary.get("symbol_mismatch_count") == 0, "symbol mismatch count mismatch")
    require(summary.get("output_csv_created") is False, "prior output CSV unexpectedly created")
    require(summary.get("output_manifest_created") is False, "prior output manifest unexpectedly created")
    require(summary.get("data_build_performed") is False, "prior data build unexpectedly performed")
    require(summary.get("aggregation_performed_now") is False, "prior aggregation unexpectedly performed")
    require(summary.get("output_valid_for_research_backtest") is False, "research/backtest readiness claim detected")
    require(summary.get("output_valid_for_edge_claim") is False, "edge readiness claim detected")
    require(summary.get("safe_for_full_universe_acquisition") is False, "full universe readiness claim detected")
    require(summary.get("broad_acquisition_ready") is False, "broad acquisition readiness claim detected")
    require(summary.get("active_p0_blocker_count") == 1, "prior P0 count mismatch")
    require(summary.get("replacement_checks_all_true") is False, "prior blocked anomaly unexpectedly had all checks true")
    require(str(summary.get("blocked_reason", "")).startswith(f"{ANOMALY_SYMBOL} duplicate"), "prior blocked reason does not identify ETH duplicate")

    require(gap.get("gap_duplicate_report_created") is True, "gap duplicate report not created")
    require(gap.get("anomaly_symbols") == [ANOMALY_SYMBOL], "gap anomaly symbols mismatch")
    require(gap.get("duplicate_open_time_count_total") == 1, "gap duplicate count mismatch")
    require(gap.get("missing_minute_count_total") == 0, "gap missing minute count mismatch")
    require(schema.get("schema_validation_report_created") is True, "schema validation report not created")
    require(schema.get("schema_mismatch_count") == 0, "schema report mismatch count mismatch")
    require(schema.get("symbol_mismatch_count") == 0, "schema report symbol mismatch count mismatch")
    require(manifest.get("output_manifest_created") is False, "blocked manifest unexpectedly created")
    require(manifest.get("blocked_before_complete_manifest") is True, "manifest did not preserve blocked state")
    require(manifest.get("anomaly_symbols") == [ANOMALY_SYMBOL], "manifest anomaly symbols mismatch")
    require(provenance.get("output_provenance_report_created") is True, "provenance report not created")
    require(provenance.get("btc_policy_clean_reused") is True, "BTC policy clean reuse missing")
    require(provenance.get("btc_policy_clean_revalidated") is True, "BTC policy clean revalidation missing")
    require(compliance.get("compliance_report_created") is True, "compliance report not created")
    require(compliance.get("no_new_download") is True, "prior compliance no_new_download mismatch")
    require(compliance.get("generic_runner_implementation_remains_blocked") is True, "generic runner block missing")
    validate_false(
        compliance,
        [
            "new_download_performed_now",
            "okx_api_call_performed",
            "okx_browse_performed",
            "output_valid_for_research_backtest",
            "output_valid_for_edge_claim",
            "safe_for_full_universe_acquisition",
            "broad_acquisition_ready",
            "schema_or_config_created",
        ],
        "build_compliance_report",
    )

    require(preview_summary.get("historical_data_acquisition_okx_10_symbol_pilot_build_preview_status") is not None, "build preview status missing")
    require(preview_summary.get("replacement_checks_all_true") is True, "build preview replacement checks did not pass")
    require(preview.get("preview_created") is True, "build preview artifact not created")
    require(preview.get("approval_grants_future_10_symbol_build_next") is True, "build preview future build approval missing")
    require(preview.get("future_build_must_revalidate_sha256_before_each_csv_read") is True, "build preview SHA revalidation rule missing")
    require(preview.get("future_build_must_not_download") is True, "build preview download ban missing")
    require(preview.get("future_build_must_not_api_or_browse") is True, "build preview API/browse ban missing")
    require(approval.get("approval_record_created") is True, "build approval record not created")
    require(approval.get("approval_grants_future_10_symbol_build_next") is True, "build approval did not grant next build")
    validate_false(
        approval,
        [
            "approval_grants_build_now",
            "approval_grants_download_now",
            "approval_grants_api_now",
            "approval_grants_browse_now",
            "approval_grants_aggregation_now",
            "approval_grants_full_csv_read_now",
            "approval_grants_full_universe_acquisition",
            "approval_grants_research_backtest_edge",
        ],
        "build_approval_record",
    )

    require(
        download_summary.get("historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_status")
        == "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_VALIDATED_BUILD_PREVIEW_READY_NO_BUILD_NO_AGGREGATION",
        "download validator status mismatch",
    )
    require(download_summary.get("replacement_checks_all_true") is True, "download validator replacement checks did not pass")
    require(download_summary.get("all_hashes_match_recorded") is True, "download hash summary mismatch")
    require(hash_report.get("all_hashes_match_recorded") is True, "download hash report mismatch")


def build_payloads(generated_at: str, exists: dict[str, bool], valid: dict[str, bool]) -> tuple[dict[str, Any], dict[str, Any]]:
    source_summary_path = ARTIFACTS["build_execution_summary"]
    blocked_record = {
        "anomaly_blocked_record_created": True,
        "pilot_build_execution_blocked": True,
        "block_reason": BLOCK_REASON,
        "source_status": PREVIOUS_STATUS,
        "source_build_execution_summary_artifact": str(source_summary_path),
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "anomaly_symbol_count": 1,
        "anomaly_symbols": [ANOMALY_SYMBOL],
        "anomaly_symbol": ANOMALY_SYMBOL,
        "duplicate_open_time_count_total": 1,
        "known_duplicate_open_time_epoch_ms": ANOMALY_OPEN_TIME_MS,
        "missing_minute_count_total": 0,
        "schema_mismatch_count": 0,
        "symbol_mismatch_count": 0,
        "output_csv_created": False,
        "output_manifest_created": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 1,
        "p0_remains_active_until_eth_duplicate_diagnostic_resolves_it": True,
        "new_download_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "full_csv_read_performed_now": False,
        "dedupe_execution_performed_now": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
    }
    diagnostic_preview = {
        "eth_duplicate_diagnostic_preview_created": True,
        "preview_only": True,
        "diagnostic_execution_performed_now": False,
        "target_symbol": ANOMALY_SYMBOL,
        "known_duplicate_open_time_epoch_ms": ANOMALY_OPEN_TIME_MS,
        "duplicate_open_time_count_total": 1,
        "future_diagnostic_module_may_read_only_eth_usdt_swap_already_validated_zip_csv_files": True,
        "future_diagnostic_module_must_reconfirm_sha256_before_reading": True,
        "future_diagnostic_module_may_locate_duplicate_open_time_group": True,
        "future_diagnostic_module_may_record_raw_duplicate_rows_and_differing_fields": True,
        "future_diagnostic_module_may_create_next_policy_route_based_on_classification": True,
        "classification_options": [
            "A_EXACT_DUPLICATE_ROW",
            "B_CONFIRM_ONLY_CONFLICT",
            "C_OHLC_VOLUME_OHLCV_MATERIAL_CONFLICT",
            "D_UNKNOWN_UNINSPECTABLE",
        ],
        "classification_policy": {
            "A_EXACT_DUPLICATE_ROW": "same open_time and identical row values across all recorded fields",
            "B_CONFIRM_ONLY_CONFLICT": "same open_time with confirm differing and OHLCV/volume fields identical",
            "C_OHLC_VOLUME_OHLCV_MATERIAL_CONFLICT": "same open_time with any OHLC, volume, vol_ccy, or vol_quote conflict",
            "D_UNKNOWN_UNINSPECTABLE": "duplicate group cannot be inspected or classified from approved local evidence",
        },
        "future_diagnostic_module_must_not_download": True,
        "future_diagnostic_module_must_not_call_api_or_browse": True,
        "future_diagnostic_module_must_not_build_or_aggregate": True,
        "future_diagnostic_module_must_not_dedupe_or_rebuild": True,
        "future_diagnostic_module_must_not_select_conflicting_row": True,
        "future_diagnostic_module_must_not_mark_research_backtest_edge_ready": True,
        "download_allowed": False,
        "api_allowed": False,
        "browse_allowed": False,
        "build_or_aggregation_performed_now": False,
        "dedupe_or_rebuild_performed_now": False,
    }
    approval_record = {
        "eth_duplicate_diagnostic_approval_record_created": True,
        "approval_scope": "NEXT_ETH_DUPLICATE_DIAGNOSTIC_ONLY_AFTER_10_SYMBOL_PILOT_BUILD_ANOMALY",
        "approval_grants_diagnostic_now": False,
        "approval_grants_future_eth_duplicate_diagnostic_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
    }
    limitations_report = {
        "build_anomaly_limitations_report_created": True,
        "pilot_build_execution_blocked": True,
        "completed_10_symbol_1h_output_exists": False,
        "output_csv_created": False,
        "output_manifest_created": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "dedupe_execution_performed_now": False,
        "pipeline_output_valid_for_research_backtest": False,
        "pipeline_output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "known_p0_blocker": BLOCK_REASON,
        "anomaly_symbol": ANOMALY_SYMBOL,
        "duplicate_open_time_count_total": 1,
        "required_next_step": "ETH_DUPLICATE_DIAGNOSTIC_ONLY",
        "download_api_browse_forbidden": True,
        "new_build_aggregation_forbidden_in_this_module": True,
        "dedupe_rebuild_forbidden_in_this_module": True,
        "research_backtest_edge_claim_forbidden": True,
    }
    self_validator = {
        "self_validator_created": True,
        "preflight_passed": True,
        "required_source_artifacts_exist": all(exists.values()),
        "required_source_artifacts_valid_json": all(valid.values()),
        "anomaly_blocked_record_valid": blocked_record["pilot_build_execution_blocked"] is True
        and blocked_record["block_reason"] == BLOCK_REASON
        and blocked_record["anomaly_symbols"] == [ANOMALY_SYMBOL]
        and blocked_record["duplicate_open_time_count_total"] == 1,
        "eth_duplicate_diagnostic_preview_valid": diagnostic_preview["eth_duplicate_diagnostic_preview_created"] is True
        and diagnostic_preview["diagnostic_execution_performed_now"] is False
        and diagnostic_preview["future_diagnostic_module_must_not_dedupe_or_rebuild"] is True,
        "eth_duplicate_diagnostic_approval_record_valid": approval_record["approval_grants_future_eth_duplicate_diagnostic_next"] is True
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_dedupe_now"] is False
        and approval_record["approval_grants_download_now"] is False
        and approval_record["approval_grants_research_backtest_edge_now"] is False,
        "no_download_api_browse_build_aggregation_dedupe_now": all(value is False for value in DANGEROUS_FLAGS.values()),
        "p0_remains_active": blocked_record["active_p0_blocker_count"] == 1,
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks = {
        "preflight_passed": True,
        "anomaly_blocked_record_created": blocked_record["anomaly_blocked_record_created"],
        "eth_duplicate_diagnostic_preview_created": diagnostic_preview["eth_duplicate_diagnostic_preview_created"],
        "eth_duplicate_diagnostic_approval_record_created": approval_record["eth_duplicate_diagnostic_approval_record_created"],
        "pilot_build_execution_blocked": blocked_record["pilot_build_execution_blocked"],
        "block_reason_valid": blocked_record["block_reason"] == BLOCK_REASON,
        "anomaly_symbol_count_one": blocked_record["anomaly_symbol_count"] == 1,
        "anomaly_symbols_eth": blocked_record["anomaly_symbols"] == [ANOMALY_SYMBOL],
        "duplicate_open_time_count_total_one": blocked_record["duplicate_open_time_count_total"] == 1,
        "missing_minutes_zero": blocked_record["missing_minute_count_total"] == 0,
        "schema_symbol_mismatch_zero": blocked_record["schema_mismatch_count"] == 0 and blocked_record["symbol_mismatch_count"] == 0,
        "no_output_csv_or_manifest": blocked_record["output_csv_created"] is False and blocked_record["output_manifest_created"] is False,
        "no_build_aggregation": blocked_record["data_build_performed"] is False and blocked_record["aggregation_performed_now"] is False,
        "approval_future_eth_duplicate_diagnostic_next": approval_record["approval_grants_future_eth_duplicate_diagnostic_next"] is True,
        "approval_rebuild_now_false": approval_record["approval_grants_rebuild_now"] is False,
        "approval_dedupe_now_false": approval_record["approval_grants_dedupe_now"] is False,
        "approval_download_api_browse_now_false": approval_record["approval_grants_download_now"] is False
        and approval_record["approval_grants_api_now"] is False
        and approval_record["approval_grants_browse_now"] is False,
        "not_research_backtest_edge_full_universe_broad": blocked_record["output_valid_for_research_backtest"] is False
        and blocked_record["output_valid_for_edge_claim"] is False
        and blocked_record["safe_for_full_universe_acquisition"] is False
        and blocked_record["broad_acquisition_ready"] is False,
        "p0_active": blocked_record["active_p0_blocker_count"] == 1,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_build_anomaly_record_status": PASS_STATUS,
        "anomaly_blocked_record_created": True,
        "eth_duplicate_diagnostic_preview_created": True,
        "eth_duplicate_diagnostic_approval_record_created": True,
        "pilot_build_execution_blocked": True,
        "block_reason": BLOCK_REASON,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "anomaly_symbol_count": 1,
        "anomaly_symbols": [ANOMALY_SYMBOL],
        "anomaly_symbol": ANOMALY_SYMBOL,
        "duplicate_open_time_count_total": 1,
        "missing_minute_count_total": 0,
        "schema_mismatch_count": 0,
        "symbol_mismatch_count": 0,
        "output_csv_created": False,
        "output_manifest_created": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "approval_grants_future_eth_duplicate_diagnostic_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": ACTIVE_P1_ATTENTION_COUNT,
        "current_evidence_chain_quality_after_anomaly_record": AFTER_QUALITY,
        "next_module": NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_anomaly_record_run": tracked_python_count(),
    }
    bundle = {
        "anomaly_blocked_record": blocked_record,
        "eth_duplicate_diagnostic_preview": diagnostic_preview,
        "eth_duplicate_diagnostic_approval_record": approval_record,
        "limitations_report": limitations_report,
        "self_validator": self_validator,
        "summary": summary_payload,
    }
    payloads = {
        "historical_okx_10_symbol_pilot_build_anomaly_blocked_record.json": blocked_record,
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_preview.json": diagnostic_preview,
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_approval_record.json": approval_record,
        "historical_okx_10_symbol_pilot_build_anomaly_limitations_report.json": limitations_report,
        "historical_okx_10_symbol_pilot_build_anomaly_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_build_anomaly_bundle_summary.json": bundle,
        f"{MODULE_NAME}_latest.json": summary_payload,
    }
    return summary_payload, payloads


def validate_written_artifacts(summary_payload: dict[str, Any]) -> dict[str, Any]:
    required_files = [
        "historical_okx_10_symbol_pilot_build_anomaly_blocked_record.json",
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_preview.json",
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_approval_record.json",
        "historical_okx_10_symbol_pilot_build_anomaly_limitations_report.json",
        "historical_okx_10_symbol_pilot_build_anomaly_self_validator.json",
        "historical_okx_10_symbol_pilot_build_anomaly_bundle_summary.json",
    ]
    loaded: dict[str, Any] = {}
    for filename in required_files:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing written artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))

    blocked = loaded["historical_okx_10_symbol_pilot_build_anomaly_blocked_record.json"]
    preview = loaded["historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_preview.json"]
    approval = loaded["historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_approval_record.json"]
    validator = loaded["historical_okx_10_symbol_pilot_build_anomaly_self_validator.json"]
    checks = {
        "required_artifacts_exist": True,
        "blocked_record_preserves_blocked_state": blocked.get("pilot_build_execution_blocked") is True
        and blocked.get("block_reason") == BLOCK_REASON,
        "eth_preview_created_without_execution": preview.get("eth_duplicate_diagnostic_preview_created") is True
        and preview.get("diagnostic_execution_performed_now") is False,
        "approval_grants_only_future_diagnostic": approval.get("approval_grants_future_eth_duplicate_diagnostic_next") is True
        and approval.get("approval_grants_diagnostic_now") is False
        and approval.get("approval_grants_rebuild_now") is False
        and approval.get("approval_grants_dedupe_now") is False,
        "self_validator_allows_next_module": validator.get("next_module_valid") is True,
        "summary_replacement_checks_all_true": summary_payload.get("replacement_checks_all_true") is True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    checks["written_artifacts_valid"] = all(checks.values())
    return checks


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    artifacts = {label: load_json(path, label, exists, valid) for label, path in ARTIFACTS.items()}
    validate_prior_artifacts(artifacts)
    summary_payload, payloads = build_payloads(generated_at, exists, valid)
    require(summary_payload["replacement_checks_all_true"] is True, "replacement checks failed")
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)
    written = validate_written_artifacts(summary_payload)
    require(written["written_artifacts_valid"] is True, f"written artifact validation failed: {written}")
    print(json.dumps(summary_payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked_payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_build_anomaly_record_status": BLOCKED_STATUS,
            "anomaly_blocked_record_created": False,
            "eth_duplicate_diagnostic_preview_created": False,
            "eth_duplicate_diagnostic_approval_record_created": False,
            "pilot_build_execution_blocked": True,
            "block_reason": BLOCK_REASON,
            "anomaly_symbol_count": 1,
            "anomaly_symbols": [ANOMALY_SYMBOL],
            "duplicate_open_time_count_total": 1,
            "missing_minute_count_total": 0,
            "schema_mismatch_count": 0,
            "symbol_mismatch_count": 0,
            "output_csv_created": False,
            "output_manifest_created": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "approval_grants_future_eth_duplicate_diagnostic_next": False,
            "approval_grants_rebuild_now": False,
            "approval_grants_dedupe_now": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_full_universe_acquisition": False,
            "broad_acquisition_ready": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": ACTIVE_P1_ATTENTION_COUNT,
            "current_evidence_chain_quality_after_anomaly_record": PREVIOUS_STATUS,
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked_payload)
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
