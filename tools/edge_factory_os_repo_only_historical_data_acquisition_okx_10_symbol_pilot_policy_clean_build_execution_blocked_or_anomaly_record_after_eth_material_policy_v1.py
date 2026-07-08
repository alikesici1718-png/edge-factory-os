from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_eth_material_policy_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "60e9686"
PREVIOUS_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "EXECUTION_ANOMALY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "ANOMALY_RECORD_SOL_DUPLICATE_DIAGNOSTIC_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "ANOMALY_RECORD_FAILED_REVIEW"
)
BLOCK_REASON = "SOL_DUPLICATE_OPEN_TIME_ROWS_AFTER_ETH_POLICY_CLEAN_PROGRESS"
ANOMALY_SYMBOL = "SOL-USDT-SWAP"
TARGET_ETH_SYMBOL = "ETH-USDT-SWAP"
SOL_DUPLICATE_OPEN_TIME = 1_697_108_400_000
ACTIVE_P1_ATTENTION_COUNT = 0
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_BLOCKED_"
    "SOL_DUPLICATE_DIAGNOSTIC_READY"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_duplicate_diagnostic_after_policy_clean_build_anomaly_v1.py"
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
    "policy_clean_build_execution_after_eth_material_conflict_policy_v1"
)
ETH_MATERIAL_POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_material_duplicate_conflict_policy_after_residual_diagnostic_v1"
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
    "policy_clean_manifest": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_1h_output_manifest.json",
    "policy_clean_schema_validation_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_schema_validation_report.json",
    "policy_clean_output_provenance_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_output_provenance_report.json",
    "policy_clean_compliance_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_compliance_report.json",
    "eth_exact_duplicate_drop_audit": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_audit.json",
    "eth_material_conflict_quarantine_audit": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_eth_material_conflict_quarantine_audit.json",
    "eth_material_policy_summary": ETH_MATERIAL_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_summary.json",
    "eth_material_policy": ETH_MATERIAL_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy.json",
    "eth_material_policy_counts": ETH_MATERIAL_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_duplicate_group_policy_counts.json",
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
    manifest = artifacts["policy_clean_manifest"]
    schema = artifacts["policy_clean_schema_validation_report"]
    provenance = artifacts["policy_clean_output_provenance_report"]
    compliance = artifacts["policy_clean_compliance_report"]
    drop_audit = artifacts["eth_exact_duplicate_drop_audit"]
    quarantine_audit = artifacts["eth_material_conflict_quarantine_audit"]
    eth_policy_summary = artifacts["eth_material_policy_summary"]
    eth_policy = artifacts["eth_material_policy"]
    eth_counts = artifacts["eth_material_policy_counts"]
    download_summary = artifacts["download_validator_summary"]
    hash_report = artifacts["download_hash_validation_report"]

    for label, payload in {"summary": summary, "report": report}.items():
        require(
            payload.get("historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_status")
            == PREVIOUS_STATUS,
            f"{label} previous status mismatch",
        )
        require(payload.get("policy_clean_build_execution_performed") is False, f"{label} build unexpectedly succeeded")
        require(payload.get("pilot_symbol_count") == 10, f"{label} pilot symbol count mismatch")
        require(payload.get("pilot_symbols") == PILOT_SYMBOLS, f"{label} pilot symbols mismatch")
        require(payload.get("btc_policy_clean_reused") is True, f"{label} BTC reuse mismatch")
        require(payload.get("btc_policy_clean_revalidated") is True, f"{label} BTC revalidation mismatch")
        require(payload.get("new_symbol_build_count") == 1, f"{label} new symbol build count mismatch")
        require(payload.get("anomaly_symbols") == [ANOMALY_SYMBOL], f"{label} anomaly symbol mismatch")
        require(payload.get("duplicate_open_time_count_total") == 1, f"{label} duplicate count mismatch")
        require(payload.get("missing_minute_count_total") == 0, f"{label} missing minute mismatch")
        require(payload.get("schema_mismatch_count") == 0, f"{label} schema mismatch count")
        require(payload.get("symbol_mismatch_count") == 0, f"{label} symbol mismatch count")
        require(payload.get("eth_exact_duplicate_rows_dropped") == 327, f"{label} ETH exact drops mismatch")
        require(payload.get("eth_material_conflict_rows_quarantined") == 2, f"{label} ETH quarantine mismatch")
        require(payload.get("eth_clean_source_rows_after_policy") == 1_516_319, f"{label} ETH clean row mismatch")
        require(payload.get("eth_complete_1h_row_count") == 25_271, f"{label} ETH complete row mismatch")
        require(payload.get("eth_incomplete_1h_row_count") == 1, f"{label} ETH incomplete row mismatch")
        require(payload.get("output_1h_row_count") == 27_762, f"{label} partial output row count mismatch")
        require(payload.get("complete_1h_row_count") == 27_761, f"{label} partial complete row count mismatch")
        require(payload.get("incomplete_1h_row_count") == 1, f"{label} partial incomplete row count mismatch")
        require(payload.get("output_csv_created") is True, f"{label} partial output CSV flag mismatch")
        require(payload.get("output_manifest_created") is False, f"{label} manifest unexpectedly created")
        require(payload.get("data_build_performed") is False, f"{label} data build flag mismatch")
        require(payload.get("aggregation_performed_now") is False, f"{label} aggregation flag mismatch")
        require(payload.get("active_p0_blocker_count") == 1, f"{label} P0 count mismatch")
        require(payload.get("replacement_checks_all_true") is False, f"{label} replacement checks unexpectedly passed")
        require(str(payload.get("blocked_reason", "")).startswith("SOL-USDT-SWAP duplicate open_time"), f"{label} blocked reason mismatch")
        validate_false(
            payload,
            [
                "synthetic_fill_used",
                "forward_fill_used",
                "backfill_used",
                "output_valid_for_research_backtest",
                "output_valid_for_edge_claim",
                "safe_for_full_universe_acquisition",
                "broad_acquisition_ready",
                "new_download_performed_now",
                "okx_api_call_performed",
                "okx_browse_performed",
            ],
            label,
        )
    require(summary.get("next_module") == REQUESTED_MODULE, "previous next_module mismatch")

    require(gap.get("gap_duplicate_report_created") is True, "gap report missing")
    require(gap.get("anomaly_symbols") == [ANOMALY_SYMBOL], "gap anomaly symbol mismatch")
    require(gap.get("duplicate_open_time_count_total") == 1, "gap duplicate count mismatch")
    require(gap.get("eth_exact_duplicate_rows_dropped") == 327, "gap ETH drop count mismatch")
    require(gap.get("eth_material_conflict_rows_quarantined") == 2, "gap ETH quarantine count mismatch")
    require(manifest.get("output_manifest_created") is False, "manifest unexpectedly created")
    require(manifest.get("blocked_before_complete_manifest") is True, "manifest blocked state mismatch")
    require(schema.get("schema_mismatch_count") == 0, "schema report mismatch")
    require(schema.get("symbol_mismatch_count") == 0, "schema report symbol mismatch")
    require(provenance.get("btc_policy_clean_reused") is True, "provenance BTC reuse mismatch")
    require(provenance.get("btc_policy_clean_revalidated") is True, "provenance BTC revalidation mismatch")
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
        "compliance_report",
    )
    require(drop_audit.get("eth_exact_duplicate_rows_dropped") == 327, "drop audit count mismatch")
    require(quarantine_audit.get("eth_material_conflict_rows_quarantined") == 2, "quarantine audit count mismatch")

    require(eth_policy_summary.get("material_conflict_policy_created") is True, "ETH policy summary missing")
    require(eth_policy_summary.get("eth_exact_duplicate_extra_rows_to_drop") == 327, "ETH policy exact drop count mismatch")
    require(eth_policy_summary.get("eth_material_conflict_rows_to_quarantine") == 2, "ETH policy quarantine count mismatch")
    require(eth_policy_summary.get("next_module").endswith("policy_clean_build_execution_after_eth_material_conflict_policy_v1.py"), "ETH policy next route mismatch")
    require(eth_policy.get("material_conflict_policy_created") is True, "ETH policy artifact missing")
    require(eth_counts.get("policy_counts_complete") is True, "ETH policy counts incomplete")
    require(download_summary.get("all_hashes_match_recorded") is True, "download validator hash status mismatch")
    require(hash_report.get("all_hashes_match_recorded") is True, "hash report mismatch")


def build_payloads(generated_at: str, exists: dict[str, bool], valid: dict[str, bool]) -> tuple[dict[str, Any], dict[str, Any]]:
    shared = {
        "pilot_policy_clean_build_execution_blocked": True,
        "block_reason": BLOCK_REASON,
        "anomaly_symbol_count": 1,
        "anomaly_symbols": [ANOMALY_SYMBOL],
        "anomaly_symbol": ANOMALY_SYMBOL,
        "duplicate_open_time_count_total": 1,
        "known_sol_duplicate_open_time": SOL_DUPLICATE_OPEN_TIME,
        "missing_minute_count_total": 0,
        "schema_mismatch_count": 0,
        "symbol_mismatch_count": 0,
        "eth_material_policy_applied_before_block": True,
        "eth_exact_duplicate_rows_dropped": 327,
        "eth_material_conflict_rows_quarantined": 2,
        "eth_clean_source_rows_after_policy": 1_516_319,
        "eth_complete_1h_row_count": 25_271,
        "eth_incomplete_1h_row_count": 1,
        "partial_output_created_during_blocked_route": True,
        "partial_output_trusted": False,
        "partial_output_quarantined": True,
        "partial_output_valid_for_research_backtest": False,
        "partial_output_valid_for_edge_claim": False,
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
        "policy_clean_build_execution_performed": False,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "btc_policy_clean_reused": True,
        "btc_policy_clean_revalidated": True,
        "new_symbol_build_count": 1,
        "p0_remains_active_until_sol_duplicate_diagnostic_resolves_it": True,
        **shared,
    }
    quarantine_record = {
        "partial_output_quarantine_record_created": True,
        "partial_output_source_module": "policy_clean_build_execution_after_eth_material_conflict_policy_v1",
        "partial_output_reason": "BLOCKED_ROUTE_NO_FINAL_MANIFEST_SOL_DUPLICATE_ANOMALY",
        "partial_output_row_count_at_block": 27_762,
        "partial_complete_row_count_at_block": 27_761,
        "partial_incomplete_row_count_at_block": 1,
        "partial_output_must_not_be_used_as_pipeline_output": True,
        "partial_output_must_not_be_used_for_research_backtest_edge": True,
        "partial_output_requires_sol_duplicate_diagnostic_before_any_rebuild_route": True,
        **shared,
    }
    diagnostic_preview = {
        "sol_duplicate_diagnostic_preview_created": True,
        "preview_only": True,
        "diagnostic_execution_performed_now": False,
        "target_symbol": ANOMALY_SYMBOL,
        "known_duplicate_open_time": SOL_DUPLICATE_OPEN_TIME,
        "next_diagnostic_module_may_read_only_sol_usdt_swap_validated_zip_csv_files": True,
        "next_diagnostic_module_may_reconfirm_sha256_before_reading": True,
        "next_diagnostic_module_may_rerun_sol_duplicate_discovery_across_approved_date_range": True,
        "next_diagnostic_module_may_locate_duplicate_open_time_groups": True,
        "duplicate_classification_options": [
            "A_EXACT_DUPLICATE_ROW",
            "B_CONFIRM_ONLY_CONFLICT",
            "C_OHLC_VOLUME_OHLCV_MATERIAL_CONFLICT",
            "D_UNKNOWN_UNINSPECTABLE",
        ],
        "next_diagnostic_module_may_capture_raw_duplicate_rows_and_differing_fields": True,
        "next_diagnostic_module_may_produce_next_policy_route": True,
        "next_diagnostic_module_must_not_download": True,
        "next_diagnostic_module_must_not_call_api_or_browse": True,
        "next_diagnostic_module_must_not_build_or_aggregate": True,
        "next_diagnostic_module_must_not_dedupe_or_rebuild": True,
        "next_diagnostic_module_must_not_write_1h_output": True,
        "next_diagnostic_module_must_not_mark_research_backtest_edge_ready": True,
        **shared,
    }
    approval_record = {
        "sol_duplicate_diagnostic_approval_record_created": True,
        "approval_scope": "NEXT_SEPARATE_SOL_DUPLICATE_DIAGNOSTIC_ONLY",
        "approval_grants_diagnostic_now": False,
        "approval_grants_future_sol_duplicate_diagnostic_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
        **shared,
    }
    limitations_report = {
        "policy_clean_build_anomaly_limitations_report_created": True,
        "completed_10_symbol_policy_clean_build_exists": False,
        "final_output_manifest_exists": False,
        "partial_output_quarantined": True,
        "required_next_step": "SOL_DUPLICATE_DIAGNOSTIC_ONLY",
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
        "blocked_record_valid": blocked_record["anomaly_blocked_record_created"] is True
        and blocked_record["block_reason"] == BLOCK_REASON
        and blocked_record["anomaly_symbols"] == [ANOMALY_SYMBOL],
        "partial_output_quarantine_valid": quarantine_record["partial_output_quarantined"] is True
        and quarantine_record["partial_output_trusted"] is False,
        "sol_preview_valid": diagnostic_preview["sol_duplicate_diagnostic_preview_created"] is True
        and diagnostic_preview["diagnostic_execution_performed_now"] is False,
        "sol_approval_valid": approval_record["approval_grants_future_sol_duplicate_diagnostic_next"] is True
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_dedupe_now"] is False,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "p0_remains_active": shared["active_p0_blocker_count"] == 1,
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks = {
        "anomaly_blocked_record_created": blocked_record["anomaly_blocked_record_created"],
        "partial_output_quarantine_record_created": quarantine_record[
            "partial_output_quarantine_record_created"
        ],
        "sol_duplicate_diagnostic_preview_created": diagnostic_preview[
            "sol_duplicate_diagnostic_preview_created"
        ],
        "sol_duplicate_diagnostic_approval_record_created": approval_record[
            "sol_duplicate_diagnostic_approval_record_created"
        ],
        "pilot_policy_clean_build_execution_blocked": shared["pilot_policy_clean_build_execution_blocked"],
        "block_reason_valid": shared["block_reason"] == BLOCK_REASON,
        "sol_anomaly_preserved": shared["anomaly_symbols"] == [ANOMALY_SYMBOL]
        and shared["duplicate_open_time_count_total"] == 1,
        "eth_policy_progress_preserved": shared["eth_material_policy_applied_before_block"] is True
        and shared["eth_exact_duplicate_rows_dropped"] == 327
        and shared["eth_material_conflict_rows_quarantined"] == 2,
        "partial_output_quarantined": shared["partial_output_created_during_blocked_route"] is True
        and shared["partial_output_trusted"] is False
        and shared["partial_output_quarantined"] is True,
        "no_output_or_manifest_created_now": shared["output_csv_created"] is False
        and shared["output_manifest_created"] is False,
        "no_build_aggregation_now": shared["data_build_performed"] is False
        and shared["aggregation_performed_now"] is False,
        "approval_future_sol_diagnostic_only": approval_record[
            "approval_grants_future_sol_duplicate_diagnostic_next"
        ]
        is True
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_dedupe_now"] is False,
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
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_anomaly_record_status": PASS_STATUS,
        "anomaly_blocked_record_created": True,
        "partial_output_quarantine_record_created": True,
        "sol_duplicate_diagnostic_preview_created": True,
        "sol_duplicate_diagnostic_approval_record_created": True,
        "approval_grants_future_sol_duplicate_diagnostic_next": True,
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
        "partial_output_quarantine_record": quarantine_record,
        "sol_duplicate_diagnostic_preview": diagnostic_preview,
        "sol_duplicate_diagnostic_approval_record": approval_record,
        "limitations_report": limitations_report,
        "self_validator": self_validator,
        "summary": summary,
    }
    payloads = {
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record_after_eth_policy.json": blocked_record,
        "historical_okx_10_symbol_pilot_partial_output_quarantine_record_after_blocked_build.json": quarantine_record,
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_preview.json": diagnostic_preview,
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_approval_record.json": approval_record,
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_limitations_report.json": limitations_report,
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_bundle_summary.json": bundle,
        f"{MODULE_NAME}_latest.json": summary,
    }
    return summary, payloads


def validate_written_artifacts(summary: dict[str, Any]) -> dict[str, bool]:
    required_files = [
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record_after_eth_policy.json",
        "historical_okx_10_symbol_pilot_partial_output_quarantine_record_after_blocked_build.json",
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_preview.json",
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_approval_record.json",
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
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record_after_eth_policy.json"
    ]
    quarantine = loaded[
        "historical_okx_10_symbol_pilot_partial_output_quarantine_record_after_blocked_build.json"
    ]
    approval = loaded[
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_approval_record.json"
    ]
    checks = {
        "required_artifacts_exist": True,
        "blocked_record_preserves_sol_anomaly": blocked.get("anomaly_symbols") == [ANOMALY_SYMBOL]
        and blocked.get("block_reason") == BLOCK_REASON,
        "partial_output_quarantined": quarantine.get("partial_output_quarantined") is True
        and quarantine.get("partial_output_trusted") is False,
        "approval_grants_only_future_sol_diagnostic": approval.get(
            "approval_grants_future_sol_duplicate_diagnostic_next"
        )
        is True
        and approval.get("approval_grants_rebuild_now") is False,
        "summary_replacement_checks_all_true": summary.get("replacement_checks_all_true") is True,
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
    summary, payloads = build_payloads(generated_at, exists, valid)
    require(summary["replacement_checks_all_true"] is True, "replacement checks failed")
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)
    written = validate_written_artifacts(summary)
    require(written["written_artifacts_valid"] is True, f"written artifact validation failed: {written}")
    print(json.dumps(summary, indent=2, sort_keys=True))


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
            "partial_output_quarantine_record_created": False,
            "sol_duplicate_diagnostic_preview_created": False,
            "sol_duplicate_diagnostic_approval_record_created": False,
            "pilot_policy_clean_build_execution_blocked": True,
            "block_reason": BLOCK_REASON,
            "anomaly_symbol_count": 1,
            "anomaly_symbols": [ANOMALY_SYMBOL],
            "duplicate_open_time_count_total": 1,
            "missing_minute_count_total": 0,
            "eth_material_policy_applied_before_block": True,
            "partial_output_created_during_blocked_route": True,
            "partial_output_trusted": False,
            "partial_output_quarantined": True,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "output_manifest_created": False,
            "approval_grants_future_sol_duplicate_diagnostic_next": False,
            "approval_grants_rebuild_now": False,
            "approval_grants_dedupe_now": False,
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
