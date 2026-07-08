#!/usr/bin/env python3
"""Repo-only holdout-safe access plan after blocked strategy execution.

This module records a plan only. It does not repair/apply, read panel rows, read
sealed holdout, read original 1m source rows, build/aggregate data, retry
strategy search, generate candidates, claim edge, or touch runtime/live/capital.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1"

BLOCKED_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_v1"
BLOCKED_RECORD = BLOCKED_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record.json"
BLOCKER_ANALYSIS = BLOCKED_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_access_blocker_analysis.json"

EXECUTION_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_after_route_preregistration_v1"
EXECUTION_REPORT = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_report.json"

PREREG_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_after_strategy_search_preview_v1"
PREREG = PREREG_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration.json"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"
SPLIT_POLICY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_split_policy.json"

EXPECTED_HEAD = "c5e4fb1"
EXPECTED_BLOCKER = "PANEL_SORTED_BY_SYMBOL_WITHOUT_ROW_OFFSET_INDEX_REQUIRES_SEALED_HOLDOUT_SCAN_TO_REACH_LATER_SYMBOL_PRE_HOLDOUT_ROWS"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_SAFE_ACCESS_PLAN_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_SAFE_ACCESS_PLAN_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_after_access_plan_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_HOLDOUT_SAFE_ACCESS_PLAN_READY_NON_HOLDOUT_VIEW_BUILD_PREVIEW_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_HOLDOUT_SAFE_ACCESS_PLAN_BLOCKED_REVIEW_REQUIRED"


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
        "blocked_record": BLOCKED_RECORD,
        "blocker_analysis": BLOCKER_ANALYSIS,
        "execution_report": EXECUTION_REPORT,
        "preregistration": PREREG,
        "registry": REGISTRY,
        "split_policy": SPLIT_POLICY,
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
    blocked = loaded.get("blocked_record", {})
    blocker_analysis = loaded.get("blocker_analysis", {})
    execution = loaded.get("execution_report", {})
    prereg = loaded.get("preregistration", {})
    registry = loaded.get("registry", {})
    split = loaded.get("split_policy", {})

    blocked_record_confirmed = (
        blocked.get("okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_EXECUTION_BLOCKED_RECORD_READY"
        and blocked.get("blocked_record_created") is True
        and blocked.get("blocked_execution_confirmed") is True
        and blocked.get("exact_blocker") == EXPECTED_BLOCKER
        and blocked.get("exact_blocker_recorded") is True
        and blocked.get("future_holdout_safe_access_plan_required") is True
        and blocked.get("replacement_checks_all_true") is True
        and blocker_analysis.get("exact_blocker") == EXPECTED_BLOCKER
        and execution.get("blocked_reason") == EXPECTED_BLOCKER
        and execution.get("sealed_holdout_accessed") is False
        and execution.get("sealed_holdout_rows_read_count") == 0
    )
    route_preregistration_still_valid = (
        prereg.get("okx_88_symbol_1h_panel_route_family_preregistration_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_ROUTE_FAMILY_PREREGISTERED"
        and prereg.get("route_family_selected") == "CROSS_SECTIONAL_MOMENTUM_BASELINE"
        and prereg.get("replacement_checks_all_true") is True
    )
    holdout_registry_still_valid = (
        registry.get("okx_88_symbol_1h_panel_holdout_registry_builder_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_CREATED"
        and registry.get("holdout_registry_valid_for_this_panel") is True
        and registry.get("sealed_holdout_window_start") == "2025-11-01T00:00:00Z"
        and registry.get("replacement_checks_all_true") is True
    )
    split_confirmed = (
        split.get("train_development_window_start") == "2023-07-01T00:00:00Z"
        and split.get("train_development_window_end_exclusive") == "2025-01-01T00:00:00Z"
        and split.get("validation_window_start") == "2025-01-01T00:00:00Z"
        and split.get("validation_window_end_exclusive") == "2025-11-01T00:00:00Z"
        and split.get("sealed_holdout_window_start") == "2025-11-01T00:00:00Z"
        and split.get("sealed_holdout_window_end_exclusive") == "2026-05-19T00:00:00Z"
    )

    no_forbidden_actions = {
        "aggregation_performed_now": False,
        "candidate_generation_performed": False,
        "data_build_performed": False,
        "data_download_performed": False,
        "edge_claim_performed": False,
        "full_1h_panel_read_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "original_source_full_csv_read_performed": False,
        "sealed_holdout_rows_read_count": 0,
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
        "approval_grants_access_repair_apply_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_non_holdout_view_build_preview_next": True,
        "approval_grants_holdout_access_now": False,
        "approval_grants_holdout_safe_access_plan_now": True,
        "approval_grants_non_holdout_view_build_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
    }

    replacement_checks = {
        "blocked_record_confirmed": blocked_record_confirmed,
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "exact_blocker_confirmed": blocked.get("exact_blocker") == EXPECTED_BLOCKER,
        "holdout_registry_still_valid": holdout_registry_still_valid,
        "no_build_aggregation_or_repair": (
            no_forbidden_actions["data_build_performed"] is False
            and no_forbidden_actions["aggregation_performed_now"] is False
            and blocks["non_holdout_view_build_allowed_now"] is False
        ),
        "no_panel_or_source_row_read": (
            no_forbidden_actions["full_1h_panel_read_performed"] is False
            and no_forbidden_actions["original_source_full_csv_read_performed"] is False
            and no_forbidden_actions["sealed_holdout_rows_read_count"] == 0
        ),
        "no_strategy_retry_or_candidate_edge": (
            blocks["strategy_search_allowed_now"] is False
            and blocks["retry_strategy_search_allowed_now"] is False
            and blocks["candidate_generation_allowed_now"] is False
            and blocks["edge_claim_allowed_now"] is False
        ),
        "repo_clean_except_current_tool": repo_clean,
        "route_preregistration_still_valid": route_preregistration_still_valid,
        "split_confirmed": split_confirmed,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    plan = {
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "blocked_record_confirmed": blocked_record_confirmed,
        "blocker_class": "HOLDOUT_SAFE_DATA_ACCESS_LAYOUT_BLOCKER",
        "current_all_in_one_panel_retry_rejected": True,
        "current_all_in_one_panel_safe_for_pre_holdout_access": False,
        "current_evidence_chain_quality_after_access_plan": quality,
        "exact_blocker": EXPECTED_BLOCKER,
        "exact_blocker_confirmed": blocked.get("exact_blocker") == EXPECTED_BLOCKER,
        "existing_per_window_safe_artifacts_available": False,
        "future_holdout_safe_access_plan_required": True,
        "future_non_holdout_view_build_preview_required": True,
        "holdout_registry_still_valid": holdout_registry_still_valid,
        "holdout_safe_access_plan_created": replacement_checks_all_true,
        "immediate_strategy_search_retry_allowed": False,
        "metadata_only_offset_or_partition_proof_available": False,
        "next_module": next_module,
        "non_holdout_view_build_allowed_now": False,
        "non_holdout_view_must_physically_exclude_sealed_holdout": True,
        "non_holdout_view_source_plan": "REBUILD_FROM_VALIDATED_SOURCE_DAILY_FILES_DATES_LT_SEALED_HOLDOUT_START",
        "non_holdout_view_train_development_window_end_exclusive": "2025-01-01T00:00:00Z",
        "non_holdout_view_train_development_window_start": "2023-07-01T00:00:00Z",
        "non_holdout_view_validation_window_end_exclusive": "2025-11-01T00:00:00Z",
        "non_holdout_view_validation_window_start": "2025-01-01T00:00:00Z",
        "okx_88_symbol_1h_panel_holdout_safe_access_plan_status": status,
        "preferred_safe_access_route": "BUILD_SEPARATE_NON_HOLDOUT_VIEW_FROM_SOURCE_DATE_FILES_PREVIEW_NEXT",
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "route_preregistration_still_valid": route_preregistration_still_valid,
        "row_offset_index_creation_by_full_panel_scan_allowed": False,
        "sealed_holdout_rows_allowed_in_non_holdout_view": False,
        "sealed_holdout_window_end_exclusive": "2026-05-19T00:00:00Z",
        "sealed_holdout_window_start": "2025-11-01T00:00:00Z",
        "tracked_python_count_at_access_plan_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_load_errors": load_errors,
    }
    plan.update(no_forbidden_actions)
    plan.update(blocks)
    plan.update(approvals)

    blocker_analysis_payload = {
        "blocker_class": "HOLDOUT_SAFE_DATA_ACCESS_LAYOUT_BLOCKER",
        "blocker_interpretation": (
            "The validated 1h panel appears physically sorted/grouped by symbol or lacks a safe row-offset/time-partition index. "
            "Because sealed holdout rows exist after 2025-11-01 for earlier symbols, reading later-symbol pre-holdout rows from "
            "the all-in-one sequential file may require physically scanning sealed holdout rows. The holdout registry forbids this."
        ),
        "current_all_in_one_panel_retry_rejected": True,
        "exact_blocker": EXPECTED_BLOCKER,
        "row_offset_index_creation_by_full_panel_scan_allowed": False,
    }
    options_review = {
        "option_a_metadata_only_row_group_offset_proof": {
            "allowed_if_artifact_proven_without_row_reads": True,
            "available_now": False,
            "decision": "NOT_AVAILABLE_FROM_EXISTING_METADATA",
        },
        "option_b_existing_per_window_safe_artifacts": {
            "allowed_if_artifact_proven_non_holdout_only": True,
            "available_now": False,
            "decision": "NOT_PRESENT",
        },
        "option_c_future_derived_non_holdout_panel_view": {
            "decision": "PREFERRED_PREVIEW_NEXT",
            "future_preview_required": True,
            "source_date_policy": "include dates 2023-07-01 through 2025-10-31; exclude dates >= 2025-11-01",
        },
    }
    build_plan = {
        "build_allowed_now": False,
        "future_preview_required": True,
        "non_holdout_view_must_physically_exclude_sealed_holdout": True,
        "non_holdout_view_source_plan": "REBUILD_FROM_VALIDATED_SOURCE_DAILY_FILES_DATES_LT_SEALED_HOLDOUT_START",
        "panel_scope_symbol_count": 88,
        "sealed_holdout_rows_allowed_in_non_holdout_view": False,
        "sealed_holdout_start": "2025-11-01T00:00:00Z",
        "strategy_execution_must_wait_for_non_holdout_view_build_and_validator": True,
        "train_development_window": {
            "end_exclusive": "2025-01-01T00:00:00Z",
            "start": "2023-07-01T00:00:00Z",
        },
        "validation_window": {
            "end_exclusive": "2025-11-01T00:00:00Z",
            "start": "2025-01-01T00:00:00Z",
        },
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
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_blocker_analysis.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_options_review.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_plan.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_preview_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_self_validator.json",
        ],
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
        "tool_path": str(REPO / TOOL_REL),
    }
    return {
        "plan": plan,
        "blocker_analysis": blocker_analysis_payload,
        "options_review": options_review,
        "build_plan": build_plan,
        "approval_record": approval_record,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payloads = {
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json": outputs["plan"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_blocker_analysis.json": outputs["blocker_analysis"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_options_review.json": outputs["options_review"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_plan.json": outputs["build_plan"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_preview_approval_record.json": outputs["approval_record"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_self_validator.json": outputs["self_validator"],
    }
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["plan"], indent=2, sort_keys=True))
    return 0 if outputs["plan"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
