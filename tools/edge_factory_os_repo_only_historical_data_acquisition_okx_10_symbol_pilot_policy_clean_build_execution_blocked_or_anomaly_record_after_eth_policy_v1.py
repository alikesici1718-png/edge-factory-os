from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_eth_policy_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "6ff92a8"
PREVIOUS_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "EXECUTION_ANOMALY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "ANOMALY_RECORD_ETH_POLICY_APPLICATION_RESIDUAL_DUPLICATE_DIAGNOSTIC_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "ANOMALY_RECORD_FAILED_REVIEW"
)
BLOCK_REASON = (
    "ETH_RESIDUAL_DUPLICATE_AFTER_EXACT_DUPLICATE_POLICY_OR_POLICY_APPLICATION_"
    "COUNT_MISMATCH"
)
ANOMALY_SYMBOL = "ETH-USDT-SWAP"
EXPECTED_ETH_EXACT_DUPLICATE_ROWS_DROPPED = 1
EXPECTED_RESIDUAL_DUPLICATE_OPEN_TIME_COUNT_TOTAL = 1
EXPECTED_OBSERVED_NEW_SYMBOL_SOURCE_ROWS_BEFORE_POLICY = 149_464
EXPECTED_CLEAN_NEW_SYMBOL_SOURCE_ROWS_AFTER_POLICY = 149_462
EXPECTED_CLEAN_SOURCE_ROW_DELTA_FOR_ONE_EXACT_DROP = 1
EXPECTED_OBSERVED_CLEAN_SOURCE_ROW_DELTA = 2
ACTIVE_P1_ATTENTION_COUNT = 0
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_BLOCKED_"
    "ETH_POLICY_APPLICATION_RESIDUAL_DUPLICATE_DIAGNOSTIC_READY"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_policy_application_residual_duplicate_diagnostic_after_build_block_v1.py"
)
FAILED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_anomaly_record_failed_review_v1.py"
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

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
POLICY_CLEAN_BUILD_EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_after_eth_exact_duplicate_policy_v1"
)
ETH_POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_exact_duplicate_policy_after_diagnostic_v1"
)
ETH_DIAGNOSTIC_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_duplicate_diagnostic_after_build_anomaly_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)

ARTIFACTS = {
    "policy_clean_build_execution_summary": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_summary.json",
    "policy_clean_build_execution_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_report.json",
    "policy_clean_gap_duplicate_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_gap_duplicate_report.json",
    "eth_exact_duplicate_drop_audit": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_audit.json",
    "policy_clean_schema_validation_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_schema_validation_report.json",
    "policy_clean_output_manifest": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_1h_output_manifest.json",
    "policy_clean_output_provenance_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_output_provenance_report.json",
    "policy_clean_build_compliance_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_compliance_report.json",
    "eth_policy_summary": ETH_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy_summary.json",
    "eth_exact_duplicate_policy": ETH_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy.json",
    "eth_exact_duplicate_drop_policy": ETH_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_policy.json",
    "eth_duplicate_diagnostic_summary": ETH_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_summary.json",
    "eth_duplicate_raw_rows_report": ETH_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_eth_duplicate_raw_rows_report.json",
    "download_validator_summary": DOWNLOAD_VALIDATOR_DIR
    / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json",
    "download_hash_validation_report": DOWNLOAD_VALIDATOR_DIR
    / "historical_okx_10_symbol_pilot_hash_validation_report.json",
}

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "full_csv_read_performed_now": False,
    "new_data_build_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "rebuild_execution_performed_now": False,
    "dedupe_execution_performed_now": False,
    "row_selection_performed_now": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "output_1h_csv_created_now": False,
    "output_manifest_created_now": False,
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

    summary = artifacts["policy_clean_build_execution_summary"]
    report = artifacts["policy_clean_build_execution_report"]
    gap = artifacts["policy_clean_gap_duplicate_report"]
    drop_audit = artifacts["eth_exact_duplicate_drop_audit"]
    schema = artifacts["policy_clean_schema_validation_report"]
    manifest = artifacts["policy_clean_output_manifest"]
    provenance = artifacts["policy_clean_output_provenance_report"]
    compliance = artifacts["policy_clean_build_compliance_report"]
    policy_summary = artifacts["eth_policy_summary"]
    policy = artifacts["eth_exact_duplicate_policy"]
    drop_policy = artifacts["eth_exact_duplicate_drop_policy"]
    diagnostic = artifacts["eth_duplicate_diagnostic_summary"]
    raw_rows = artifacts["eth_duplicate_raw_rows_report"]
    download_summary = artifacts["download_validator_summary"]
    hash_report = artifacts["download_hash_validation_report"]

    for label, payload in {
        "summary": summary,
        "report": report,
    }.items():
        require(
            payload.get("historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_status")
            == PREVIOUS_STATUS,
            f"{label} previous status mismatch",
        )
        require(payload.get("policy_clean_build_execution_performed") is False, f"{label} build performed mismatch")
        require(payload.get("pilot_symbol_count") == len(PILOT_SYMBOLS), f"{label} pilot count mismatch")
        require(payload.get("pilot_symbols") == PILOT_SYMBOLS, f"{label} pilot symbols mismatch")
        require(payload.get("btc_policy_clean_reused") is True, f"{label} BTC policy reuse mismatch")
        require(payload.get("btc_policy_clean_revalidated") is True, f"{label} BTC policy revalidation mismatch")
        require(payload.get("anomaly_symbol_count") == 1, f"{label} anomaly count mismatch")
        require(payload.get("anomaly_symbols") == [ANOMALY_SYMBOL], f"{label} anomaly symbols mismatch")
        require(
            payload.get("eth_exact_duplicate_rows_dropped")
            == EXPECTED_ETH_EXACT_DUPLICATE_ROWS_DROPPED,
            f"{label} ETH exact duplicate drop count mismatch",
        )
        require(
            payload.get("duplicate_open_time_count_total")
            == EXPECTED_RESIDUAL_DUPLICATE_OPEN_TIME_COUNT_TOTAL,
            f"{label} residual duplicate count mismatch",
        )
        require(payload.get("missing_minute_count_total") == 0, f"{label} missing minute mismatch")
        require(payload.get("schema_mismatch_count") == 0, f"{label} schema mismatch")
        require(payload.get("symbol_mismatch_count") == 0, f"{label} symbol mismatch")
        require(
            payload.get("observed_new_symbol_source_rows_before_policy")
            == EXPECTED_OBSERVED_NEW_SYMBOL_SOURCE_ROWS_BEFORE_POLICY,
            f"{label} observed source row mismatch",
        )
        require(
            payload.get("clean_new_symbol_source_rows_after_policy")
            == EXPECTED_CLEAN_NEW_SYMBOL_SOURCE_ROWS_AFTER_POLICY,
            f"{label} clean source row mismatch",
        )
        require(payload.get("output_csv_created") is False, f"{label} output CSV created")
        require(payload.get("output_manifest_created") is False, f"{label} output manifest created")
        require(payload.get("data_build_performed") is False, f"{label} data build performed")
        require(payload.get("aggregation_performed_now") is False, f"{label} aggregation performed")
        require(payload.get("output_valid_for_research_backtest") is False, f"{label} research/backtest claim")
        require(payload.get("output_valid_for_edge_claim") is False, f"{label} edge claim")
        require(payload.get("safe_for_full_universe_acquisition") is False, f"{label} full universe claim")
        require(payload.get("broad_acquisition_ready") is False, f"{label} broad acquisition claim")
        require(payload.get("active_p0_blocker_count") == 1, f"{label} P0 count mismatch")
        require(payload.get("replacement_checks_all_true") is False, f"{label} blocked checks mismatch")

    require(summary.get("next_module") == REQUESTED_MODULE, "previous summary next_module mismatch")
    require(gap.get("gap_duplicate_report_created") is True, "gap report missing")
    require(gap.get("anomaly_symbols") == [ANOMALY_SYMBOL], "gap anomaly mismatch")
    require(gap.get("eth_exact_duplicate_rows_dropped") == 1, "gap ETH drop count mismatch")
    require(gap.get("duplicate_open_time_count_total") == 1, "gap residual duplicate mismatch")
    require(drop_audit.get("eth_exact_duplicate_drop_audit_created") is True, "drop audit missing")
    require(drop_audit.get("target_symbol") == ANOMALY_SYMBOL, "drop audit target mismatch")
    require(drop_audit.get("eth_exact_duplicate_rows_dropped") == 1, "drop audit drop count mismatch")
    require(len(drop_audit.get("dropped_rows", [])) == 1, "drop audit dropped row detail mismatch")
    require(drop_audit.get("blocked_after_approved_drop") is True, "drop audit did not preserve block")
    require(schema.get("schema_mismatch_count") == 0, "schema report mismatch count")
    require(schema.get("symbol_mismatch_count") == 0, "schema report symbol count")
    require(manifest.get("output_manifest_created") is False, "manifest unexpectedly created")
    require(manifest.get("blocked_before_complete_manifest") is True, "manifest blocked flag mismatch")
    require(provenance.get("btc_policy_clean_reused") is True, "provenance BTC reuse mismatch")
    require(provenance.get("btc_policy_clean_revalidated") is True, "provenance BTC revalidation mismatch")
    require(compliance.get("compliance_report_created") is True, "compliance report missing")
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
        "policy_clean_build_compliance_report",
    )

    require(policy_summary.get("eth_exact_duplicate_policy_created") is True, "policy summary missing policy")
    require(policy_summary.get("target_symbol") == ANOMALY_SYMBOL, "policy summary target mismatch")
    require(policy_summary.get("exact_duplicate_extra_rows_to_drop") == 1, "policy summary drop count")
    require(policy_summary.get("replacement_checks_all_true") is True, "policy summary replacement checks")
    require(policy.get("eth_exact_duplicate_policy_created") is True, "policy artifact missing")
    require(policy.get("policy", {}).get("exact_duplicate_extra_rows_to_drop") == 1, "policy exact drop mismatch")
    require(drop_policy.get("target_symbol") == ANOMALY_SYMBOL, "drop policy target mismatch")
    require(drop_policy.get("exact_duplicate_extra_rows_to_drop") == 1, "drop policy count mismatch")
    require(diagnostic.get("target_symbol") == ANOMALY_SYMBOL, "diagnostic target mismatch")
    require(diagnostic.get("duplicate_classification") == "EXACT_DUPLICATE", "diagnostic classification mismatch")
    require(diagnostic.get("duplicate_open_time_count_total") == 1, "diagnostic duplicate count mismatch")
    require(diagnostic.get("raw_duplicate_rows_captured") is True, "diagnostic raw rows not captured")
    require(raw_rows.get("raw_duplicate_rows_captured") is True, "raw rows report missing")
    require(len(raw_rows.get("raw_duplicate_rows", [])) == 2, "raw rows report row count mismatch")
    require(download_summary.get("all_hashes_match_recorded") is True, "download validator hash summary mismatch")
    require(hash_report.get("all_hashes_match_recorded") is True, "download hash report mismatch")


def build_payloads(
    generated_at: str,
    artifacts: dict[str, dict[str, Any]],
    exists: dict[str, bool],
    valid: dict[str, bool],
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_summary = artifacts["policy_clean_build_execution_summary"]
    observed_delta = (
        EXPECTED_OBSERVED_NEW_SYMBOL_SOURCE_ROWS_BEFORE_POLICY
        - EXPECTED_CLEAN_NEW_SYMBOL_SOURCE_ROWS_AFTER_POLICY
    )
    count_mismatch_detected = observed_delta != EXPECTED_CLEAN_SOURCE_ROW_DELTA_FOR_ONE_EXACT_DROP

    shared = {
        "pilot_policy_clean_build_execution_blocked": True,
        "block_reason": BLOCK_REASON,
        "anomaly_symbol_count": 1,
        "anomaly_symbols": [ANOMALY_SYMBOL],
        "anomaly_symbol": ANOMALY_SYMBOL,
        "eth_exact_duplicate_policy_present": True,
        "eth_exact_duplicate_rows_dropped": EXPECTED_ETH_EXACT_DUPLICATE_ROWS_DROPPED,
        "residual_duplicate_open_time_count_total": EXPECTED_RESIDUAL_DUPLICATE_OPEN_TIME_COUNT_TOTAL,
        "missing_minute_count_total": 0,
        "schema_mismatch_count": 0,
        "symbol_mismatch_count": 0,
        "observed_new_symbol_source_rows_before_policy": EXPECTED_OBSERVED_NEW_SYMBOL_SOURCE_ROWS_BEFORE_POLICY,
        "clean_new_symbol_source_rows_after_policy": EXPECTED_CLEAN_NEW_SYMBOL_SOURCE_ROWS_AFTER_POLICY,
        "expected_clean_source_row_delta_for_one_exact_drop": EXPECTED_CLEAN_SOURCE_ROW_DELTA_FOR_ONE_EXACT_DROP,
        "observed_clean_source_row_delta": observed_delta,
        "count_mismatch_detected": count_mismatch_detected,
        "output_csv_created": False,
        "output_manifest_created": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 1,
    }
    blocked_record = {
        "anomaly_blocked_record_created": True,
        "source_status": PREVIOUS_STATUS,
        "source_policy_clean_build_execution_summary_artifact": str(
            ARTIFACTS["policy_clean_build_execution_summary"]
        ),
        "source_policy_clean_gap_duplicate_report_artifact": str(
            ARTIFACTS["policy_clean_gap_duplicate_report"]
        ),
        "source_eth_exact_duplicate_drop_audit_artifact": str(
            ARTIFACTS["eth_exact_duplicate_drop_audit"]
        ),
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "policy_clean_build_execution_performed": False,
        "btc_policy_clean_reused": True,
        "btc_policy_clean_revalidated": True,
        "previous_blocked_reason": source_summary.get("blocked_reason"),
        "p0_remains_active_until_eth_policy_application_residual_duplicate_diagnostic_resolves_count_mismatch": True,
        "new_download_performed_now": False,
        "api_call_performed_now": False,
        "browse_performed_now": False,
        "full_csv_read_performed_now": False,
        "dedupe_execution_performed_now": False,
        "rebuild_execution_performed_now": False,
        "row_selection_performed_now": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        **shared,
    }
    diagnostic_preview = {
        "eth_policy_application_residual_duplicate_diagnostic_preview_created": True,
        "preview_only": True,
        "diagnostic_execution_performed_now": False,
        "target_symbol": ANOMALY_SYMBOL,
        "trigger": BLOCK_REASON,
        "diagnostic_question": (
            "why one approved exact duplicate drop leaves one residual duplicate and a "
            "two-row clean source delta"
        ),
        "next_diagnostic_module_may_read_only_eth_usdt_swap_validated_zip_csv_files": True,
        "next_diagnostic_module_may_reconfirm_sha256_before_reading": True,
        "next_diagnostic_module_may_rerun_eth_duplicate_discovery_from_raw_data": True,
        "next_diagnostic_module_may_reread_eth_exact_duplicate_policy": True,
        "next_diagnostic_module_may_verify_approved_exact_duplicate_open_time_was_matched": True,
        "next_diagnostic_module_may_verify_one_row_was_dropped_or_both_rows_quarantined_dropped": True,
        "next_diagnostic_module_may_capture_raw_rows_for_any_residual_duplicate": True,
        "next_diagnostic_module_may_produce_repair_or_next_policy_route": True,
        "residual_duplicate_classification_options": [
            "A_SAME_APPROVED_DUPLICATE_NOT_ACTUALLY_REMOVED",
            "B_SECOND_DUPLICATE_GROUP_MISSED_BY_PRIOR_DIAGNOSTIC",
            "C_POLICY_APPLICATION_BUG_OR_COUNTER_BUG",
            "D_MATERIAL_CONFLICT",
            "E_UNKNOWN",
        ],
        "next_diagnostic_module_must_not_download": True,
        "next_diagnostic_module_must_not_call_api_or_browse": True,
        "next_diagnostic_module_must_not_build_or_aggregate": True,
        "next_diagnostic_module_must_not_dedupe_or_rebuild": True,
        "next_diagnostic_module_must_not_write_1h_output": True,
        "next_diagnostic_module_must_not_mark_research_backtest_edge_ready": True,
        "download_performed_now": False,
        "api_call_performed_now": False,
        "browse_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "dedupe_execution_performed_now": False,
        "output_1h_csv_created_now": False,
        **shared,
    }
    approval_record = {
        "eth_policy_application_residual_duplicate_diagnostic_approval_record_created": True,
        "approval_scope": "NEXT_SEPARATE_ETH_POLICY_APPLICATION_RESIDUAL_DUPLICATE_DIAGNOSTIC_ONLY",
        "approval_grants_diagnostic_now": False,
        "approval_grants_future_eth_policy_application_residual_duplicate_diagnostic_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
        **shared,
    }
    count_mismatch_report = {
        "policy_application_count_mismatch_report_created": True,
        "source_observation": "policy clean build blocked after approved ETH exact duplicate policy",
        "expected_count_model": (
            "one approved exact duplicate extra row should reduce clean source rows by one"
        ),
        "count_mismatch_requires_separate_diagnostic": True,
        "count_mismatch_resolved_now": False,
        **shared,
    }
    limitations_report = {
        "policy_clean_build_anomaly_limitations_report_created": True,
        "completed_10_symbol_pilot_build_exists": False,
        "completed_policy_clean_1h_output_exists": False,
        "pilot_build_did_not_succeed": True,
        "required_next_step": "ETH_POLICY_APPLICATION_RESIDUAL_DUPLICATE_DIAGNOSTIC_ONLY",
        "download_api_browse_forbidden": True,
        "new_build_aggregation_forbidden_in_this_module": True,
        "dedupe_rebuild_forbidden_in_this_module": True,
        "research_backtest_edge_claim_forbidden": True,
        "full_universe_or_broad_acquisition_claim_forbidden": True,
        **shared,
    }
    self_validator = {
        "policy_clean_build_anomaly_self_validator_created": True,
        "preflight_passed": True,
        "required_source_artifacts_exist": all(exists.values()),
        "required_source_artifacts_valid_json": all(valid.values()),
        "anomaly_blocked_record_valid": blocked_record["anomaly_blocked_record_created"] is True
        and blocked_record["pilot_policy_clean_build_execution_blocked"] is True
        and blocked_record["block_reason"] == BLOCK_REASON,
        "eth_policy_application_residual_duplicate_diagnostic_preview_valid": diagnostic_preview[
            "eth_policy_application_residual_duplicate_diagnostic_preview_created"
        ]
        is True
        and diagnostic_preview["diagnostic_execution_performed_now"] is False
        and diagnostic_preview["next_diagnostic_module_must_not_dedupe_or_rebuild"] is True,
        "eth_policy_application_residual_duplicate_diagnostic_approval_record_valid": approval_record[
            "approval_grants_future_eth_policy_application_residual_duplicate_diagnostic_next"
        ]
        is True
        and approval_record["approval_grants_diagnostic_now"] is False
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_dedupe_now"] is False
        and approval_record["approval_grants_download_now"] is False,
        "count_mismatch_report_valid": count_mismatch_report["count_mismatch_detected"] is True
        and count_mismatch_report["observed_clean_source_row_delta"] == 2,
        "no_download_api_browse_build_aggregation_dedupe_now": all(
            value is False for value in DANGEROUS_FLAGS.values()
        ),
        "p0_remains_active": blocked_record["active_p0_blocker_count"] == 1,
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks = {
        "preflight_passed": True,
        "anomaly_blocked_record_created": blocked_record["anomaly_blocked_record_created"],
        "eth_policy_application_residual_duplicate_diagnostic_preview_created": diagnostic_preview[
            "eth_policy_application_residual_duplicate_diagnostic_preview_created"
        ],
        "eth_policy_application_residual_duplicate_diagnostic_approval_record_created": approval_record[
            "eth_policy_application_residual_duplicate_diagnostic_approval_record_created"
        ],
        "pilot_policy_clean_build_execution_blocked": shared[
            "pilot_policy_clean_build_execution_blocked"
        ],
        "block_reason_valid": shared["block_reason"] == BLOCK_REASON,
        "anomaly_symbol_count_one": shared["anomaly_symbol_count"] == 1,
        "anomaly_symbols_eth": shared["anomaly_symbols"] == [ANOMALY_SYMBOL],
        "eth_exact_duplicate_policy_present": shared["eth_exact_duplicate_policy_present"] is True,
        "eth_exact_duplicate_rows_dropped_one": shared["eth_exact_duplicate_rows_dropped"] == 1,
        "residual_duplicate_open_time_count_total_one": shared[
            "residual_duplicate_open_time_count_total"
        ]
        == 1,
        "missing_schema_symbol_mismatch_zero": shared["missing_minute_count_total"] == 0
        and shared["schema_mismatch_count"] == 0
        and shared["symbol_mismatch_count"] == 0,
        "observed_source_rows_valid": shared["observed_new_symbol_source_rows_before_policy"]
        == 149_464,
        "clean_source_rows_valid": shared["clean_new_symbol_source_rows_after_policy"] == 149_462,
        "expected_delta_one_observed_delta_two": shared[
            "expected_clean_source_row_delta_for_one_exact_drop"
        ]
        == 1
        and shared["observed_clean_source_row_delta"] == 2,
        "count_mismatch_detected": shared["count_mismatch_detected"] is True,
        "no_output_csv_or_manifest": shared["output_csv_created"] is False
        and shared["output_manifest_created"] is False,
        "no_build_aggregation": shared["data_build_performed"] is False
        and shared["aggregation_performed_now"] is False,
        "approval_future_eth_policy_application_residual_duplicate_diagnostic_next": approval_record[
            "approval_grants_future_eth_policy_application_residual_duplicate_diagnostic_next"
        ]
        is True,
        "approval_rebuild_now_false": approval_record["approval_grants_rebuild_now"] is False,
        "approval_dedupe_now_false": approval_record["approval_grants_dedupe_now"] is False,
        "not_research_backtest_edge_full_universe_broad": shared[
            "output_valid_for_research_backtest"
        ]
        is False
        and shared["output_valid_for_edge_claim"] is False
        and shared["safe_for_full_universe_acquisition"] is False
        and shared["broad_acquisition_ready"] is False,
        "p0_active": shared["active_p0_blocker_count"] == 1,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_anomaly_record_status": PASS_STATUS,
        "anomaly_blocked_record_created": True,
        "eth_policy_application_residual_duplicate_diagnostic_preview_created": True,
        "eth_policy_application_residual_duplicate_diagnostic_approval_record_created": True,
        "approval_grants_future_eth_policy_application_residual_duplicate_diagnostic_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "active_p1_attention_count": ACTIVE_P1_ATTENTION_COUNT,
        "current_evidence_chain_quality_after_anomaly_record": AFTER_QUALITY,
        "next_module": NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_anomaly_record_run": tracked_python_count(),
        **shared,
    }
    bundle = {
        "anomaly_blocked_record": blocked_record,
        "eth_policy_application_residual_duplicate_diagnostic_preview": diagnostic_preview,
        "eth_policy_application_residual_duplicate_diagnostic_approval_record": approval_record,
        "policy_application_count_mismatch_report": count_mismatch_report,
        "limitations_report": limitations_report,
        "self_validator": self_validator,
        "summary": summary_payload,
    }
    payloads = {
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record.json": blocked_record,
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_preview.json": diagnostic_preview,
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_approval_record.json": approval_record,
        "historical_okx_10_symbol_pilot_policy_application_count_mismatch_report.json": count_mismatch_report,
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_limitations_report.json": limitations_report,
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_bundle_summary.json": bundle,
        f"{MODULE_NAME}_latest.json": summary_payload,
    }
    return summary_payload, payloads


def validate_written_artifacts(summary_payload: dict[str, Any]) -> dict[str, bool]:
    required_files = [
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record.json",
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_preview.json",
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_approval_record.json",
        "historical_okx_10_symbol_pilot_policy_application_count_mismatch_report.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_limitations_report.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_self_validator.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_bundle_summary.json",
    ]
    loaded: dict[str, Any] = {}
    for filename in required_files:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing written artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))

    blocked = loaded[
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record.json"
    ]
    preview = loaded[
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_preview.json"
    ]
    approval = loaded[
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_approval_record.json"
    ]
    mismatch = loaded[
        "historical_okx_10_symbol_pilot_policy_application_count_mismatch_report.json"
    ]
    validator = loaded[
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_self_validator.json"
    ]
    checks = {
        "required_artifacts_exist": True,
        "blocked_record_preserves_policy_clean_blocked_state": blocked.get(
            "pilot_policy_clean_build_execution_blocked"
        )
        is True
        and blocked.get("block_reason") == BLOCK_REASON,
        "eth_preview_created_without_execution": preview.get(
            "eth_policy_application_residual_duplicate_diagnostic_preview_created"
        )
        is True
        and preview.get("diagnostic_execution_performed_now") is False,
        "approval_grants_only_future_diagnostic": approval.get(
            "approval_grants_future_eth_policy_application_residual_duplicate_diagnostic_next"
        )
        is True
        and approval.get("approval_grants_diagnostic_now") is False
        and approval.get("approval_grants_rebuild_now") is False
        and approval.get("approval_grants_dedupe_now") is False,
        "count_mismatch_report_preserves_delta_two": mismatch.get("count_mismatch_detected") is True
        and mismatch.get("observed_clean_source_row_delta") == 2,
        "self_validator_allows_next_module": validator.get("next_module_valid") is True,
        "summary_replacement_checks_all_true": summary_payload.get("replacement_checks_all_true")
        is True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "p0_still_active": summary_payload.get("active_p0_blocker_count") == 1,
    }
    checks["written_artifacts_valid"] = all(checks.values())
    return checks


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    artifacts = {label: load_json(path, label, exists, valid) for label, path in ARTIFACTS.items()}
    validate_prior_artifacts(artifacts)
    summary_payload, payloads = build_payloads(generated_at, artifacts, exists, valid)
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
            "historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_anomaly_record_status": BLOCKED_STATUS,
            "anomaly_blocked_record_created": False,
            "eth_policy_application_residual_duplicate_diagnostic_preview_created": False,
            "eth_policy_application_residual_duplicate_diagnostic_approval_record_created": False,
            "pilot_policy_clean_build_execution_blocked": True,
            "block_reason": BLOCK_REASON,
            "anomaly_symbol_count": 1,
            "anomaly_symbols": [ANOMALY_SYMBOL],
            "eth_exact_duplicate_policy_present": False,
            "eth_exact_duplicate_rows_dropped": EXPECTED_ETH_EXACT_DUPLICATE_ROWS_DROPPED,
            "residual_duplicate_open_time_count_total": EXPECTED_RESIDUAL_DUPLICATE_OPEN_TIME_COUNT_TOTAL,
            "observed_new_symbol_source_rows_before_policy": EXPECTED_OBSERVED_NEW_SYMBOL_SOURCE_ROWS_BEFORE_POLICY,
            "clean_new_symbol_source_rows_after_policy": EXPECTED_CLEAN_NEW_SYMBOL_SOURCE_ROWS_AFTER_POLICY,
            "expected_clean_source_row_delta_for_one_exact_drop": EXPECTED_CLEAN_SOURCE_ROW_DELTA_FOR_ONE_EXACT_DROP,
            "observed_clean_source_row_delta": EXPECTED_OBSERVED_CLEAN_SOURCE_ROW_DELTA,
            "count_mismatch_detected": True,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "output_manifest_created": False,
            "approval_grants_future_eth_policy_application_residual_duplicate_diagnostic_next": False,
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
