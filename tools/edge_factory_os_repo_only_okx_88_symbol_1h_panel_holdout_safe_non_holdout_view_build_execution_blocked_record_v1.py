#!/usr/bin/env python3
"""Repo-only blocked record after non-holdout view build fail-closed.

This module records the source-date/UTC output-window reconciliation blocker.
It does not repair, build, aggregate, read panel rows, read source rows, access
sealed holdout, retry strategy search, generate candidates, claim edge, release
a family, or touch runtime/live/capital.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_blocked_record_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_blocked_record_v1"

BUILD_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_after_preview_v1"
BUILD_REPORT = BUILD_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_report.json"
BUILD_SUMMARY = BUILD_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_summary.json"

PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_after_access_plan_v1"
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview.json"

ACCESS_PLAN_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1"
ACCESS_PLAN = ACCESS_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"

EXPECTED_HEAD = "0fe72ce"
EXPECTED_BLOCKER = "SOURCE_DATE_POLICY_AND_UTC_OUTPUT_WINDOW_COUNT_NOT_RECONCILED_WITH_ALLOWED_PRE_HOLDOUT_SOURCE_FILES"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_EXECUTION_BLOCKED_RECORD_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_EXECUTION_BLOCKED_RECORD_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_after_blocked_build_v1.py"
NEXT_FAIL_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record_failed_review_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_BLOCKED_RECORD_READY_DATE_BOUNDARY_RECONCILIATION_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_BLOCKED_RECORD_FAILED_REVIEW_REQUIRED"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO.as_posix()}", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(TOOL_REL.as_posix())]
    return not unexpected, unexpected


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for label, path in {
        "build_report": BUILD_REPORT,
        "build_summary": BUILD_SUMMARY,
        "preview": PREVIEW,
        "access_plan": ACCESS_PLAN,
        "registry": REGISTRY,
    }.items():
        try:
            loaded[label] = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def build_record() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_inputs()
    build = loaded.get("build_report", {})
    summary = loaded.get("build_summary", {})
    preview = loaded.get("preview", {})
    access_plan = loaded.get("access_plan", {})
    registry = loaded.get("registry", {})

    exact_blocker_recorded = build.get("exact_blocker") == EXPECTED_BLOCKER
    blocked_build_execution_confirmed = (
        build.get("okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_status")
        == "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_EXECUTION_DATE_BOUNDARY_RECONCILIATION_REQUIRED"
        and build.get("non_holdout_view_build_execution_performed") is False
        and build.get("output_file_created") is False
        and build.get("output_1h_row_count") == 0
        and build.get("sealed_holdout_source_file_read_count") == 0
        and build.get("sealed_holdout_rows_read_count") == 0
        and build.get("sealed_holdout_rows_written_count") == 0
        and build.get("current_all_in_one_panel_read_performed") is False
        and build.get("full_1h_panel_read_performed") is False
        and build.get("strategy_search_executed") is False
        and build.get("candidate_generation_performed") is False
        and build.get("edge_claim_performed") is False
        and build.get("data_build_performed") is False
        and build.get("aggregation_performed_now") is False
        and build.get("replacement_checks_all_true") is False
        and exact_blocker_recorded
    )
    build_preview_still_valid_pending_boundary_reconciliation = (
        preview.get("okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_PREVIEW_READY"
        and preview.get("non_holdout_view_build_preview_created") is True
        and preview.get("future_build_must_use_source_daily_files_only") is True
        and preview.get("future_build_must_not_use_current_all_in_one_panel") is True
        and preview.get("replacement_checks_all_true") is True
    )
    access_plan_still_valid = (
        access_plan.get("okx_88_symbol_1h_panel_holdout_safe_access_plan_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_SAFE_ACCESS_PLAN_READY"
        and access_plan.get("current_all_in_one_panel_retry_rejected") is True
        and access_plan.get("future_non_holdout_view_build_preview_required") is True
        and access_plan.get("replacement_checks_all_true") is True
    )
    registry_still_valid = (
        registry.get("okx_88_symbol_1h_panel_holdout_registry_builder_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_CREATED"
        and registry.get("holdout_registry_valid_for_this_panel") is True
        and registry.get("sealed_holdout_window_start") == "2025-11-01T00:00:00Z"
        and registry.get("replacement_checks_all_true") is True
    )

    replacement_checks = {
        "access_plan_still_valid": access_plan_still_valid,
        "blocked_build_execution_confirmed": blocked_build_execution_confirmed,
        "build_preview_still_valid_pending_boundary_reconciliation": build_preview_still_valid_pending_boundary_reconciliation,
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "exact_blocker_recorded": exact_blocker_recorded,
        "no_build_retry_or_repair": True,
        "no_forbidden_reads": (
            build.get("current_all_in_one_panel_read_performed") is False
            and build.get("full_1h_panel_read_performed") is False
            and build.get("sealed_holdout_source_file_read_count") == 0
            and build.get("sealed_holdout_rows_read_count") == 0
        ),
        "no_strategy_candidate_edge": (
            build.get("strategy_search_executed") is False
            and build.get("candidate_generation_performed") is False
            and build.get("edge_claim_performed") is False
        ),
        "registry_still_valid": registry_still_valid,
        "repo_clean_except_current_tool": repo_clean,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_FAIL_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    record = {
        "access_plan_still_valid": access_plan_still_valid,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "aggregation_performed_now": False,
        "approval_grants_blocked_record_now": True,
        "approval_grants_build_repair_apply_now": False,
        "approval_grants_build_retry_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_date_boundary_reconciliation_next": True,
        "approval_grants_holdout_access_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "blocked_build_execution_confirmed": blocked_build_execution_confirmed,
        "blocked_record_created": replacement_checks_all_true,
        "blocker_class": "NON_HOLDOUT_VIEW_SOURCE_DATE_UTC_BOUNDARY_RECONCILIATION_BLOCKER",
        "blocker_interpretation_created": True,
        "build_preview_still_valid_pending_boundary_reconciliation": build_preview_still_valid_pending_boundary_reconciliation,
        "candidate_generation_performed": False,
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_blocked_record": quality,
        "data_build_performed": False,
        "date_boundary_reconciliation_required": True,
        "edge_claim_performed": False,
        "exact_blocker": EXPECTED_BLOCKER,
        "exact_blocker_recorded": exact_blocker_recorded,
        "full_1h_panel_read_performed": False,
        "next_module": next_module,
        "non_holdout_view_build_execution_performed": False,
        "okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record_status": status,
        "output_1h_row_count": 0,
        "output_file_created": False,
        "raw_source_rows_read_before_block": build.get("raw_source_rows_read", 0),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "retry_build_allowed_now": False,
        "sealed_holdout_rows_read_count": 0,
        "sealed_holdout_rows_written_count": 0,
        "sealed_holdout_source_file_read_count": build.get("sealed_holdout_source_file_read_count", 0),
        "source_file_count_matches_expected": build.get("source_file_count_matches_expected", False),
        "source_file_count_processed": build.get("source_file_count_processed", 0),
        "source_file_date_max_read": build.get("source_file_date_max_read"),
        "source_file_dates_all_lt_sealed_holdout_start": build.get("source_file_dates_all_lt_sealed_holdout_start", False),
        "strategy_search_executed": False,
        "tracked_python_count_at_blocked_record_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_load_errors": load_errors,
    }

    analysis = {
        **record,
        "boundary_evidence_from_prior_blocked_execution": {
            "earliest_allowed_source_file_first_row_utc": build.get("earliest_allowed_source_file_first_row_utc"),
            "latest_allowed_source_file_last_row_utc": build.get("latest_allowed_source_file_last_row_utc"),
            "raw_source_rows_read_before_block": build.get("raw_source_rows_read", 0),
        },
        "blocker_interpretation": (
            "The source file date list is pre-holdout-safe by filename/date metadata, "
            "but the build must prove that daily source file timestamps reconcile exactly "
            "with the UTC output window and expected 1h row counts before producing a "
            "non-holdout panel."
        ),
        "prior_execution_summary_status": summary.get("okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_status"),
    }
    retry_policy = {
        **record,
        "build_retry_route": "blocked_until_date_boundary_reconciliation_diagnostic_passes",
        "date_boundary_reconciliation_required_before_build_retry": True,
        "direct_build_retry_allowed_now": False,
        "repair_apply_allowed_now": False,
        "strategy_retry_allowed_now": False,
    }
    approval = {
        **record,
        "approval_scope": "future_date_boundary_reconciliation_diagnostic_only",
        "approved_next_module": NEXT_PASS_MODULE,
    }
    self_validator = {
        **record,
        "artifact_count_expected": 5,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_boundary_blocker_analysis.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_retry_block_policy.json",
            "repo_only_okx_88_symbol_1h_panel_date_boundary_reconciliation_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
    }
    return {
        "record": record,
        "analysis": analysis,
        "retry_policy": retry_policy,
        "approval": approval,
        "self_validator": self_validator,
    }


def main() -> None:
    outputs = build_record()
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record.json", outputs["record"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_boundary_blocker_analysis.json", outputs["analysis"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_retry_block_policy.json", outputs["retry_policy"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_date_boundary_reconciliation_approval_record.json", outputs["approval"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record_self_validator.json", outputs["self_validator"])
    print(json.dumps(outputs["record"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
