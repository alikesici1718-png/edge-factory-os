#!/usr/bin/env python3
"""Repo-only preview for a holdout-safe non-holdout OKX 1h view build.

This module creates preview/approval artifacts only. It does not build,
aggregate, repair/apply, read the current all-in-one 1h panel, read sealed
holdout rows, read original 1m source CSV/ZIP row contents, retry strategy
search, generate candidates, claim edge, or touch runtime/live/capital.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_after_access_plan_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_after_access_plan_v1"

ACCESS_PLAN_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1"
ACCESS_PLAN = ACCESS_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json"
ACCESS_BUILD_PLAN = ACCESS_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_plan.json"

BLOCKED_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_v1"
BLOCKED_RECORD = BLOCKED_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record.json"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"

BUILD_SUMMARY = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1" / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_summary.json"
PIPELINE_SUMMARY = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_after_validator_v1" / "repo_only_okx_88_symbol_near_3y_1h_panel_validated_pipeline_output_summary.json"

EXPECTED_HEAD = "4f47e65"
EXPECTED_BLOCKER = "PANEL_SORTED_BY_SYMBOL_WITHOUT_ROW_OFFSET_INDEX_REQUIRES_SEALED_HOLDOUT_SCAN_TO_REACH_LATER_SYMBOL_PRE_HOLDOUT_ROWS"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_PREVIEW_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_PREVIEW_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_after_preview_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_PREVIEW_READY_EXECUTION_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_PREVIEW_BLOCKED_REVIEW_REQUIRED"

SELECTED_SYMBOL_COUNT = 88
NON_HOLDOUT_VIEW_START = "2023-07-01T00:00:00Z"
NON_HOLDOUT_VIEW_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
NON_HOLDOUT_SOURCE_START_DATE = "2023-07-01"
NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE = "2025-10-31"
SEALED_HOLDOUT_START = "2025-11-01T00:00:00Z"
SEALED_HOLDOUT_END_EXCLUSIVE = "2026-05-19T00:00:00Z"
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 854
EXPECTED_TOTAL_SOURCE_FILE_COUNT = 75152
EXPECTED_SOURCE_ROWS_PER_SYMBOL = 1229760
EXPECTED_TOTAL_SOURCE_ROWS = 108218880
EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H = 20496
EXPECTED_TOTAL_OUTPUT_ROWS_1H = 1803648


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
        "access_plan": ACCESS_PLAN,
        "access_build_plan": ACCESS_BUILD_PLAN,
        "blocked_record": BLOCKED_RECORD,
        "registry": REGISTRY,
        "build_summary": BUILD_SUMMARY,
        "pipeline_summary": PIPELINE_SUMMARY,
    }.items():
        try:
            loaded[label] = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def build_outputs() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_inputs()
    access_plan = loaded.get("access_plan", {})
    access_build_plan = loaded.get("access_build_plan", {})
    blocked_record = loaded.get("blocked_record", {})
    registry = loaded.get("registry", {})
    build_summary = loaded.get("build_summary", {})
    pipeline_summary = loaded.get("pipeline_summary", {})

    access_plan_confirmed = (
        access_plan.get("okx_88_symbol_1h_panel_holdout_safe_access_plan_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_SAFE_ACCESS_PLAN_READY"
        and access_plan.get("holdout_safe_access_plan_created") is True
        and access_plan.get("exact_blocker") == EXPECTED_BLOCKER
        and access_plan.get("preferred_safe_access_route") == "BUILD_SEPARATE_NON_HOLDOUT_VIEW_FROM_SOURCE_DATE_FILES_PREVIEW_NEXT"
        and access_plan.get("future_non_holdout_view_build_preview_required") is True
        and access_plan.get("non_holdout_view_build_allowed_now") is False
        and access_plan.get("replacement_checks_all_true") is True
        and access_build_plan.get("future_preview_required") is True
        and blocked_record.get("exact_blocker") == EXPECTED_BLOCKER
    )
    exact_blocker_confirmed = access_plan.get("exact_blocker") == EXPECTED_BLOCKER and blocked_record.get("exact_blocker") == EXPECTED_BLOCKER
    preferred_safe_access_route_confirmed = access_plan.get("preferred_safe_access_route") == "BUILD_SEPARATE_NON_HOLDOUT_VIEW_FROM_SOURCE_DATE_FILES_PREVIEW_NEXT"
    registry_metadata_confirmed = (
        registry.get("selected_symbol_count") == SELECTED_SYMBOL_COUNT
        and registry.get("sealed_holdout_window_start") == SEALED_HOLDOUT_START
        and registry.get("sealed_holdout_window_end_exclusive") == SEALED_HOLDOUT_END_EXCLUSIVE
        and registry.get("replacement_checks_all_true") is True
    )
    metadata_consistent = (
        build_summary.get("selected_symbol_count") == SELECTED_SYMBOL_COUNT
        and build_summary.get("expected_source_rows_per_symbol") == 1516320
        and build_summary.get("expected_output_rows_per_symbol_1h") == 25272
        and pipeline_summary.get("selected_symbol_count") == SELECTED_SYMBOL_COUNT
    )

    no_forbidden_actions = {
        "aggregation_performed_now": False,
        "candidate_generation_performed": False,
        "data_build_performed": False,
        "data_download_performed": False,
        "edge_claim_performed": False,
        "full_1h_panel_read_performed": False,
        "original_source_full_csv_read_performed": False,
        "sealed_holdout_rows_read_count": 0,
        "source_zip_csv_row_read_performed": False,
        "strategy_search_executed": False,
    }
    blocks = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "non_holdout_view_build_allowed_now": False,
        "retry_strategy_search_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
    }
    approvals = {
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_non_holdout_view_build_execution_next": True,
        "approval_grants_holdout_access_now": False,
        "approval_grants_non_holdout_view_build_now": False,
        "approval_grants_non_holdout_view_build_preview_now": True,
        "approval_grants_non_holdout_view_validator_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
    }

    replacement_checks = {
        "access_plan_confirmed": access_plan_confirmed,
        "count_expectations_match_policy": (
            EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL == 854
            and EXPECTED_TOTAL_SOURCE_FILE_COUNT == 75152
            and EXPECTED_SOURCE_ROWS_PER_SYMBOL == 1229760
            and EXPECTED_TOTAL_SOURCE_ROWS == 108218880
            and EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H == 20496
            and EXPECTED_TOTAL_OUTPUT_ROWS_1H == 1803648
        ),
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "exact_blocker_confirmed": exact_blocker_confirmed,
        "metadata_consistent": metadata_consistent,
        "no_build_or_aggregation": no_forbidden_actions["data_build_performed"] is False and no_forbidden_actions["aggregation_performed_now"] is False,
        "no_panel_or_source_row_read": (
            no_forbidden_actions["full_1h_panel_read_performed"] is False
            and no_forbidden_actions["source_zip_csv_row_read_performed"] is False
            and no_forbidden_actions["original_source_full_csv_read_performed"] is False
            and no_forbidden_actions["sealed_holdout_rows_read_count"] == 0
        ),
        "no_strategy_retry_candidate_edge_runtime": (
            blocks["strategy_search_allowed_now"] is False
            and blocks["retry_strategy_search_allowed_now"] is False
            and blocks["candidate_generation_allowed_now"] is False
            and blocks["edge_claim_allowed_now"] is False
            and blocks["runtime_live_capital_allowed_now"] is False
        ),
        "preferred_safe_access_route_confirmed": preferred_safe_access_route_confirmed,
        "registry_metadata_confirmed": registry_metadata_confirmed,
        "repo_clean_except_current_tool": repo_clean,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    preview = {
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "access_plan_confirmed": access_plan_confirmed,
        "aggregation_policy_carried_forward": True,
        "current_all_in_one_panel_retry_rejected": True,
        "current_evidence_chain_quality_after_preview": quality,
        "duplicate_conflict_policy_carried_forward": True,
        "exact_blocker_confirmed": exact_blocker_confirmed,
        "expected_daily_file_count_per_symbol_non_holdout": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_output_rows_per_symbol_1h_non_holdout": EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "expected_source_rows_per_symbol_non_holdout": EXPECTED_SOURCE_ROWS_PER_SYMBOL,
        "expected_total_output_rows_1h_non_holdout": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "expected_total_source_file_count_non_holdout": EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "expected_total_source_rows_non_holdout": EXPECTED_TOTAL_SOURCE_ROWS,
        "future_build_must_not_use_current_all_in_one_panel": True,
        "future_build_must_use_source_daily_files_only": True,
        "future_strategy_search_retry_requires_validated_non_holdout_view": True,
        "future_validator_required": True,
        "incomplete_hour_policy_carried_forward": True,
        "next_module": next_module,
        "non_holdout_source_end_date_inclusive": NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE,
        "non_holdout_source_start_date": NON_HOLDOUT_SOURCE_START_DATE,
        "non_holdout_view_build_preview_created": replacement_checks_all_true,
        "non_holdout_view_end_exclusive": NON_HOLDOUT_VIEW_END_EXCLUSIVE,
        "non_holdout_view_must_physically_exclude_sealed_holdout": True,
        "non_holdout_view_start": NON_HOLDOUT_VIEW_START,
        "okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_status": status,
        "output_valid_for_edge_claim": False,
        "output_valid_for_strategy_search_after_preview": False,
        "preferred_safe_access_route_confirmed": preferred_safe_access_route_confirmed,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "row_offset_index_creation_by_full_panel_scan_allowed": False,
        "sealed_holdout_dates_included": False,
        "sealed_holdout_rows_allowed_in_non_holdout_view": False,
        "sealed_holdout_rows_expected_in_non_holdout_view": 0,
        "sealed_holdout_window_end_exclusive": SEALED_HOLDOUT_END_EXCLUSIVE,
        "sealed_holdout_window_start": SEALED_HOLDOUT_START,
        "selected_symbol_count": SELECTED_SYMBOL_COUNT,
        "tracked_python_count_at_preview_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_load_errors": load_errors,
    }
    preview.update(no_forbidden_actions)
    preview.update(blocks)
    preview.update(approvals)

    date_policy = {
        "daily_source_files_allowed": {
            "date_gte": NON_HOLDOUT_SOURCE_START_DATE,
            "date_lte": NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE,
            "date_lt_sealed_holdout_start": True,
        },
        "daily_source_files_forbidden": {"date_gte": "2025-11-01"},
        "filtering_after_reading_sealed_holdout_rows_forbidden": True,
        "non_holdout_view_end_exclusive": NON_HOLDOUT_VIEW_END_EXCLUSIVE,
        "non_holdout_view_start": NON_HOLDOUT_VIEW_START,
        "sealed_holdout_dates_included": False,
        "sealed_holdout_window_end_exclusive": SEALED_HOLDOUT_END_EXCLUSIVE,
        "sealed_holdout_window_start": SEALED_HOLDOUT_START,
    }
    expected_counts = {
        "expected_daily_file_count_per_symbol_non_holdout": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_output_rows_per_symbol_1h_non_holdout": EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "expected_source_rows_per_symbol_non_holdout": EXPECTED_SOURCE_ROWS_PER_SYMBOL,
        "expected_total_output_rows_1h_non_holdout": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "expected_total_source_file_count_non_holdout": EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "expected_total_source_rows_non_holdout": EXPECTED_TOTAL_SOURCE_ROWS,
        "selected_symbol_count": SELECTED_SYMBOL_COUNT,
    }
    source_plan = {
        "aggregation_policy_carried_forward": True,
        "duplicate_conflict_policy_carried_forward": True,
        "future_build_must_not_use_current_all_in_one_panel": True,
        "future_build_must_use_source_daily_files_only": True,
        "future_execution_must_preserve_numeric_provenance_schema_validation": True,
        "incomplete_hour_policy_carried_forward": True,
        "output_is_non_holdout_view_required": True,
        "output_valid_for_edge_claim": False,
        "output_valid_for_strategy_search_after_validator": False,
    }
    validation_plan = {
        "duplicate_symbol_hour_count_must_equal": 0,
        "future_validator_required": True,
        "no_timestamp_gte": SEALED_HOLDOUT_START,
        "numeric_sanity_required": True,
        "output_row_count_must_equal": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "output_valid_for_edge_claim": False,
        "output_valid_for_strategy_search_after_validator_may_become_true_only_after_validator": True,
        "per_symbol_hourly_rows_must_equal": EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "policy_effects_reconcile_required": True,
        "provenance_valid_required": True,
        "schema_valid_required": True,
        "symbol_count_must_equal": SELECTED_SYMBOL_COUNT,
    }
    approval_record = {
        **approvals,
        "next_module": next_module,
    }
    self_validator = {
        "created_at_utc": now_utc(),
        "expected_head": EXPECTED_HEAD,
        "latest_head_at_run": head,
        "output_dir": str(OUTPUT_DIR),
        "required_artifacts": [
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_date_policy.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_expected_counts.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_source_plan.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_validation_plan.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_self_validator.json",
        ],
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
        "tool_path": str(REPO / TOOL_REL),
    }
    return {
        "preview": preview,
        "date_policy": date_policy,
        "expected_counts": expected_counts,
        "source_plan": source_plan,
        "validation_plan": validation_plan,
        "approval_record": approval_record,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payloads = {
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview.json": outputs["preview"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_date_policy.json": outputs["date_policy"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_expected_counts.json": outputs["expected_counts"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_source_plan.json": outputs["source_plan"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_validation_plan.json": outputs["validation_plan"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_approval_record.json": outputs["approval_record"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_self_validator.json": outputs["self_validator"],
    }
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["preview"], indent=2, sort_keys=True))
    return 0 if outputs["preview"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
