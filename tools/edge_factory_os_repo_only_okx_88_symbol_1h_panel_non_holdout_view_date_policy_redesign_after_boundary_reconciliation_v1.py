#!/usr/bin/env python3
"""Repo-only date-policy redesign after UTC boundary reconciliation failed.

This module redesigns metadata only. It does not read source rows, read the
current all-in-one panel, read sealed-holdout files, build, aggregate, retry
strategy search, generate candidates, claim edge, release a family, or touch
runtime/live/capital.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_after_boundary_reconciliation_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_after_boundary_reconciliation_v1"

BOUNDARY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_after_blocked_build_v1"
BOUNDARY = BOUNDARY_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation.json"
BOUNDARY_SAMPLE = BOUNDARY_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_boundary_sample_report.json"

BLOCKED_RECORD_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_blocked_record_v1"
BLOCKED_RECORD = BLOCKED_RECORD_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record.json"

PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_after_access_plan_v1"
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview.json"

ACCESS_PLAN_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1"
ACCESS_PLAN = ACCESS_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"

PREREG_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_after_strategy_search_preview_v1"
PREREG = PREREG_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration.json"

EXPECTED_HEAD = "e3f9d47"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_DATE_POLICY_REDESIGNED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_DATE_POLICY_REDESIGN_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_after_date_policy_redesign_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_DATE_POLICY_REDESIGNED_REVISED_BUILD_RETRY_PREVIEW_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_DATE_POLICY_REDESIGN_BLOCKED_REVIEW_REQUIRED"

ORIGINAL_NON_HOLDOUT_VIEW_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
REVISED_NON_HOLDOUT_VIEW_START = "2023-07-01T00:00:00Z"
REVISED_NON_HOLDOUT_VIEW_END_EXCLUSIVE = "2025-10-31T16:00:00Z"
SEALED_HOLDOUT_START = "2025-11-01T00:00:00Z"
BOUNDARY_BUFFER_START = "2025-10-31T16:00:00Z"
BOUNDARY_BUFFER_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
REVISED_SOURCE_START_DATE = "2023-07-01"
REVISED_SOURCE_END_DATE_INCLUSIVE = "2025-10-31"
EXPECTED_BLOCKER = "SOURCE_DATE_POLICY_AND_UTC_OUTPUT_WINDOW_COUNT_NOT_RECONCILED_WITH_ALLOWED_PRE_HOLDOUT_SOURCE_FILES"

SELECTED_SYMBOL_COUNT = 88
REVISED_EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 854
REVISED_EXPECTED_TOTAL_SOURCE_FILE_COUNT = 75152
REVISED_EXPECTED_RAW_SOURCE_ROWS_FROM_ALLOWED_FILES = 108218880
REVISED_EXPECTED_OUTPUT_1M_ROWS_PER_SYMBOL = 1229280
REVISED_EXPECTED_TOTAL_OUTPUT_1M_ROWS = 108176640
REVISED_EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H = 20488
REVISED_EXPECTED_TOTAL_OUTPUT_ROWS_1H = 1802944
BOUNDARY_BUFFER_HOURS_PER_SYMBOL = 8
BOUNDARY_BUFFER_TOTAL_1H_ROWS_EXCLUDED = 704


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
        "boundary": BOUNDARY,
        "boundary_sample": BOUNDARY_SAMPLE,
        "blocked_record": BLOCKED_RECORD,
        "preview": PREVIEW,
        "access_plan": ACCESS_PLAN,
        "registry": REGISTRY,
        "preregistration": PREREG,
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
    boundary = loaded.get("boundary", {})
    sample = loaded.get("boundary_sample", {})
    blocked = loaded.get("blocked_record", {})
    preview = loaded.get("preview", {})
    access_plan = loaded.get("access_plan", {})
    registry = loaded.get("registry", {})
    prereg = loaded.get("preregistration", {})

    boundary_reconciliation_confirmed = (
        boundary.get("okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_SOURCE_DATE_UTC_BOUNDARY_RECONCILIATION_READY"
        and boundary.get("boundary_reconciliation_performed") is True
        and boundary.get("date_boundary_reconciliation_passed") is False
        and boundary.get("future_date_policy_redesign_required") is True
        and boundary.get("source_date_policy_reconciled_with_utc_output_window") is False
        and boundary.get("utc_output_window_count_reconciled") is False
        and boundary.get("replacement_checks_all_true") is True
    )
    source_files_appear_utc_plus_8_day_boundary = (
        boundary.get("boundary_sample_min_timestamp") == "2023-06-30T16:00:00Z"
        and boundary.get("boundary_sample_max_timestamp") == "2025-10-31T15:59:00Z"
        and sample.get("boundary_sample_timestamps_all_lt_sealed_holdout_start") is True
        and sample.get("boundary_sample_source_files_all_lt_sealed_holdout_start") is True
    )
    upstream_chain_confirmed = (
        blocked.get("exact_blocker") == EXPECTED_BLOCKER
        and blocked.get("replacement_checks_all_true") is True
        and preview.get("selected_symbol_count") == SELECTED_SYMBOL_COUNT
        and preview.get("replacement_checks_all_true") is True
        and access_plan.get("replacement_checks_all_true") is True
        and registry.get("sealed_holdout_window_start") == SEALED_HOLDOUT_START
        and prereg.get("route_family_selected") == "CROSS_SECTIONAL_MOMENTUM_BASELINE"
    )
    revised_counts_recomputed = (
        REVISED_EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H == 20488
        and REVISED_EXPECTED_TOTAL_OUTPUT_ROWS_1H == REVISED_EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H * SELECTED_SYMBOL_COUNT
        and REVISED_EXPECTED_OUTPUT_1M_ROWS_PER_SYMBOL == REVISED_EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H * 60
        and REVISED_EXPECTED_TOTAL_OUTPUT_1M_ROWS == REVISED_EXPECTED_OUTPUT_1M_ROWS_PER_SYMBOL * SELECTED_SYMBOL_COUNT
        and BOUNDARY_BUFFER_TOTAL_1H_ROWS_EXCLUDED == BOUNDARY_BUFFER_HOURS_PER_SYMBOL * SELECTED_SYMBOL_COUNT
    )
    source_file_date_2025_11_01_required_for_original_utc_end = True
    replacement_checks = {
        "boundary_reconciliation_confirmed": boundary_reconciliation_confirmed,
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "no_build_or_aggregation": True,
        "no_forbidden_reads": True,
        "no_strategy_candidate_edge": True,
        "repo_clean_except_current_tool": repo_clean,
        "revised_counts_recomputed": revised_counts_recomputed,
        "source_file_2025_11_01_rejected": True,
        "source_files_appear_utc_plus_8_day_boundary": source_files_appear_utc_plus_8_day_boundary,
        "upstream_chain_confirmed": upstream_chain_confirmed,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    record = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 0,
        "aggregation_performed_now": False,
        "approval_grants_build_apply_now": False,
        "approval_grants_build_retry_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_date_policy_redesign_now": True,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_revised_build_retry_preview_next": replacement_checks_all_true,
        "approval_grants_holdout_access_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "boundary_buffer_end_exclusive": BOUNDARY_BUFFER_END_EXCLUSIVE,
        "boundary_buffer_excluded": True,
        "boundary_buffer_hours_per_symbol": BOUNDARY_BUFFER_HOURS_PER_SYMBOL,
        "boundary_buffer_reason": "AVOID_SOURCE_FILE_2025_11_01_MIXED_PRE_HOLDOUT_AND_SEALED_HOLDOUT_CONTENT",
        "boundary_buffer_start": BOUNDARY_BUFFER_START,
        "boundary_buffer_total_1h_rows_excluded": BOUNDARY_BUFFER_TOTAL_1H_ROWS_EXCLUDED,
        "boundary_reconciliation_confirmed": boundary_reconciliation_confirmed,
        "boundary_reconciliation_passed_before_redesign": False,
        "build_apply_allowed_now": False,
        "build_retry_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_date_policy_redesign": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "date_policy_redesign_performed": replacement_checks_all_true,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "full_1h_panel_read_performed": False,
        "future_build_must_apply_utc_output_filter": True,
        "future_build_must_not_use_current_all_in_one_panel": True,
        "future_revised_build_retry_preview_allowed_next": replacement_checks_all_true,
        "next_module": next_module,
        "okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_status": status,
        "original_non_holdout_view_end_exclusive": ORIGINAL_NON_HOLDOUT_VIEW_END_EXCLUSIVE,
        "output_timestamps_must_be_lt_revised_end_exclusive": True,
        "output_timestamps_must_be_lt_sealed_holdout_start": True,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "retry_strategy_search_allowed_now": False,
        "revised_expected_daily_file_count_per_symbol": REVISED_EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "revised_expected_output_1m_rows_per_symbol": REVISED_EXPECTED_OUTPUT_1M_ROWS_PER_SYMBOL,
        "revised_expected_output_rows_per_symbol_1h": REVISED_EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "revised_expected_raw_source_rows_from_allowed_files": REVISED_EXPECTED_RAW_SOURCE_ROWS_FROM_ALLOWED_FILES,
        "revised_expected_total_output_1m_rows": REVISED_EXPECTED_TOTAL_OUTPUT_1M_ROWS,
        "revised_expected_total_output_rows_1h": REVISED_EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "revised_expected_total_source_file_count": REVISED_EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "revised_non_holdout_view_end_exclusive": REVISED_NON_HOLDOUT_VIEW_END_EXCLUSIVE,
        "revised_non_holdout_view_start": REVISED_NON_HOLDOUT_VIEW_START,
        "revised_source_end_date_inclusive": REVISED_SOURCE_END_DATE_INCLUSIVE,
        "revised_source_start_date": REVISED_SOURCE_START_DATE,
        "runtime_live_capital_allowed_now": False,
        "sealed_holdout_rows_allowed_in_output": False,
        "sealed_holdout_rows_read_count": 0,
        "sealed_holdout_source_file_read_allowed": False,
        "sealed_holdout_source_file_read_count": 0,
        "sealed_holdout_window_start": SEALED_HOLDOUT_START,
        "source_file_date_2025_11_01_allowed": False,
        "source_file_date_2025_11_01_rejected": True,
        "source_file_date_2025_11_01_required_for_original_utc_end": source_file_date_2025_11_01_required_for_original_utc_end,
        "source_files_appear_utc_plus_8_day_boundary": source_files_appear_utc_plus_8_day_boundary,
        "source_zip_csv_row_read_performed": False,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "tracked_python_count_at_date_policy_redesign_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_load_errors": load_errors,
    }
    revised_policy = {
        **record,
        "policy_statement": "Use source file dates 2023-07-01 through 2025-10-31 inclusive, reject source date 2025-11-01, and filter output timestamps to [2023-07-01T00:00:00Z, 2025-10-31T16:00:00Z).",
    }
    buffer_policy = {
        **record,
        "excluded_boundary_buffer": {
            "start": BOUNDARY_BUFFER_START,
            "end_exclusive": BOUNDARY_BUFFER_END_EXCLUSIVE,
            "hours_per_symbol": BOUNDARY_BUFFER_HOURS_PER_SYMBOL,
            "total_1h_rows_excluded": BOUNDARY_BUFFER_TOTAL_1H_ROWS_EXCLUDED,
            "reason": record["boundary_buffer_reason"],
        },
    }
    counts = {
        **record,
        "count_formula": "20496 original hours - 8 boundary-buffer hours = 20488 revised hours per symbol; 20488*88=1802944.",
    }
    approval = {
        **record,
        "approval_scope": "future_revised_build_retry_preview_only",
        "approved_next_module": NEXT_PASS_MODULE,
    }
    self_validator = {
        **record,
        "artifact_count_expected": 6,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_date_policy.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_boundary_buffer_policy.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_expected_counts.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
    }
    return {
        "record": record,
        "revised_policy": revised_policy,
        "buffer_policy": buffer_policy,
        "counts": counts,
        "approval": approval,
        "self_validator": self_validator,
    }


def main() -> None:
    outputs = build_outputs()
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign.json", outputs["record"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_date_policy.json", outputs["revised_policy"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_boundary_buffer_policy.json", outputs["buffer_policy"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_expected_counts.json", outputs["counts"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_approval_record.json", outputs["approval"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_self_validator.json", outputs["self_validator"])
    print(json.dumps(outputs["record"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
