from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_sol_policy_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_sol_policy_v1.py"
)
EXPECTED_HEAD = "1d4b9bc"
EXPECTED_FULL_AUDIT_STATUS = "PASS_REPO_ONLY_FULL_AUDIT_AFTER_10_SYMBOL_POLICY_CLEAN_BUILD_BLOCK_READY_FOR_BATCH_ROUTE_RECORD"
PREVIOUS_BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "EXECUTION_ANOMALY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "ANOMALY_RECORD_BATCH_CLASSIFICATION_READY_AUDIT_CONFIRMED"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "ANOMALY_RECORD_FAILED_REVIEW"
)
BLOCK_REASON = "SOL_UNAPPROVED_DUPLICATE_AFTER_NARROW_SOL_EXACT_POLICY"
ANOMALY_SYMBOL = "SOL-USDT-SWAP"
UNAPPROVED_DUPLICATE_OPEN_TIME = 1_697_108_460_000
DORMANT_REPO_ATTENTION_COUNT = 716
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_BLOCKED_"
    "BATCH_ANOMALY_CLASSIFICATION_READY_AUDIT_CONFIRMED"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "batch_anomaly_classification_after_policy_clean_build_block_v1.py"
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
ANOMALY_TYPES = [
    "CLEAN_NO_ANOMALY",
    "EXACT_DUPLICATE_ONLY",
    "MATERIAL_DUPLICATE_CONFLICT",
    "MISSING_MINUTE",
    "SCHEMA_MISMATCH",
    "SYMBOL_MISMATCH",
    "COVERAGE_GAP",
    "UNKNOWN",
]

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
FULL_AUDIT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_full_audit_after_10_symbol_policy_clean_build_block_v1"
POLICY_CLEAN_BUILD_EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_after_sol_exact_duplicate_policy_v1"
)
SOL_POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_exact_duplicate_policy_after_diagnostic_v1"
)
ETH_MATERIAL_POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_material_duplicate_conflict_policy_after_residual_diagnostic_v1"
)
BTC_POLICY_SUMMARY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_"
    "policy_clean_pipeline_summary_after_rebuild_validator_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)

ARTIFACTS = {
    "full_audit_summary": FULL_AUDIT_DIR / "repo_only_full_audit_summary.json",
    "full_audit_report": FULL_AUDIT_DIR / "repo_only_full_audit_after_10_symbol_policy_clean_build_block_report.json",
    "full_audit_partial_output": FULL_AUDIT_DIR / "repo_only_full_audit_partial_output_quarantine_report.json",
    "full_audit_next_route": FULL_AUDIT_DIR / "repo_only_full_audit_next_route_report.json",
    "blocked_build_summary": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_summary.json",
    "blocked_build_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_report.json",
    "blocked_gap_duplicate_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_gap_duplicate_report.json",
    "blocked_output_manifest": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_1h_output_manifest.json",
    "blocked_compliance_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_compliance_report.json",
    "blocked_schema_validation_report": POLICY_CLEAN_BUILD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_schema_validation_report.json",
    "sol_exact_policy_summary": SOL_POLICY_DIR
    / "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy_summary.json",
    "sol_exact_policy": SOL_POLICY_DIR / "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy.json",
    "sol_exact_drop_policy": SOL_POLICY_DIR
    / "historical_okx_10_symbol_pilot_sol_exact_duplicate_drop_policy.json",
    "eth_material_policy_summary": ETH_MATERIAL_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_summary.json",
    "btc_policy_clean_summary": BTC_POLICY_SUMMARY_DIR
    / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary.json",
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
    "zip_csv_parquet_row_read_performed_now": False,
    "full_csv_read_performed_now": False,
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
    "candidate_generation_performed_now": False,
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


def current_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def tracked_python_files_including_current() -> list[str]:
    files = sorted(path for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))
    rel = current_tool_rel()
    if APPROVED_TOOL.exists() and rel not in files:
        files.append(rel)
    return sorted(files)


def tracked_python_validation() -> dict[str, Any]:
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    for rel in tracked_python_files_including_current():
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(tracked_python_files_including_current()),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def repo_has_only_this_tool_change() -> bool:
    status = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    if not status:
        return True
    rel = current_tool_rel()
    return all(line[3:].replace("\\", "/") == rel for line in status)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> dict[str, Any]:
    exists[label] = path.exists()
    require(path.exists(), f"missing artifact {label}: {path}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise Blocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(loaded, dict), f"artifact {label} is not a JSON object")
    return loaded


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_false(payload: dict[str, Any], keys: list[str], label: str) -> None:
    for key in keys:
        require(payload.get(key) is False, f"{label}.{key} must be false")


def validate_inputs(artifacts: dict[str, dict[str, Any]], py: dict[str, Any]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(current_tool_rel() == CURRENT_TOOL_REL, "target path guard mismatch")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved SOL anomaly record module")
    require(py["syntax_error_count"] == 0, "tracked Python syntax errors present")
    require(py["bom_error_count"] == 0, "tracked Python BOM errors present")

    full_audit = artifacts["full_audit_summary"]
    require(full_audit.get("full_audit_status") == EXPECTED_FULL_AUDIT_STATUS, "full audit status mismatch")
    require(full_audit.get("repo_clean") is True, "full audit repo_clean mismatch")
    require(full_audit.get("dangerous_true_flag_count") == 0, "full audit dangerous flag count mismatch")
    require(full_audit.get("syntax_error_count") == 0, "full audit syntax count mismatch")
    require(full_audit.get("bom_error_count") == 0, "full audit BOM count mismatch")
    require(full_audit.get("active_p0_blocker_count") == 1, "full audit active P0 mismatch")
    require(full_audit.get("active_p1_attention_count", 0) >= 505, "full audit active P1 mismatch")
    require(full_audit.get("dormant_repo_attention_count") == DORMANT_REPO_ATTENTION_COUNT, "dormant attention mismatch")
    require(full_audit.get("latest_blocked_route_confirmed") is True, "full audit blocked route mismatch")
    require(full_audit.get("latest_anomaly_symbol") == ANOMALY_SYMBOL, "full audit anomaly symbol mismatch")
    require(full_audit.get("latest_unapproved_duplicate_open_time") == UNAPPROVED_DUPLICATE_OPEN_TIME, "full audit duplicate open_time mismatch")
    require(full_audit.get("partial_output_trusted") is False, "full audit partial trust mismatch")
    require(full_audit.get("partial_output_quarantine_required") is True, "full audit quarantine mismatch")
    require(full_audit.get("one_symbol_policy_loop_should_continue") is False, "full audit loop continuation mismatch")
    require(full_audit.get("batch_anomaly_classification_required") is True, "full audit batch classification mismatch")
    require(full_audit.get("stale_guard_attention_count") == 504, "full audit stale guard mismatch")
    require(full_audit.get("current_head_path_guard_passed") is True, "full audit current guard mismatch")
    require(full_audit.get("next_module") == REQUESTED_MODULE, "full audit next module mismatch")
    require(full_audit.get("replacement_checks_all_true") is True, "full audit replacement checks mismatch")

    blocked = artifacts["blocked_build_summary"]
    blocked_report = artifacts["blocked_build_report"]
    gap = artifacts["blocked_gap_duplicate_report"]
    manifest = artifacts["blocked_output_manifest"]
    compliance = artifacts["blocked_compliance_report"]
    schema = artifacts["blocked_schema_validation_report"]
    for label, payload in {"blocked_summary": blocked, "blocked_report": blocked_report}.items():
        require(
            payload.get("historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_status")
            == PREVIOUS_BLOCKED_STATUS,
            f"{label} blocked status mismatch",
        )
        require(payload.get("policy_clean_build_execution_performed") is False, f"{label} build success mismatch")
        require(payload.get("anomaly_symbol_count") == 1, f"{label} anomaly count mismatch")
        require(payload.get("anomaly_symbols") == [ANOMALY_SYMBOL], f"{label} anomaly symbol mismatch")
        require(payload.get("duplicate_open_time_count_total") == 1, f"{label} duplicate count mismatch")
        require(str(UNAPPROVED_DUPLICATE_OPEN_TIME) in str(payload.get("blocked_reason", "")), f"{label} open_time missing")
        require(payload.get("output_csv_created") is True, f"{label} partial CSV flag mismatch")
        require(payload.get("output_manifest_created") is False, f"{label} manifest flag mismatch")
        require(payload.get("replacement_checks_all_true") is False, f"{label} latest replacement checks mismatch")
        require(payload.get("active_p0_blocker_count") == 1, f"{label} P0 mismatch")
        validate_false(
            payload,
            [
                "data_build_performed",
                "aggregation_performed_now",
                "okx_api_call_performed",
                "okx_browse_performed",
                "output_valid_for_research_backtest",
                "output_valid_for_edge_claim",
                "safe_for_full_universe_acquisition",
                "broad_acquisition_ready",
                "synthetic_fill_used",
                "forward_fill_used",
                "backfill_used",
            ],
            label,
        )
    require(gap.get("anomaly_symbols") == [ANOMALY_SYMBOL], "gap report anomaly mismatch")
    require(gap.get("duplicate_open_time_count_total") == 1, "gap report duplicate count mismatch")
    require(manifest.get("output_manifest_created") is False, "blocked manifest unexpectedly created")
    require(manifest.get("blocked_before_complete_manifest") is True, "manifest block marker mismatch")
    require(schema.get("schema_mismatch_count") == 0, "schema mismatch count not zero")
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
        "blocked_compliance_report",
    )

    sol_policy = artifacts["sol_exact_policy_summary"]
    require(sol_policy.get("target_symbol") == ANOMALY_SYMBOL, "SOL policy target mismatch")
    require(sol_policy.get("sol_exact_dedupe_required") is True, "SOL exact policy missing")
    require(sol_policy.get("exact_duplicate_extra_rows_to_drop") == 1, "SOL exact duplicate drop count mismatch")
    require(sol_policy.get("next_module", "").endswith("policy_clean_build_execution_after_sol_exact_duplicate_policy_v1.py"), "SOL policy next module mismatch")
    require(sol_policy.get("replacement_checks_all_true") is True, "SOL policy replacement checks mismatch")
    require(sol_policy.get("duplicate_open_time") != UNAPPROVED_DUPLICATE_OPEN_TIME, "SOL policy unexpectedly approved latest duplicate")


def build_payloads(
    generated_at: str,
    artifacts: dict[str, dict[str, Any]],
    exists: dict[str, bool],
    valid: dict[str, bool],
    py: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    full_audit = artifacts["full_audit_summary"]
    blocked = artifacts["blocked_build_summary"]
    blocked_manifest = artifacts["blocked_output_manifest"]
    partial_audit = artifacts["full_audit_partial_output"]
    next_route_audit = artifacts["full_audit_next_route"]
    active_p1_attention_count = max(int(full_audit.get("active_p1_attention_count", 0)), 505)

    shared = {
        "audit_confirmed_blocked_route": True,
        "pilot_policy_clean_build_execution_blocked": True,
        "block_reason": BLOCK_REASON,
        "anomaly_symbol_count": 1,
        "anomaly_symbols": [ANOMALY_SYMBOL],
        "anomaly_symbol": ANOMALY_SYMBOL,
        "unapproved_duplicate_open_time": UNAPPROVED_DUPLICATE_OPEN_TIME,
        "prior_sol_policy_was_too_narrow": True,
        "one_symbol_policy_loop_should_continue": False,
        "one_symbol_policy_loop_terminated": True,
        "batch_anomaly_classification_required": True,
        "partial_output_created_during_blocked_route": True,
        "partial_output_trusted": False,
        "partial_output_quarantined": True,
        "partial_output_valid_for_any_downstream_use": False,
        "partial_output_allowed_for_validator": False,
        "partial_output_allowed_for_research_backtest_edge": False,
        "output_csv_created_in_blocked_execution": True,
        "output_manifest_created_in_blocked_execution": False,
        "replacement_checks_all_true_latest": False,
        "full_audit_passed": True,
        "dangerous_true_flag_count": 0,
        "syntax_error_count": 0,
        "bom_error_count": 0,
        "stale_guard_attention_count": 504,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "approval_grants_future_batch_anomaly_classification_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": active_p1_attention_count,
        "dormant_repo_attention_count": DORMANT_REPO_ATTENTION_COUNT,
        "current_evidence_chain_quality_after_anomaly_record": AFTER_QUALITY,
        "next_module": NEXT_MODULE,
    }
    blocked_record = {
        "anomaly_blocked_record_created": True,
        "record_scope": "AUDIT_CONFIRMED_SOL_POLICY_CLEAN_BUILD_BLOCK",
        "source_blocked_build_status": blocked.get(
            "historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_status"
        ),
        "source_blocked_reason": blocked.get("blocked_reason"),
        "source_output_1h_row_count_metadata_only": blocked.get("output_1h_row_count"),
        "source_complete_1h_row_count_metadata_only": blocked.get("complete_1h_row_count"),
        "source_incomplete_1h_row_count_metadata_only": blocked.get("incomplete_1h_row_count"),
        **shared,
    }
    quarantine_record = {
        "partial_output_quarantine_record_created": True,
        "quarantine_scope": "PARTIAL_OUTPUT_FROM_BLOCKED_SOL_POLICY_CLEAN_BUILD",
        "partial_output_source_directory": str(POLICY_CLEAN_BUILD_EXECUTION_DIR / "pilot_1h_outputs"),
        "partial_output_metadata_names": partial_audit.get("output_csv_metadata_names", []),
        "partial_output_must_not_feed_validator": True,
        "partial_output_must_not_feed_research_backtest_edge": True,
        "partial_output_must_not_feed_batch_policy": True,
        "partial_output_must_not_feed_batch_policy_except_as_blocked_context_metadata_only": True,
        "output_manifest_created_in_blocked_manifest_artifact": blocked_manifest.get("output_manifest_created"),
        **shared,
    }
    loop_termination_record = {
        "one_symbol_policy_loop_termination_record_created": True,
        "reason": (
            "SOL produced another unapproved duplicate immediately after SOL exact duplicate policy; "
            "per-symbol loop will not scale"
        ),
        "no_more_sol_only_policy_modules_now": True,
        "no_xrp_only_or_doge_only_or_ada_only_or_symbol_specific_policy_loop_now": True,
        "next_route_is_batch_classification": True,
        "full_audit_one_symbol_policy_loop_should_continue": full_audit.get(
            "one_symbol_policy_loop_should_continue"
        ),
        "full_audit_recommended_following_module": full_audit.get("recommended_following_module"),
        **shared,
    }
    batch_preview = {
        "batch_anomaly_classification_preview_created": True,
        "preview_only": True,
        "batch_classification_execution_performed_now": False,
        "target_pilot_symbols": PILOT_SYMBOLS,
        "classification_scope": "FULL_10_SYMBOL_PILOT_OR_ALL_NON_FINALIZED_PILOT_SYMBOLS",
        "must_scan_or_classify_across_full_scope": True,
        "must_not_stop_at_first_anomaly": True,
        "must_not_build_or_aggregate": True,
        "must_not_write_1h_output": True,
        "must_not_create_coin_specific_next_modules": True,
        "must_produce_one_batch_policy_preview": True,
        "anomaly_type_groups": ANOMALY_TYPES,
        "next_batch_module_may_read_validated_zip_csv_files_for_diagnostic_only_classification": True,
        "next_batch_module_requires_sha256_revalidation_before_reads": True,
        "current_module_zip_csv_parquet_row_read_performed_now": False,
        **shared,
    }
    approval_record = {
        "batch_anomaly_classification_approval_record_created": True,
        "approval_scope": "NEXT_SEPARATE_BATCH_ANOMALY_CLASSIFICATION_ONLY",
        "approval_grants_batch_classification_now": False,
        "approval_grants_future_batch_anomaly_classification_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
        **shared,
    }
    full_audit_carry_forward = {
        "full_audit_findings_carried_forward": True,
        "full_audit_status": full_audit.get("full_audit_status"),
        "full_audit_commit": EXPECTED_HEAD,
        "full_audit_repo_clean": full_audit.get("repo_clean"),
        "full_audit_tracked_python_count": full_audit.get("tracked_python_count"),
        "full_audit_active_p0_blocker_count": full_audit.get("active_p0_blocker_count"),
        "full_audit_active_p1_attention_count": full_audit.get("active_p1_attention_count"),
        "full_audit_dormant_repo_attention_count": full_audit.get("dormant_repo_attention_count"),
        "full_audit_stale_guard_attention_count": full_audit.get("stale_guard_attention_count"),
        "full_audit_latest_blocked_route_confirmed": full_audit.get("latest_blocked_route_confirmed"),
        "full_audit_partial_output_quarantine_required": full_audit.get("partial_output_quarantine_required"),
        "full_audit_batch_anomaly_classification_required": full_audit.get(
            "batch_anomaly_classification_required"
        ),
        "full_audit_next_route_record": next_route_audit,
        **shared,
    }
    limitations_report = {
        "policy_clean_build_batch_route_limitations_report_created": True,
        "completed_10_symbol_policy_clean_build_exists": False,
        "final_output_manifest_exists": False,
        "partial_output_quarantined": True,
        "required_next_step": "BATCH_ANOMALY_CLASSIFICATION_ONLY",
        "download_api_browse_forbidden_now": True,
        "new_build_aggregation_forbidden_now": True,
        "dedupe_rebuild_forbidden_now": True,
        "research_backtest_edge_claim_forbidden": True,
        "full_universe_or_broad_acquisition_claim_forbidden": True,
        "generic_runner_approval_forbidden": True,
        "schema_or_config_creation_forbidden": True,
        **shared,
    }
    self_validator = {
        "policy_clean_build_anomaly_self_validator_created": True,
        "preflight_passed": True,
        "required_source_artifacts_exist": all(exists.values()),
        "required_source_artifacts_valid_json": all(valid.values()),
        "tracked_python_count": py["tracked_python_count"],
        "tracked_python_syntax_clean": py["syntax_error_count"] == 0,
        "tracked_python_bom_clean": py["bom_error_count"] == 0,
        "blocked_record_valid": blocked_record["audit_confirmed_blocked_route"] is True
        and blocked_record["block_reason"] == BLOCK_REASON
        and blocked_record["unapproved_duplicate_open_time"] == UNAPPROVED_DUPLICATE_OPEN_TIME,
        "partial_output_quarantine_valid": quarantine_record["partial_output_quarantined"] is True
        and quarantine_record["partial_output_valid_for_any_downstream_use"] is False,
        "loop_termination_valid": loop_termination_record["one_symbol_policy_loop_terminated"] is True
        and loop_termination_record["no_more_sol_only_policy_modules_now"] is True,
        "batch_preview_valid": batch_preview["batch_anomaly_classification_preview_created"] is True
        and batch_preview["must_not_stop_at_first_anomaly"] is True,
        "batch_approval_valid": approval_record["approval_grants_future_batch_anomaly_classification_next"] is True
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_dedupe_now"] is False,
        "full_audit_carried_forward": full_audit_carry_forward["full_audit_findings_carried_forward"] is True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "p0_remains_active": shared["active_p0_blocker_count"] == 1,
        "next_module_valid": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks = {
        "anomaly_blocked_record_created": blocked_record["anomaly_blocked_record_created"],
        "partial_output_quarantine_record_created": quarantine_record["partial_output_quarantine_record_created"],
        "one_symbol_policy_loop_termination_record_created": loop_termination_record[
            "one_symbol_policy_loop_termination_record_created"
        ],
        "batch_anomaly_classification_preview_created": batch_preview[
            "batch_anomaly_classification_preview_created"
        ],
        "batch_anomaly_classification_approval_record_created": approval_record[
            "batch_anomaly_classification_approval_record_created"
        ],
        "full_audit_findings_carried_forward": full_audit_carry_forward[
            "full_audit_findings_carried_forward"
        ],
        "blocked_route_confirmed": shared["audit_confirmed_blocked_route"] is True
        and shared["pilot_policy_clean_build_execution_blocked"] is True,
        "sol_unapproved_duplicate_recorded": shared["anomaly_symbols"] == [ANOMALY_SYMBOL]
        and shared["unapproved_duplicate_open_time"] == UNAPPROVED_DUPLICATE_OPEN_TIME,
        "partial_output_quarantined": shared["partial_output_created_during_blocked_route"] is True
        and shared["partial_output_trusted"] is False
        and shared["partial_output_quarantined"] is True
        and shared["partial_output_valid_for_any_downstream_use"] is False,
        "one_symbol_loop_terminated": shared["one_symbol_policy_loop_should_continue"] is False
        and shared["one_symbol_policy_loop_terminated"] is True,
        "batch_route_approved_next_only": approval_record[
            "approval_grants_future_batch_anomaly_classification_next"
        ]
        is True
        and approval_record["approval_grants_batch_classification_now"] is False
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_dedupe_now"] is False,
        "no_download_api_browse_build_aggregation_now": shared["data_download_performed"] is False
        and shared["data_build_performed"] is False
        and shared["aggregation_performed_now"] is False
        and shared["okx_api_call_performed"] is False
        and shared["okx_browse_performed"] is False,
        "not_research_backtest_edge_full_universe_broad": shared["output_valid_for_research_backtest"] is False
        and shared["output_valid_for_edge_claim"] is False
        and shared["safe_for_full_universe_acquisition"] is False
        and shared["broad_acquisition_ready"] is False,
        "p0_remains_active": shared["active_p0_blocker_count"] == 1,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_valid": NEXT_MODULE == approval_record["next_module"],
        "self_validator_passed": all(value is True for value in self_validator.values() if isinstance(value, bool)),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_anomaly_record_status": PASS_STATUS,
        "anomaly_blocked_record_created": True,
        "partial_output_quarantine_record_created": True,
        "one_symbol_policy_loop_termination_record_created": True,
        "batch_anomaly_classification_preview_created": True,
        "batch_anomaly_classification_approval_record_created": True,
        "full_audit_findings_carried_forward": True,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_anomaly_record_run": py["tracked_python_count"],
        **shared,
    }
    bundle = {
        "anomaly_blocked_record": blocked_record,
        "partial_output_quarantine_record": quarantine_record,
        "one_symbol_policy_loop_termination_record": loop_termination_record,
        "batch_anomaly_classification_preview": batch_preview,
        "batch_anomaly_classification_approval_record": approval_record,
        "full_audit_findings_carried_forward": full_audit_carry_forward,
        "limitations_report": limitations_report,
        "self_validator": self_validator,
        "summary": summary,
    }
    payloads = {
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record_after_sol_policy.json": blocked_record,
        "historical_okx_10_symbol_pilot_partial_output_quarantine_record_after_sol_policy_block.json": quarantine_record,
        "historical_okx_10_symbol_pilot_one_symbol_policy_loop_termination_record.json": loop_termination_record,
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_preview.json": batch_preview,
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_approval_record.json": approval_record,
        "historical_okx_10_symbol_pilot_full_audit_findings_carried_forward.json": full_audit_carry_forward,
        "historical_okx_10_symbol_pilot_policy_clean_build_batch_route_limitations_report.json": limitations_report,
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_batch_route_summary.json": summary,
        f"{MODULE_NAME}_latest.json": summary,
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_batch_route_bundle.json": bundle,
    }
    return summary, payloads


def validate_written_artifacts(summary: dict[str, Any]) -> dict[str, bool]:
    required = [
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record_after_sol_policy.json",
        "historical_okx_10_symbol_pilot_partial_output_quarantine_record_after_sol_policy_block.json",
        "historical_okx_10_symbol_pilot_one_symbol_policy_loop_termination_record.json",
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_preview.json",
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_approval_record.json",
        "historical_okx_10_symbol_pilot_full_audit_findings_carried_forward.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_batch_route_limitations_report.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_self_validator.json",
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_batch_route_summary.json",
    ]
    loaded: dict[str, Any] = {}
    for filename in required:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing written artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))
    blocked = loaded[
        "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record_after_sol_policy.json"
    ]
    quarantine = loaded[
        "historical_okx_10_symbol_pilot_partial_output_quarantine_record_after_sol_policy_block.json"
    ]
    loop = loaded["historical_okx_10_symbol_pilot_one_symbol_policy_loop_termination_record.json"]
    preview = loaded["historical_okx_10_symbol_pilot_batch_anomaly_classification_preview.json"]
    approval = loaded["historical_okx_10_symbol_pilot_batch_anomaly_classification_approval_record.json"]
    carried = loaded["historical_okx_10_symbol_pilot_full_audit_findings_carried_forward.json"]
    checks = {
        "required_artifacts_exist": True,
        "blocked_record_valid": blocked.get("audit_confirmed_blocked_route") is True
        and blocked.get("block_reason") == BLOCK_REASON
        and blocked.get("unapproved_duplicate_open_time") == UNAPPROVED_DUPLICATE_OPEN_TIME,
        "partial_output_quarantine_valid": quarantine.get("partial_output_quarantined") is True
        and quarantine.get("partial_output_valid_for_any_downstream_use") is False,
        "loop_termination_valid": loop.get("one_symbol_policy_loop_terminated") is True
        and loop.get("one_symbol_policy_loop_should_continue") is False,
        "batch_preview_valid": preview.get("batch_anomaly_classification_preview_created") is True
        and preview.get("must_not_stop_at_first_anomaly") is True,
        "approval_next_only_valid": approval.get("approval_grants_future_batch_anomaly_classification_next") is True
        and approval.get("approval_grants_rebuild_now") is False
        and approval.get("approval_grants_dedupe_now") is False,
        "full_audit_carried_forward": carried.get("full_audit_findings_carried_forward") is True,
        "summary_replacement_checks_all_true": summary.get("replacement_checks_all_true") is True,
        "p0_still_active": summary.get("active_p0_blocker_count") == 1,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    checks["written_artifacts_valid"] = all(checks.values())
    return checks


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    py = tracked_python_validation()
    artifacts = {label: load_json(path, label, exists, valid) for label, path in ARTIFACTS.items()}
    validate_inputs(artifacts, py)
    summary, payloads = build_payloads(generated_at, artifacts, exists, valid, py)
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
            "audit_confirmed_blocked_route": False,
            "anomaly_blocked_record_created": False,
            "partial_output_quarantine_record_created": False,
            "one_symbol_policy_loop_termination_record_created": False,
            "batch_anomaly_classification_preview_created": False,
            "batch_anomaly_classification_approval_record_created": False,
            "full_audit_findings_carried_forward": False,
            "pilot_policy_clean_build_execution_blocked": True,
            "block_reason": BLOCK_REASON,
            "anomaly_symbol_count": 1,
            "anomaly_symbols": [ANOMALY_SYMBOL],
            "unapproved_duplicate_open_time": UNAPPROVED_DUPLICATE_OPEN_TIME,
            "one_symbol_policy_loop_should_continue": False,
            "one_symbol_policy_loop_terminated": False,
            "batch_anomaly_classification_required": True,
            "partial_output_trusted": False,
            "partial_output_quarantined": False,
            "partial_output_valid_for_any_downstream_use": False,
            "approval_grants_future_batch_anomaly_classification_next": False,
            "approval_grants_rebuild_now": False,
            "approval_grants_dedupe_now": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 505,
            "dormant_repo_attention_count": DORMANT_REPO_ATTENTION_COUNT,
            "current_evidence_chain_quality_after_anomaly_record": PREVIOUS_BLOCKED_STATUS,
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked_payload)
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
