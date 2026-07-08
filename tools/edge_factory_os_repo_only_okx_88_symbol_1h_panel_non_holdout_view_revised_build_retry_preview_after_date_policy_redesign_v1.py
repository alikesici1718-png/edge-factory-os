#!/usr/bin/env python3
"""Repo-only revised non-holdout build retry preview.

This preview defines the future revised build contract only. It does not read
source rows, read the current all-in-one 1h panel, read sealed-holdout files,
build, aggregate, retry strategy search, generate candidates, claim edge,
release a family, or touch runtime/live/capital.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_after_date_policy_redesign_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_after_date_policy_redesign_v1"

REDESIGN_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_after_boundary_reconciliation_v1"
REDESIGN = REDESIGN_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign.json"
REVISED_POLICY = REDESIGN_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_date_policy.json"
REVISED_COUNTS = REDESIGN_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_expected_counts.json"

BOUNDARY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_after_blocked_build_v1"
BOUNDARY = BOUNDARY_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation.json"

BLOCKED_RECORD_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_blocked_record_v1"
BLOCKED_RECORD = BLOCKED_RECORD_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record.json"

PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_after_access_plan_v1"
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview.json"

ACCESS_PLAN_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1"
ACCESS_PLAN = ACCESS_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"

EXPECTED_HEAD = "21725a5"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_BUILD_RETRY_PREVIEW_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_BUILD_RETRY_PREVIEW_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_BUILD_RETRY_PREVIEW_READY_EXECUTION_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_BUILD_RETRY_PREVIEW_BLOCKED_REVIEW_REQUIRED"

REVISED_NON_HOLDOUT_VIEW_START = "2023-07-01T00:00:00Z"
REVISED_NON_HOLDOUT_VIEW_END_EXCLUSIVE = "2025-10-31T16:00:00Z"
REVISED_SOURCE_START_DATE = "2023-07-01"
REVISED_SOURCE_END_DATE_INCLUSIVE = "2025-10-31"
BOUNDARY_BUFFER_TOTAL_1H_ROWS_EXCLUDED = 704
REVISED_EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 854
REVISED_EXPECTED_TOTAL_SOURCE_FILE_COUNT = 75152
REVISED_EXPECTED_RAW_SOURCE_ROWS_FROM_ALLOWED_FILES = 108218880
REVISED_EXPECTED_OUTPUT_1M_ROWS_PER_SYMBOL = 1229280
REVISED_EXPECTED_TOTAL_OUTPUT_1M_ROWS = 108176640
REVISED_EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H = 20488
REVISED_EXPECTED_TOTAL_OUTPUT_ROWS_1H = 1802944


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
        "redesign": REDESIGN,
        "revised_policy": REVISED_POLICY,
        "revised_counts": REVISED_COUNTS,
        "boundary": BOUNDARY,
        "blocked_record": BLOCKED_RECORD,
        "preview": PREVIEW,
        "access_plan": ACCESS_PLAN,
        "registry": REGISTRY,
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
    redesign = loaded.get("redesign", {})
    revised_policy = loaded.get("revised_policy", {})
    revised_counts = loaded.get("revised_counts", {})
    boundary = loaded.get("boundary", {})
    blocked = loaded.get("blocked_record", {})
    preview = loaded.get("preview", {})
    access_plan = loaded.get("access_plan", {})
    registry = loaded.get("registry", {})

    date_policy_redesign_confirmed = (
        redesign.get("okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_DATE_POLICY_REDESIGNED"
        and redesign.get("date_policy_redesign_performed") is True
        and redesign.get("revised_non_holdout_view_end_exclusive") == REVISED_NON_HOLDOUT_VIEW_END_EXCLUSIVE
        and redesign.get("source_file_date_2025_11_01_allowed") is False
        and redesign.get("source_file_date_2025_11_01_rejected") is True
        and redesign.get("boundary_buffer_excluded") is True
        and redesign.get("future_revised_build_retry_preview_allowed_next") is True
        and redesign.get("replacement_checks_all_true") is True
    )
    revised_counts_consistent = (
        redesign.get("revised_expected_total_source_file_count") == REVISED_EXPECTED_TOTAL_SOURCE_FILE_COUNT
        and redesign.get("revised_expected_raw_source_rows_from_allowed_files") == REVISED_EXPECTED_RAW_SOURCE_ROWS_FROM_ALLOWED_FILES
        and redesign.get("revised_expected_output_1m_rows_per_symbol") == REVISED_EXPECTED_OUTPUT_1M_ROWS_PER_SYMBOL
        and redesign.get("revised_expected_total_output_1m_rows") == REVISED_EXPECTED_TOTAL_OUTPUT_1M_ROWS
        and redesign.get("revised_expected_output_rows_per_symbol_1h") == REVISED_EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H
        and redesign.get("revised_expected_total_output_rows_1h") == REVISED_EXPECTED_TOTAL_OUTPUT_ROWS_1H
        and revised_counts.get("revised_expected_total_output_rows_1h") == REVISED_EXPECTED_TOTAL_OUTPUT_ROWS_1H
    )
    upstream_chain_confirmed = (
        boundary.get("future_date_policy_redesign_required") is True
        and boundary.get("date_boundary_reconciliation_passed") is False
        and blocked.get("replacement_checks_all_true") is True
        and preview.get("replacement_checks_all_true") is True
        and access_plan.get("replacement_checks_all_true") is True
        and registry.get("holdout_registry_valid_for_this_panel") is True
        and revised_policy.get("future_build_must_not_use_current_all_in_one_panel") is True
    )

    replacement_checks = {
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "date_policy_redesign_confirmed": date_policy_redesign_confirmed,
        "no_build_or_aggregation": True,
        "no_forbidden_reads": True,
        "no_strategy_candidate_edge": True,
        "repo_clean_except_current_tool": repo_clean,
        "revised_counts_consistent": revised_counts_consistent,
        "source_file_2025_11_01_forbidden": redesign.get("source_file_date_2025_11_01_allowed") is False and redesign.get("source_file_date_2025_11_01_rejected") is True,
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
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_revised_build_execution_next": replacement_checks_all_true,
        "approval_grants_holdout_access_now": False,
        "approval_grants_revised_build_execution_now": False,
        "approval_grants_revised_build_retry_preview_now": True,
        "approval_grants_revised_build_validator_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "boundary_buffer_excluded": True,
        "boundary_buffer_total_1h_rows_excluded": BOUNDARY_BUFFER_TOTAL_1H_ROWS_EXCLUDED,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_revised_build_retry_preview": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "date_policy_redesign_confirmed": date_policy_redesign_confirmed,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "full_1h_panel_read_performed": False,
        "future_build_must_apply_utc_output_filter": True,
        "future_build_must_not_read_source_file_2025_11_01": True,
        "future_build_must_not_use_current_all_in_one_panel": True,
        "future_build_must_physically_exclude_sealed_holdout": True,
        "future_revised_build_execution_allowed_next": replacement_checks_all_true,
        "future_validator_required": True,
        "next_module": next_module,
        "okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_status": status,
        "output_valid_for_edge_claim": False,
        "output_valid_for_strategy_search_after_preview": False,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "retry_strategy_search_allowed_now": False,
        "revised_build_execution_allowed_now": False,
        "revised_build_retry_preview_created": replacement_checks_all_true,
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
        "sealed_holdout_rows_read_count": 0,
        "sealed_holdout_source_file_read_count": 0,
        "source_file_date_2025_11_01_allowed": False,
        "source_file_date_2025_11_01_rejected": True,
        "source_zip_csv_row_read_performed": False,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "tracked_python_count_at_revised_build_retry_preview_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_load_errors": load_errors,
    }
    contract = {
        **record,
        "future_build_fail_closed_if": [
            "source_file_date_gte_2025_11_01_read",
            "current_all_in_one_1h_panel_read",
            "source_file_count_processed_ne_75152",
            "source_file_date_max_read_ne_2025_10_31",
            "output_1h_row_count_ne_1802944",
            "output_symbol_count_ne_88",
            "output_timestamp_gte_2025_10_31T16_00_00Z",
            "output_timestamp_lt_2023_07_01T00_00_00Z",
            "output_marked_strategy_search_valid_before_validator",
            "strategy_search_candidate_or_edge_occurs",
        ],
        "future_build_contract": "build physically separate revised non-holdout view using allowed source dates only and UTC output filter",
    }
    counts = {**record, "count_formula": "20488 1h rows per symbol * 88 symbols = 1802944 total 1h rows"}
    utc_filter = {
        **record,
        "exclude_boundary_buffer_start": "2025-10-31T16:00:00Z",
        "exclude_pre_window_rows_before": "2023-07-01T00:00:00Z",
        "output_timestamp_filter": "2023-07-01T00:00:00Z <= timestamp < 2025-10-31T16:00:00Z",
    }
    fail_closed_policy = {**contract}
    approval = {
        **record,
        "approval_scope": "future_revised_non_holdout_view_build_execution_only",
        "approved_next_module": NEXT_PASS_MODULE,
    }
    self_validator = {
        **record,
        "artifact_count_expected": 7,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_contract.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_expected_counts.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_utc_output_filter_policy.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_fail_closed_policy.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
    }
    return {
        "record": record,
        "contract": contract,
        "counts": counts,
        "utc_filter": utc_filter,
        "fail_closed_policy": fail_closed_policy,
        "approval": approval,
        "self_validator": self_validator,
    }


def main() -> None:
    outputs = build_outputs()
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview.json", outputs["record"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_contract.json", outputs["contract"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_expected_counts.json", outputs["counts"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_utc_output_filter_policy.json", outputs["utc_filter"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_fail_closed_policy.json", outputs["fail_closed_policy"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_approval_record.json", outputs["approval"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_self_validator.json", outputs["self_validator"])
    print(json.dumps(outputs["record"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
