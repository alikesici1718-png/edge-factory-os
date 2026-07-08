from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_after_batch_anomaly_classification_v1"
TARGET_RELATIVE_PATH = Path("tools") / f"{MODULE_NAME}.py"
EXPECTED_HEAD_PREFIX = "40fe0df"
EXPECTED_PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_ANOMALY_CLASSIFIED_BATCH_POLICY_READY"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_APPROVED_POLICY_CLEAN_BUILD_READY"
FAIL_STATUS = "FAIL_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_FAILED_REVIEW"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_after_batch_policy_v1.py"
FAIL_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_blocked_record_after_classification_v1.py"
CLASSIFICATION_MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_anomaly_classification_after_policy_clean_build_block_v1"
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
CLASSIFICATION_DIR = EDGE_LAB_ROOT / CLASSIFICATION_MODULE_NAME
CURRENT_EVIDENCE_CHAIN_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_APPROVED_POLICY_CLEAN_BUILD_READY"

POLICIES = {
    "exact_duplicate_policy": "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROWS_KEEP_ONE_CANONICAL_ROW",
    "material_conflict_policy": "QUARANTINE_ALL_ROWS_IN_MATERIAL_CONFLICT_OPEN_TIME_GROUP",
    "missing_minute_policy": "NO_FILL_MARK_AFFECTED_HOUR_INCOMPLETE_OR_EXCLUDE_FROM_COMPLETE_CLAIMS",
    "confirm_only_conflict_policy": "DO_NOT_RESOLVE_WITHOUT_SEPARATE_POLICY",
    "schema_mismatch_policy": "FAIL_CLOSED_AFFECTED_SYMBOL",
    "symbol_mismatch_policy": "FAIL_CLOSED_AFFECTED_SYMBOL",
    "unknown_anomaly_policy": "FAIL_CLOSED_AFFECTED_SYMBOL",
}

EXPECTED_COUNTS = {
    "pilot_symbol_count": 10,
    "symbols_policy_covered_count": 10,
    "total_raw_rows_scanned": 15166462,
    "total_duplicate_group_count": 3244,
    "total_duplicate_extra_row_count": 3262,
    "total_exact_duplicate_group_count": 3234,
    "total_exact_duplicate_extra_rows_to_drop": 3252,
    "total_material_conflict_group_count": 10,
    "total_material_conflict_rows_to_quarantine": 20,
    "total_missing_minute_count": 4800,
    "expected_clean_source_rows_after_duplicate_and_conflict_policy": 15163190,
    "symbols_with_material_duplicate_conflict_count": 10,
    "symbols_with_missing_minutes_count": 10,
    "symbols_with_schema_mismatch_count": 0,
    "symbols_with_symbol_mismatch_count": 0,
    "symbols_with_unknown_count": 0,
}

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

REQUIRED_OUTPUTS = [
    "historical_okx_10_symbol_pilot_batch_policy.json",
    "historical_okx_10_symbol_pilot_batch_exact_duplicate_policy.json",
    "historical_okx_10_symbol_pilot_batch_material_conflict_quarantine_policy.json",
    "historical_okx_10_symbol_pilot_batch_missing_minute_incomplete_hour_policy.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_build_preview.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_build_approval_record.json",
    "historical_okx_10_symbol_pilot_batch_policy_limitations_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_self_validator.json",
    "historical_okx_10_symbol_pilot_batch_policy_summary.json",
]


class FailClosed(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FailClosed(f"Missing required classification artifact: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(name: str, payload: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get_nested(payload: dict[str, Any], *keys: str) -> Any:
    cursor: Any = payload
    for key in keys:
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(key)
    return cursor


def list_value(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    return value if isinstance(value, list) else []


def current_git_state() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    status_lines = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    tracked_python = run_git(["ls-files", "*.py"]).splitlines()
    dirty_unapproved = []
    allowed_path = TARGET_RELATIVE_PATH.as_posix()
    for line in status_lines:
        path = line[3:].strip().replace("\\", "/")
        if path != allowed_path:
            dirty_unapproved.append(line)
    return {
        "head": head,
        "head_prefix": head[:7],
        "repo_clean_before_tool_creation": len(status_lines) == 0,
        "status_lines": status_lines,
        "only_approved_tool_changed": not dirty_unapproved,
        "unapproved_status_lines": dirty_unapproved,
        "tracked_python_count": len(tracked_python),
        "tracked_python_paths": tracked_python,
    }


def validate_python(paths: list[str]) -> dict[str, Any]:
    syntax_errors: list[dict[str, Any]] = []
    bom_errors: list[str] = []
    candidate_paths = list(paths)
    target_posix = TARGET_RELATIVE_PATH.as_posix()
    if target_posix not in candidate_paths:
        candidate_paths.append(target_posix)
    for rel in candidate_paths:
        path = REPO_ROOT / rel
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            syntax_errors.append({"path": rel, "error": str(exc)})
    return {
        "tracked_python_count": len(paths),
        "checked_python_count_including_current_tool": len(candidate_paths),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_error_paths": bom_errors,
    }


def read_classification_artifacts() -> dict[str, Any]:
    return {
        "summary": load_json(CLASSIFICATION_DIR / "historical_okx_10_symbol_pilot_batch_anomaly_classification_summary.json"),
        "policy_preview": load_json(CLASSIFICATION_DIR / "historical_okx_10_symbol_pilot_batch_policy_preview.json"),
        "approval": load_json(CLASSIFICATION_DIR / "historical_okx_10_symbol_pilot_batch_policy_approval_record.json"),
        "per_symbol_table": load_json(CLASSIFICATION_DIR / "historical_okx_10_symbol_pilot_batch_per_symbol_anomaly_table.json"),
        "classification_report": load_json(CLASSIFICATION_DIR / "historical_okx_10_symbol_pilot_batch_anomaly_classification_report.json"),
    }


def validate_classification_inputs(artifacts: dict[str, Any], git_state: dict[str, Any], py_state: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    summary = artifacts["summary"]
    preview = artifacts["policy_preview"]
    approval = artifacts["approval"]
    per_symbol_table = artifacts["per_symbol_table"]

    if git_state["head_prefix"] != EXPECTED_HEAD_PREFIX:
        failures.append(f"HEAD mismatch: expected {EXPECTED_HEAD_PREFIX}, found {git_state['head']}")
    if not git_state["only_approved_tool_changed"]:
        failures.append(f"Repo has unapproved dirty paths: {git_state['unapproved_status_lines']}")
    if py_state["syntax_error_count"] != 0:
        failures.append("Python syntax errors detected")
    if py_state["bom_error_count"] != 0:
        failures.append("Python BOM errors detected")
    if summary.get("historical_data_acquisition_okx_10_symbol_pilot_batch_anomaly_classification_status") != EXPECTED_PREVIOUS_STATUS:
        failures.append("Previous batch classification status is not pass")
    if summary.get("next_module") != TARGET_RELATIVE_PATH.name:
        failures.append("Current next_module does not match this batch policy module")

    checks = {
        "pilot_symbol_count": summary.get("pilot_symbol_count"),
        "symbols_policy_covered_count": summary.get("symbols_classified_count"),
        "total_raw_rows_scanned": summary.get("total_raw_rows_scanned"),
        "total_duplicate_group_count": summary.get("total_duplicate_group_count"),
        "total_duplicate_extra_row_count": summary.get("total_duplicate_extra_row_count"),
        "total_exact_duplicate_group_count": summary.get("total_exact_duplicate_group_count"),
        "total_exact_duplicate_extra_rows_to_drop": summary.get("total_exact_duplicate_extra_rows"),
        "total_material_conflict_group_count": summary.get("total_material_conflict_group_count"),
        "total_material_conflict_rows_to_quarantine": summary.get("total_material_conflict_rows"),
        "total_missing_minute_count": summary.get("total_missing_minute_count"),
        "expected_clean_source_rows_after_duplicate_and_conflict_policy": preview.get("total_expected_clean_source_rows_after_policy"),
        "symbols_with_material_duplicate_conflict_count": len(list_value(summary, "symbols_with_material_duplicate_conflict")),
        "symbols_with_missing_minutes_count": len(list_value(summary, "symbols_with_missing_minutes")),
        "symbols_with_schema_mismatch_count": len(list_value(summary, "symbols_with_schema_mismatch")),
        "symbols_with_symbol_mismatch_count": len(list_value(summary, "symbols_with_symbol_mismatch")),
        "symbols_with_unknown_count": len(list_value(summary, "symbols_with_unknown")),
    }
    for key, expected in EXPECTED_COUNTS.items():
        if checks.get(key) != expected:
            failures.append(f"{key} mismatch: expected {expected}, found {checks.get(key)}")

    row_count = (
        per_symbol_table.get("symbol_count")
        or len(per_symbol_table.get("per_symbol_anomaly_table", []))
        or len(per_symbol_table.get("symbols", []))
    )
    if row_count != 10:
        failures.append(f"Per-symbol anomaly table does not cover all 10 symbols: {row_count}")
    if approval.get("approval_grants_future_batch_policy_next") is not True:
        failures.append("Prior approval does not grant future batch policy next")
    forbidden_true = [
        "data_download_performed",
        "data_build_performed",
        "aggregation_performed_now",
        "output_csv_created",
        "output_manifest_created",
        "okx_api_call_performed",
        "okx_browse_performed",
        "output_valid_for_research_backtest",
        "output_valid_for_edge_claim",
        "safe_for_full_universe_acquisition",
        "broad_acquisition_ready",
    ]
    for key in forbidden_true:
        if summary.get(key) is True or approval.get(key) is True:
            failures.append(f"Forbidden prior/current flag true: {key}")
    return failures


def common_policy_fields(status: str, replacement_checks_all_true: bool, failures: list[str]) -> dict[str, Any]:
    return {
        "historical_data_acquisition_okx_10_symbol_pilot_batch_policy_status": status,
        "module": TARGET_RELATIVE_PATH.name,
        "created_at_utc": utc_now(),
        "fail_closed_reasons": failures,
        "batch_policy_created": status == PASS_STATUS,
        "one_symbol_policy_loop_terminated": True,
        "pilot_symbol_count": 10,
        "symbols_policy_covered_count": 10,
        "pilot_symbols": PILOT_SYMBOLS,
        **EXPECTED_COUNTS,
        "complete_hour_count_precomputed": False,
        "complete_hour_count_requires_future_build_computation": True,
        "future_build_must_compute": [
            "affected_hour_count",
            "complete_1h_row_count",
            "incomplete_1h_row_count",
        ],
        **POLICIES,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "ohlcv_modification_allowed": False,
        "synthetic_fill_allowed": False,
        "forward_fill_allowed": False,
        "backfill_allowed": False,
        "batch_policy_clean_build_preview_created": status == PASS_STATUS,
        "batch_policy_clean_build_approval_record_created": status == PASS_STATUS,
        "approval_grants_batch_policy_now": status == PASS_STATUS,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_batch_policy_clean_build_next": status == PASS_STATUS,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "output_manifest_created": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "generic_runner_approved": False,
        "runtime_or_live_path_approved": False,
        "active_p0_blocker_count": 0 if status == PASS_STATUS else 1,
        "active_p1_attention_count": 505,
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_policy": CURRENT_EVIDENCE_CHAIN_QUALITY if status == PASS_STATUS else "BATCH_POLICY_FAILED_REVIEW",
        "next_module": NEXT_MODULE if status == PASS_STATUS else FAIL_NEXT_MODULE,
        "replacement_checks_all_true": replacement_checks_all_true,
    }


def build_artifacts(artifacts: dict[str, Any], git_state: dict[str, Any], py_state: dict[str, Any], failures: list[str]) -> dict[str, dict[str, Any]]:
    status = PASS_STATUS if not failures else FAIL_STATUS
    replacement_checks = {
        "current_head_guard_passed": git_state["head_prefix"] == EXPECTED_HEAD_PREFIX,
        "current_path_guard_passed": (REPO_ROOT / TARGET_RELATIVE_PATH).exists(),
        "repo_has_only_approved_tool_change": git_state["only_approved_tool_changed"],
        "classification_status_passed": artifacts["summary"].get("historical_data_acquisition_okx_10_symbol_pilot_batch_anomaly_classification_status") == EXPECTED_PREVIOUS_STATUS,
        "current_next_module_matches": artifacts["summary"].get("next_module") == TARGET_RELATIVE_PATH.name,
        "counts_match_batch_classification": not [failure for failure in failures if "mismatch" in failure],
        "complete_hour_count_not_precomputed": True,
        "future_build_computation_required": True,
        "no_fill_or_conflict_selection_allowed": True,
        "no_download_api_browse_build_aggregation_output": True,
        "no_research_backtest_edge_claim": True,
        "next_route_is_batch_policy_clean_build": True,
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not failures
    common = common_policy_fields(status, replacement_checks_all_true, failures)

    classification_snapshot = {
        "source_classification_module": CLASSIFICATION_MODULE_NAME,
        "source_status": artifacts["summary"].get("historical_data_acquisition_okx_10_symbol_pilot_batch_anomaly_classification_status"),
        "classification_counts_used_for_policy": EXPECTED_COUNTS,
        "classification_complete_hour_counts_not_adopted_as_final": True,
        "reason_complete_hour_counts_not_adopted": "Policy module does not compute or claim final complete-hour counts; future clean build must recompute from cleaned minute rows.",
    }

    batch_policy = {
        **common,
        "artifact_type": "batch_policy",
        "classification_snapshot": classification_snapshot,
        "policy_scope": "FULL_10_SYMBOL_PILOT_GENERALIZED_BATCH_POLICY",
        "no_symbol_specific_policy_module_created": True,
    }
    exact_policy = {
        **common,
        "artifact_type": "exact_duplicate_policy",
        "policy_decision": POLICIES["exact_duplicate_policy"],
        "rows_to_drop": EXPECTED_COUNTS["total_exact_duplicate_extra_rows_to_drop"],
        "keep_one_canonical_row_per_exact_duplicate_open_time": True,
        "canonical_row_selection_requires_all_canonical_fields_equal": True,
        "canonical_fields": ["instrument_name", "open", "high", "low", "close", "vol", "vol_ccy", "vol_quote", "open_time", "confirm"],
    }
    material_policy = {
        **common,
        "artifact_type": "material_conflict_quarantine_policy",
        "policy_decision": POLICIES["material_conflict_policy"],
        "material_conflict_groups_to_quarantine": EXPECTED_COUNTS["total_material_conflict_group_count"],
        "material_conflict_rows_to_quarantine": EXPECTED_COUNTS["total_material_conflict_rows_to_quarantine"],
        "never_choose_average_or_merge_conflicting_rows": True,
    }
    missing_policy = {
        **common,
        "artifact_type": "missing_minute_incomplete_hour_policy",
        "policy_decision": POLICIES["missing_minute_policy"],
        "missing_minutes_detected": EXPECTED_COUNTS["total_missing_minute_count"],
        "affected_hours_must_be_marked_complete_hour_false": True,
        "future_build_must_exclude_incomplete_hours_from_complete_output_claims": True,
        "all_hours_complete_claim_allowed": False,
        "complete_1h_row_count_claim_allowed_now": False,
    }
    build_preview = {
        **common,
        "artifact_type": "batch_policy_clean_build_preview",
        "future_execution_allowed_scope": "PILOT_POLICY_CLEAN_BUILD_ONLY_AFTER_THIS_POLICY",
        "future_execution_may_use_only_already_validated_zip_count": 10530,
        "future_execution_must_revalidate_sha256_before_csv_read": True,
        "future_execution_may_aggregate_clean_rows_into_utc_1h_candles": True,
        "future_execution_must_mark_hours_with_source_row_count_less_than_60_incomplete": True,
        "future_execution_must_fail_closed_on": [
            "schema_mismatch",
            "symbol_mismatch",
            "unknown_duplicate_group",
            "confirm_only_conflict_without_policy",
            "hash_or_provenance_mismatch",
            "unapproved_symbol_or_date",
            "synthetic_fill_forward_fill_or_backfill_attempt",
            "research_backtest_edge_full_universe_or_broad_acquisition_claim",
        ],
        "future_execution_must_write_per_symbol_audits": True,
    }
    approval = {
        **common,
        "artifact_type": "batch_policy_clean_build_approval_record",
        "approval_grants_batch_policy_now": status == PASS_STATUS,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_batch_policy_clean_build_next": status == PASS_STATUS,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
    }
    limitations = {
        **common,
        "artifact_type": "batch_policy_limitations_report",
        "limitations": [
            "No final complete-hour count is claimed by this policy module.",
            "No 1h output was created.",
            "No dedupe or quarantine execution was performed.",
            "No downstream research, backtest, edge, full-universe, or broad-acquisition readiness is granted.",
        ],
    }
    self_validator = {
        **common,
        "artifact_type": "batch_policy_self_validator",
        "replacement_checks": replacement_checks,
        "required_outputs": REQUIRED_OUTPUTS,
        "required_outputs_created": [],
        "python_validation": {
            "tracked_python_count": py_state["tracked_python_count"],
            "syntax_error_count": py_state["syntax_error_count"],
            "bom_error_count": py_state["bom_error_count"],
        },
        "git_validation": {
            "head": git_state["head"],
            "expected_head_prefix": EXPECTED_HEAD_PREFIX,
            "status_lines_before_run": git_state["status_lines"],
        },
    }
    summary = {
        **common,
        "artifact_type": "batch_policy_summary",
        "post_check_status": "PASS" if status == PASS_STATUS else "FAIL_CLOSED",
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "replacement_checks": replacement_checks,
    }

    return {
        "historical_okx_10_symbol_pilot_batch_policy.json": batch_policy,
        "historical_okx_10_symbol_pilot_batch_exact_duplicate_policy.json": exact_policy,
        "historical_okx_10_symbol_pilot_batch_material_conflict_quarantine_policy.json": material_policy,
        "historical_okx_10_symbol_pilot_batch_missing_minute_incomplete_hour_policy.json": missing_policy,
        "historical_okx_10_symbol_pilot_batch_policy_clean_build_preview.json": build_preview,
        "historical_okx_10_symbol_pilot_batch_policy_clean_build_approval_record.json": approval,
        "historical_okx_10_symbol_pilot_batch_policy_limitations_report.json": limitations,
        "historical_okx_10_symbol_pilot_batch_policy_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_batch_policy_summary.json": summary,
    }


def validate_written_outputs() -> None:
    missing = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise FailClosed(f"Missing required output artifacts after write: {missing}")
    summary = load_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_batch_policy_summary.json")
    if summary.get("replacement_checks_all_true") is not True:
        raise FailClosed("Self-validation failed: replacement_checks_all_true is not true")


def main() -> int:
    git_state = current_git_state()
    py_state = validate_python(git_state["tracked_python_paths"])
    artifacts = read_classification_artifacts()
    failures = validate_classification_inputs(artifacts, git_state, py_state)
    outputs = build_artifacts(artifacts, git_state, py_state, failures)
    for name, payload in outputs.items():
        write_json(name, payload)
    if failures:
        print(json.dumps(outputs["historical_okx_10_symbol_pilot_batch_policy_summary.json"], indent=2, sort_keys=True))
        return 1
    validate_written_outputs()
    print(json.dumps(outputs["historical_okx_10_symbol_pilot_batch_policy_summary.json"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
