#!/usr/bin/env python3
"""Repo-only partial-output forensic validation preview after resumable plan.

This module creates the contract for a future forensic validation execution.
It does not full-read or validate the partial output, promote it, rerun the
build, execute validators, run strategy search, generate candidates, claim edge,
or delete/quarantine/overwrite the partial output.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_after_resumable_plan_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_after_resumable_plan_v1"
)

EXPECTED_HEAD = "5d97522d9a64dc0ea29635e84b1d0904978e9eea"
RESUMABLE_PLAN_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_after_stall_diagnostic_v1"
)
RESUMABLE_PLAN = RESUMABLE_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan.json"
STALL_DIAGNOSTIC_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_stall_diagnostic_after_stalled_record_v1"
)
STALL_DIAGNOSTIC = STALL_DIAGNOSTIC_DIR / "repo_only_okx_88_symbol_1h_panel_revised_build_stall_diagnostic.json"
STALLED_RECORD_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record_v1"
)
STALLED_RECORD = (
    STALLED_RECORD_DIR
    / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record.json"
)
RETRY_PREVIEW_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_after_date_policy_redesign_v1"
)
RETRY_PREVIEW = RETRY_PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview.json"
DATE_POLICY_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_after_boundary_reconciliation_v1"
)
DATE_POLICY = DATE_POLICY_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign.json"

PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FORENSIC_VALIDATION_PREVIEW_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FORENSIC_VALIDATION_PREVIEW_REVIEW_REQUIRED"
NEXT_PASS_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_after_preview_v1.py"
)
NEXT_BLOCKED_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_blocked_record_v1.py"
)
FUTURE_PASS_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_after_forensic_validation_v1.py"
)
FUTURE_FAIL_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_safe_overwrite_or_resume_plan_after_failed_forensic_validation_v1.py"
)
FUTURE_BLOCKED_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_blocked_record_v1.py"
)
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_PARTIAL_OUTPUT_FORENSIC_VALIDATION_PREVIEW_READY_EXECUTION_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_PARTIAL_OUTPUT_FORENSIC_VALIDATION_PREVIEW_BLOCKED_REVIEW_REQUIRED"

EXPECTED_RESUMABLE_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_RESUMABLE_EXECUTION_PLAN_READY"
EXPECTED_OUTPUT_1H_ROW_COUNT = 1_802_944
EXPECTED_SYMBOL_COUNT = 88
EXPECTED_ROWS_PER_SYMBOL = 20_488
EXPECTED_MIN_TIMESTAMP = "2023-07-01T00:00:00Z"
EXPECTED_MAX_TIMESTAMP_EXCLUSIVE = "2025-10-31T16:00:00Z"
EXPECTED_MAX_TIMESTAMP_IF_BUCKET_STARTS = "2025-10-31T15:00:00Z"
EXPECTED_TAIL_SYMBOL = "ZRX-USDT-SWAP"
EXPECTED_STALL_CAUSE = "PROCESS_INTERRUPTED_OR_BROWSER_CODEX_STALL"
EXPECTED_ROUTE = "PARTIAL_OUTPUT_FORENSIC_VALIDATION_PREVIEW_NEXT"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO.as_posix()}", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_suffix = TOOL_REL.as_posix()
    unexpected = [
        line
        for line in lines
        if not line.replace("\\", "/").endswith(allowed_suffix)
    ]
    return not unexpected, unexpected


def load_input(label: str, path: Path, errors: dict[str, str]) -> dict[str, Any]:
    try:
        return read_json(path)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        errors[label] = f"{path}: {exc}"
        return {}


def file_metadata_only(path_text: Any) -> dict[str, Any]:
    if not isinstance(path_text, str) or not path_text:
        return {"exists": False, "metadata_error": "missing path text", "path": path_text}
    path = Path(path_text)
    try:
        stat = path.stat()
    except OSError as exc:
        return {"exists": False, "metadata_error": str(exc), "path": str(path)}
    modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0)
    return {
        "exists": path.is_file(),
        "modified_time": modified.isoformat().replace("+00:00", "Z"),
        "path": str(path),
        "size_bytes": stat.st_size,
    }


def resumable_plan_confirmed(plan: dict[str, Any]) -> bool:
    return (
        plan.get("okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_status")
        == EXPECTED_RESUMABLE_STATUS
        and plan.get("resumable_execution_plan_created") is True
        and plan.get("stall_diagnostic_confirmed") is True
        and plan.get("partial_output_exists") is True
        and plan.get("partial_output_valid") is False
        and plan.get("partial_output_must_not_be_used_for_strategy_search") is True
        and plan.get("partial_output_tail_last_symbol_detected") == EXPECTED_TAIL_SYMBOL
        and plan.get("suspected_stall_cause_class") == EXPECTED_STALL_CAUSE
        and plan.get("preferred_recovery_route") == EXPECTED_ROUTE
        and plan.get("partial_output_forensic_validation_required") is True
        and plan.get("future_partial_output_forensic_validation_preview_allowed_next") is True
        and plan.get("future_safe_overwrite_or_resume_plan_allowed_next") is False
        and plan.get("direct_build_rerun_allowed_now") is False
        and plan.get("partial_output_validation_allowed_now") is False
        and plan.get("partial_output_promotion_allowed_now") is False
        and plan.get("partial_output_cleanup_allowed_now") is False
        and plan.get("partial_output_overwrite_allowed_now") is False
        and plan.get("strategy_search_allowed_now") is False
        and plan.get("retry_strategy_search_allowed_now") is False
        and plan.get("candidate_generation_allowed_now") is False
        and plan.get("edge_claim_allowed_now") is False
        and plan.get("revised_build_rerun_performed") is False
        and plan.get("validator_executed") is False
        and plan.get("strategy_search_executed") is False
        and plan.get("candidate_generation_performed") is False
        and plan.get("edge_claim_performed") is False
        and plan.get("replacement_checks_all_true") is True
    )


def expected_checklist() -> dict[str, Any]:
    return {
        "partial_output_file_exists": True,
        "partial_output_file_readable": True,
        "schema_matches_expected_revised_non_holdout_output_schema": True,
        "row_count_equals": EXPECTED_OUTPUT_1H_ROW_COUNT,
        "symbol_count_equals": EXPECTED_SYMBOL_COUNT,
        "every_symbol_row_count_equals": EXPECTED_ROWS_PER_SYMBOL,
        "duplicate_symbol_hour_count_equals": 0,
        "output_min_timestamp_equals": EXPECTED_MIN_TIMESTAMP,
        "output_max_timestamp_less_than": EXPECTED_MAX_TIMESTAMP_EXCLUSIVE,
        "expected_max_timestamp_if_hour_bucket_starts": EXPECTED_MAX_TIMESTAMP_IF_BUCKET_STARTS,
        "no_timestamp_before_min": EXPECTED_MIN_TIMESTAMP,
        "no_timestamp_at_or_after_max_exclusive": EXPECTED_MAX_TIMESTAMP_EXCLUSIVE,
        "no_timestamp_at_or_after": "2025-11-01T00:00:00Z",
        "boundary_buffer_rows_written_count_equals": 0,
        "sealed_holdout_rows_written_count_equals": 0,
        "numeric_sanity_valid": True,
        "no_nan_or_inf_in_required_numeric_columns": True,
        "negative_volume_count_equals": 0,
        "ohlc_consistency_valid": True,
        "complete_1h_plus_incomplete_1h_equals_total_rows": True,
        "output_physically_excludes_sealed_holdout": True,
        "output_physically_excludes_boundary_buffer": True,
        "provenance_manifest_reconstructable_only_if_validation_passes": True,
        "output_valid_for_strategy_search_after_forensic_validation_may_become_true_only_if_all_checks_pass": True,
        "output_valid_for_edge_claim_must_remain_false": True,
    }


def forbidden_future_execution_actions() -> dict[str, bool]:
    return {
        "must_not_run_strategy_search": True,
        "must_not_generate_candidates": True,
        "must_not_claim_edge": True,
        "must_not_access_sealed_holdout": True,
        "must_not_read_current_all_in_one_1h_panel": True,
        "must_not_read_original_1m_source_files": True,
        "must_not_rerun_build": True,
        "must_not_patch_existing_tracked_files": True,
    }


def build_outputs() -> dict[str, dict[str, Any]]:
    head = git(["rev-parse", "HEAD"])
    top_level = git(["rev-parse", "--show-toplevel"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    load_errors: dict[str, str] = {}
    plan = load_input("resumable_execution_plan", RESUMABLE_PLAN, load_errors)
    diagnostic = load_input("stall_diagnostic", STALL_DIAGNOSTIC, load_errors)
    stalled_record = load_input("stalled_record", STALLED_RECORD, load_errors)
    retry_preview = load_input("revised_build_retry_preview", RETRY_PREVIEW, load_errors)
    date_policy = load_input("date_policy_redesign", DATE_POLICY, load_errors)

    metadata = file_metadata_only(diagnostic.get("partial_output_path"))
    plan_confirmed = resumable_plan_confirmed(plan)
    partial_output_exists = plan.get("partial_output_exists") is True and metadata.get("exists") is True
    partial_output_valid = plan.get("partial_output_valid")
    partial_blocked_for_strategy = plan.get("partial_output_must_not_be_used_for_strategy_search") is True

    future_checks = expected_checklist()
    approval = {
        "approval_grants_forensic_validation_preview_now": True,
        "approval_grants_future_partial_output_forensic_validation_execution_next": True,
        "approval_grants_partial_output_validation_now": False,
        "approval_grants_partial_output_promotion_now": False,
        "approval_grants_build_rerun_now": False,
        "approval_grants_validator_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_cleanup_now": False,
    }
    current_action_state = {
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "full_1h_panel_read_performed": False,
        "current_all_in_one_panel_read_performed": False,
        "original_source_full_csv_read_performed": False,
        "partial_output_full_read_performed": False,
        "revised_build_rerun_performed": False,
        "forensic_validation_executed": False,
        "validator_executed": False,
        "strategy_search_executed": False,
        "candidate_generation_performed": False,
        "edge_claim_performed": False,
    }
    route_policy = {
        "future_if_validation_passes": {
            "partial_output_forensic_validation_passed": True,
            "partial_output_promotable_to_validated_non_holdout_view": True,
            "output_valid_for_strategy_search_after_forensic_validation": True,
            "output_valid_for_edge_claim": False,
            "next_module": FUTURE_PASS_MODULE,
        },
        "future_if_any_core_check_fails": {
            "partial_output_forensic_validation_passed": False,
            "partial_output_valid": False,
            "output_valid_for_strategy_search_after_forensic_validation": False,
            "next_module": FUTURE_FAIL_MODULE,
        },
        "future_if_validation_execution_blocked": {
            "next_module": FUTURE_BLOCKED_MODULE,
        },
    }

    validation_contract = {
        "contract_scope": "future forensic validation execution only",
        "future_forensic_validation_must_check": future_checks,
        "future_forensic_validation_must_not": forbidden_future_execution_actions(),
        "output_valid_for_edge_claim_must_remain_false": True,
        "output_valid_for_strategy_search_after_forensic_validation_may_be_true_only_after_all_checks_pass": True,
        "pass_fail_policy": route_policy,
        "preview_module_did_not_execute_checks_now": True,
    }

    replacement_checks = {
        "correct_repo_path_confirmed": top_level == REPO.as_posix(),
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "repo_clean_except_current_tool": repo_clean,
        "resumable_execution_plan_confirmed": plan_confirmed,
        "required_input_artifacts_loaded": not load_errors and bool(diagnostic) and bool(stalled_record) and bool(retry_preview) and bool(date_policy),
        "partial_output_exists_metadata_only": partial_output_exists,
        "partial_output_remains_invalid": partial_output_valid is False,
        "partial_output_not_strategy_search_usable": partial_blocked_for_strategy,
        "preferred_recovery_route_confirmed": plan.get("preferred_recovery_route") == EXPECTED_ROUTE,
        "future_execution_allowed_next_only": approval["approval_grants_future_partial_output_forensic_validation_execution_next"] is True
        and plan.get("partial_output_validation_allowed_now") is False,
        "validation_not_executed_now": current_action_state["forensic_validation_executed"] is False
        and current_action_state["validator_executed"] is False,
        "partial_output_not_full_read_now": current_action_state["partial_output_full_read_performed"] is False,
        "partial_output_not_promoted_now": approval["approval_grants_partial_output_promotion_now"] is False,
        "build_not_rerun_now": current_action_state["revised_build_rerun_performed"] is False,
        "strategy_candidate_edge_blocked": (
            current_action_state["strategy_search_executed"] is False
            and current_action_state["candidate_generation_performed"] is False
            and current_action_state["edge_claim_performed"] is False
        ),
        "no_forbidden_panel_or_source_reads": (
            current_action_state["full_1h_panel_read_performed"] is False
            and current_action_state["current_all_in_one_panel_read_performed"] is False
            and current_action_state["original_source_full_csv_read_performed"] is False
        ),
        "validation_contract_created": bool(validation_contract),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    preview = {
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "build_rerun_allowed_now": False,
        "cleanup_allowed_now": False,
        "created_at_utc": now_utc(),
        "current_evidence_chain_quality_after_forensic_validation_preview": quality,
        "expected_revised_max_timestamp_exclusive": EXPECTED_MAX_TIMESTAMP_EXCLUSIVE,
        "expected_revised_min_timestamp": EXPECTED_MIN_TIMESTAMP,
        "expected_revised_output_1h_row_count": EXPECTED_OUTPUT_1H_ROW_COUNT,
        "expected_revised_rows_per_symbol": EXPECTED_ROWS_PER_SYMBOL,
        "expected_revised_symbol_count": EXPECTED_SYMBOL_COUNT,
        "forensic_validation_execution_allowed_now": False,
        "forensic_validation_preview_created": replacement_checks_all_true,
        "future_forensic_validation_execution_allowed_next": replacement_checks_all_true,
        "future_forensic_validation_required": True,
        "future_if_validation_fails_next_module": FUTURE_FAIL_MODULE,
        "future_if_validation_passes_next_module": FUTURE_PASS_MODULE,
        "load_errors": load_errors,
        "next_module": next_module,
        "okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_status": status,
        "partial_output_exists": partial_output_exists,
        "partial_output_metadata_only": metadata,
        "partial_output_must_not_be_used_for_strategy_search": partial_blocked_for_strategy,
        "partial_output_promotion_allowed_now": False,
        "partial_output_tail_last_symbol_detected": plan.get("partial_output_tail_last_symbol_detected"),
        "partial_output_valid": partial_output_valid,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "resumable_execution_plan_confirmed": plan_confirmed,
        "suspected_stall_cause_class": plan.get("suspected_stall_cause_class"),
        "tracked_python_count_at_forensic_validation_preview_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_contract_created": bool(validation_contract),
        "validation_must_check_complete_incomplete_reconciliation": True,
        "validation_must_check_duplicates": True,
        "validation_must_check_no_boundary_buffer": True,
        "validation_must_check_no_sealed_holdout": True,
        "validation_must_check_numeric_sanity": True,
        "validation_must_check_ohlc_sanity": True,
        "validation_must_check_per_symbol_counts": True,
        "validation_must_check_row_count": True,
        "validation_must_check_schema": True,
        "validation_must_check_symbol_count": True,
        "validation_must_check_timestamp_bounds": True,
        "strategy_search_allowed_now": False,
        "retry_strategy_search_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
    }
    preview.update(approval)
    preview.update(current_action_state)

    checklist = {
        **preview,
        "future_forensic_validation_checklist": future_checks,
        "checklist_is_contract_only_no_execution_now": True,
    }
    pass_fail_policy = {
        **preview,
        "future_pass_fail_policy": route_policy,
        "core_check_failure_definition": "any required future forensic validation check fails",
    }
    future_routes = {
        **preview,
        "expected_next_module_if_preview_passes": NEXT_PASS_MODULE,
        "expected_next_module_if_preview_blocked": NEXT_BLOCKED_MODULE,
        "future_routes": route_policy,
    }
    approval_record = {
        **preview,
        **approval,
        "approval_scope": "future forensic validation execution only",
    }
    self_validator = {
        **preview,
        "artifact_count_expected": 7,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_contract.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_validation_checklist.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_pass_fail_policy.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_future_routes.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
        "self_validation_result": replacement_checks_all_true,
    }

    return {
        "preview": preview,
        "contract": {**preview, **validation_contract},
        "checklist": checklist,
        "pass_fail_policy": pass_fail_policy,
        "future_routes": future_routes,
        "approval_record": approval_record,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, dict[str, Any]]) -> None:
    files = {
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview.json": outputs["preview"],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_contract.json": outputs["contract"],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_validation_checklist.json": outputs["checklist"],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_pass_fail_policy.json": outputs["pass_fail_policy"],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_future_routes.json": outputs["future_routes"],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_approval_record.json": outputs[
            "approval_record"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_self_validator.json": outputs[
            "self_validator"
        ],
    }
    for filename, payload in files.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["preview"], indent=2, sort_keys=True))
    return 0 if outputs["preview"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
