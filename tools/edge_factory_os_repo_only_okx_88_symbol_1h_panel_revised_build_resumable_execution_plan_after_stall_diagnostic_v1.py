#!/usr/bin/env python3
"""Repo-only resumable execution plan after revised build stall diagnostic.

This module plans the next safe recovery route. It does not rerun the build,
execute forensic validation, validate partial output as usable, run strategy
search, patch tracked files, or delete/quarantine/overwrite partial output.
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
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_after_stall_diagnostic_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_after_stall_diagnostic_v1"
)

EXPECTED_HEAD = "fd2993261abd0cef2cb6512ae010ecf7ff2581de"
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
PREVIEW_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_after_date_policy_redesign_v1"
)
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview.json"
REDESIGN_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_after_boundary_reconciliation_v1"
)
REDESIGN = REDESIGN_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign.json"
ACCESS_PLAN_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1"
)
ACCESS_PLAN = ACCESS_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json"

PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_RESUMABLE_EXECUTION_PLAN_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_RESUMABLE_EXECUTION_PLAN_REVIEW_REQUIRED"
NEXT_PASS_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_after_resumable_plan_v1.py"
)
NEXT_FALLBACK_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_safe_overwrite_or_resume_plan_after_stall_diagnostic_v1.py"
)
NEXT_BLOCKED_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_blocked_record_v1.py"
)
PASS_QUALITY = (
    "OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_RESUMABLE_PLAN_READY_PARTIAL_FORENSIC_VALIDATION_PREVIEW_NEXT"
)
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_RESUMABLE_PLAN_BLOCKED_REVIEW_REQUIRED"

EXPECTED_OUTPUT_1H_ROW_COUNT = 1_802_944
EXPECTED_SYMBOL_COUNT = 88
EXPECTED_ROWS_PER_SYMBOL = 20_488
EXPECTED_MIN_TIMESTAMP = "2023-07-01T00:00:00Z"
EXPECTED_MAX_TIMESTAMP_EXCLUSIVE = "2025-10-31T16:00:00Z"


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
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(TOOL_REL.as_posix())]
    return not unexpected, unexpected


def load_input(label: str, path: Path, errors: dict[str, str]) -> dict[str, Any]:
    try:
        return read_json(path)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        errors[label] = f"{path}: {exc}"
        return {}


def diagnostic_confirmed(diagnostic: dict[str, Any]) -> bool:
    return (
        diagnostic.get("okx_88_symbol_1h_panel_revised_build_stall_diagnostic_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_STALL_DIAGNOSTIC_READY"
        and diagnostic.get("stall_diagnostic_performed") is True
        and diagnostic.get("stalled_record_confirmed") is True
        and diagnostic.get("partial_output_exists") is True
        and diagnostic.get("partial_output_valid") is False
        and diagnostic.get("partial_output_must_not_be_used_for_strategy_search") is True
        and diagnostic.get("partial_output_tail_last_symbol_detected") == "ZRX-USDT-SWAP"
        and diagnostic.get("suspected_stall_cause_class") == "PROCESS_INTERRUPTED_OR_BROWSER_CODEX_STALL"
        and diagnostic.get("approval_grants_future_resumable_execution_plan_next") is True
        and diagnostic.get("approval_grants_future_rsr_symbol_probe_next") is False
        and diagnostic.get("revised_build_rerun_performed") is False
        and diagnostic.get("validator_executed") is False
        and diagnostic.get("strategy_search_executed") is False
        and diagnostic.get("candidate_generation_performed") is False
        and diagnostic.get("edge_claim_performed") is False
        and diagnostic.get("replacement_checks_all_true") is True
    )


def build_outputs() -> dict[str, dict[str, Any]]:
    head = git(["rev-parse", "HEAD"])
    top_level = git(["rev-parse", "--show-toplevel"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    load_errors: dict[str, str] = {}
    diagnostic = load_input("stall_diagnostic", STALL_DIAGNOSTIC, load_errors)
    stalled_record = load_input("stalled_record", STALLED_RECORD, load_errors)
    preview = load_input("revised_build_retry_preview", PREVIEW, load_errors)
    redesign = load_input("date_policy_redesign", REDESIGN, load_errors)
    access_plan = load_input("holdout_safe_access_plan", ACCESS_PLAN, load_errors)

    stall_diagnostic_confirmed = diagnostic_confirmed(diagnostic)
    partial_output_exists = diagnostic.get("partial_output_exists") is True
    partial_output_valid = False
    partial_output_must_not_be_used_for_strategy_search = True
    tail_symbol = diagnostic.get("partial_output_tail_last_symbol_detected")
    cause_class = diagnostic.get("suspected_stall_cause_class")
    rsr_specific_issue_suspected = False
    option_a_selected = (
        stall_diagnostic_confirmed
        and partial_output_exists
        and tail_symbol == "ZRX-USDT-SWAP"
        and cause_class == "PROCESS_INTERRUPTED_OR_BROWSER_CODEX_STALL"
        and diagnostic.get("rsr_source_manifest_metadata_checked") is True
        and diagnostic.get("rsr_tiny_allowed_source_probe_performed") is False
    )
    preferred_recovery_route = (
        "PARTIAL_OUTPUT_FORENSIC_VALIDATION_PREVIEW_NEXT"
        if option_a_selected
        else "SAFE_OVERWRITE_OR_RESUME_PLAN_REQUIRED_AFTER_REVIEW"
    )
    next_module_if_ready = NEXT_PASS_MODULE if option_a_selected else NEXT_FALLBACK_MODULE

    partial_policy = {
        "partial_output_can_be_promoted_only_after_dedicated_validator": False,
        "partial_output_cleanup_allowed_now": False,
        "partial_output_delete_allowed_now": False,
        "partial_output_forensic_validation_required": True,
        "partial_output_must_not_be_used_for_strategy_search": partial_output_must_not_be_used_for_strategy_search,
        "partial_output_overwrite_allowed_now": False,
        "partial_output_promotion_allowed_now": False,
        "partial_output_quarantine_allowed_now": False,
        "partial_output_validation_allowed_now": False,
        "partial_output_valid": partial_output_valid,
    }
    forbidden_action_state = {
        "aggregation_performed_now": False,
        "broad_source_row_read_performed": False,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "current_all_in_one_panel_read_performed": False,
        "data_build_performed": False,
        "data_download_performed": False,
        "direct_build_rerun_allowed_now": False,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "full_1h_panel_read_performed": False,
        "retry_strategy_search_allowed_now": False,
        "revised_build_rerun_performed": False,
        "runtime_live_capital_allowed_now": False,
        "sealed_holdout_source_file_read_count": 0,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "validator_executed": False,
    }
    forensic_contract = {
        "expected_revised_max_timestamp_exclusive": EXPECTED_MAX_TIMESTAMP_EXCLUSIVE,
        "expected_revised_min_timestamp": EXPECTED_MIN_TIMESTAMP,
        "expected_revised_output_1h_row_count": EXPECTED_OUTPUT_1H_ROW_COUNT,
        "expected_revised_rows_per_symbol": EXPECTED_ROWS_PER_SYMBOL,
        "expected_revised_symbol_count": EXPECTED_SYMBOL_COUNT,
        "forensic_validation_must_check_duplicates": True,
        "forensic_validation_must_check_no_boundary_buffer": True,
        "forensic_validation_must_check_no_sealed_holdout": True,
        "forensic_validation_must_check_per_symbol_counts": True,
        "forensic_validation_must_check_row_count": True,
        "forensic_validation_must_check_schema": True,
        "forensic_validation_must_check_symbol_count": True,
        "forensic_validation_must_check_timestamp_bounds": True,
        "forensic_validation_must_not_mark_valid_by_assumption": True,
        "forensic_validation_must_not_run_strategy_search": True,
    }
    approval = {
        "approval_grants_build_rerun_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_cleanup_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_partial_output_forensic_validation_preview_next": option_a_selected,
        "approval_grants_future_safe_overwrite_or_resume_plan_next": False,
        "approval_grants_partial_output_promotion_now": False,
        "approval_grants_partial_output_validation_now": False,
        "approval_grants_resumable_plan_now": True,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "approval_grants_validator_now": False,
    }

    replacement_checks = {
        "correct_repo_path_confirmed": top_level == REPO.as_posix(),
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "repo_clean_except_current_tool": repo_clean,
        "stall_diagnostic_confirmed": stall_diagnostic_confirmed,
        "partial_output_exists": partial_output_exists,
        "partial_output_remains_invalid": partial_output_valid is False,
        "partial_output_not_strategy_search_usable": partial_output_must_not_be_used_for_strategy_search is True,
        "process_interruption_not_rsr_specific": cause_class == "PROCESS_INTERRUPTED_OR_BROWSER_CODEX_STALL"
        and rsr_specific_issue_suspected is False,
        "zrx_tail_observed": tail_symbol == "ZRX-USDT-SWAP",
        "option_a_selected": option_a_selected,
        "no_build_rerun_now": forbidden_action_state["direct_build_rerun_allowed_now"] is False
        and forbidden_action_state["revised_build_rerun_performed"] is False,
        "no_validator_now": forbidden_action_state["validator_executed"] is False
        and approval["approval_grants_validator_now"] is False,
        "no_strategy_candidate_edge": (
            forbidden_action_state["strategy_search_executed"] is False
            and forbidden_action_state["candidate_generation_performed"] is False
            and forbidden_action_state["edge_claim_performed"] is False
            and forbidden_action_state["strategy_search_allowed_now"] is False
            and forbidden_action_state["candidate_generation_allowed_now"] is False
            and forbidden_action_state["edge_claim_allowed_now"] is False
        ),
        "no_partial_output_cleanup_or_overwrite": (
            partial_policy["partial_output_cleanup_allowed_now"] is False
            and partial_policy["partial_output_delete_allowed_now"] is False
            and partial_policy["partial_output_quarantine_allowed_now"] is False
            and partial_policy["partial_output_overwrite_allowed_now"] is False
        ),
        "no_forbidden_panel_or_source_reads": (
            forbidden_action_state["current_all_in_one_panel_read_performed"] is False
            and forbidden_action_state["full_1h_panel_read_performed"] is False
            and forbidden_action_state["sealed_holdout_source_file_read_count"] == 0
            and forbidden_action_state["broad_source_row_read_performed"] is False
        ),
        "preview_redesign_metadata_available": bool(preview) and bool(redesign),
        "stalled_record_metadata_available": bool(stalled_record),
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = next_module_if_ready if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    plan = {
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "created_at_utc": now_utc(),
        "current_evidence_chain_quality_after_resumable_plan": quality,
        "expected_current_next_module_from_diagnostic": diagnostic.get("next_module"),
        "future_partial_output_forensic_validation_preview_allowed_next": option_a_selected,
        "future_safe_overwrite_or_resume_plan_allowed_next": False,
        "holdout_safe_access_plan_metadata_available": bool(access_plan),
        "load_errors": load_errors,
        "next_module": next_module,
        "okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_status": status,
        "partial_output_exists": partial_output_exists,
        "partial_output_tail_last_symbol_detected": tail_symbol,
        "preferred_recovery_route": preferred_recovery_route,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "resumable_execution_plan_created": replacement_checks_all_true,
        "rsr_specific_issue_suspected": rsr_specific_issue_suspected,
        "stall_diagnostic_confirmed": stall_diagnostic_confirmed,
        "suspected_stall_cause_class": cause_class,
        "tracked_python_count_at_resumable_plan_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
    }
    plan.update(partial_policy)
    plan.update(forbidden_action_state)
    plan.update(forensic_contract)
    plan.update(approval)

    route_decision = {
        **plan,
        "option_a_selected_reason": (
            "Partial output exists, remains invalid, tail metadata detected ZRX-USDT-SWAP, and diagnostic classified "
            "the stall as process/browser interruption rather than RSR source-data failure."
        ),
        "option_b_fallback_module": NEXT_FALLBACK_MODULE,
        "option_b_selected_now": False,
    }
    fallback_contract = {
        **plan,
        "fallback_allowed_now": False,
        "future_fallback_requires_explicit_approval": True,
        "safe_overwrite_or_resume_plan_must_use_per_symbol_checkpointing": True,
        "safe_overwrite_or_resume_plan_must_write_durable_progress_artifacts": True,
        "safe_overwrite_or_resume_plan_must_not_read_source_date_2025_11_01": True,
        "safe_overwrite_or_resume_plan_must_not_use_stdout_only_progress": True,
        "safe_overwrite_or_resume_plan_must_not_use_current_all_in_one_panel": True,
    }
    self_validator = {
        **plan,
        "artifact_count_expected": 7,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan.json",
            "repo_only_okx_88_symbol_1h_panel_revised_build_recovery_route_decision.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_policy.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_contract.json",
            "repo_only_okx_88_symbol_1h_panel_revised_build_safe_overwrite_or_resume_fallback_contract.json",
            "repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
    }
    return {
        "plan": plan,
        "route_decision": route_decision,
        "partial_output_policy": partial_policy,
        "forensic_contract": forensic_contract,
        "fallback_contract": fallback_contract,
        "approval": {**approval, "next_module": next_module},
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, dict[str, Any]]) -> None:
    files = {
        "repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan.json": outputs["plan"],
        "repo_only_okx_88_symbol_1h_panel_revised_build_recovery_route_decision.json": outputs["route_decision"],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_policy.json": outputs["partial_output_policy"],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_contract.json": outputs[
            "forensic_contract"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_build_safe_overwrite_or_resume_fallback_contract.json": outputs[
            "fallback_contract"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_approval_record.json": outputs[
            "approval"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_self_validator.json": outputs[
            "self_validator"
        ],
    }
    for filename, payload in files.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["plan"], indent=2, sort_keys=True))
    return 0 if outputs["plan"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
