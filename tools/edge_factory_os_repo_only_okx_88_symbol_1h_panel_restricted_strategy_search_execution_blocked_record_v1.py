#!/usr/bin/env python3
"""Repo-only blocked record after restricted strategy-search fail-closed.

This module records the sealed-holdout read guard block. It does not repair
access, read the 1h panel, read original 1m sources, run strategy search,
generate candidates, claim edge, release a family, or touch runtime/live/capital.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_v1"

EXECUTION_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_after_route_preregistration_v1"
EXECUTION_REPORT = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_report.json"
ACCESS_LOG = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_data_window_access_log.json"

PREREG_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_after_strategy_search_preview_v1"
PREREG = PREREG_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration.json"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"

EXPECTED_HEAD = "c54e49c"
EXPECTED_BLOCKER = "PANEL_SORTED_BY_SYMBOL_WITHOUT_ROW_OFFSET_INDEX_REQUIRES_SEALED_HOLDOUT_SCAN_TO_REACH_LATER_SYMBOL_PRE_HOLDOUT_ROWS"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_EXECUTION_BLOCKED_RECORD_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_EXECUTION_BLOCKED_RECORD_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1.py"
NEXT_FAIL_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_failed_review_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_STRATEGY_SEARCH_BLOCKED_RECORD_READY_HOLDOUT_SAFE_ACCESS_PLAN_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_STRATEGY_SEARCH_BLOCKED_RECORD_FAILED_REVIEW_REQUIRED"


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
        "execution_report": EXECUTION_REPORT,
        "access_log": ACCESS_LOG,
        "preregistration": PREREG,
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
    execution = loaded.get("execution_report", {})
    access_log = loaded.get("access_log", {})
    prereg = loaded.get("preregistration", {})
    registry = loaded.get("registry", {})

    blocked_execution_confirmed = (
        execution.get("okx_88_symbol_1h_panel_restricted_strategy_search_execution_status")
        == "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_EXECUTION_SEALED_HOLDOUT_READ_GUARD"
        and execution.get("blocked_reason") == EXPECTED_BLOCKER
        and execution.get("restricted_strategy_search_execution_performed") is False
        and execution.get("strategy_search_executed") is False
        and execution.get("tested_config_count") == 0
        and execution.get("sealed_holdout_accessed") is False
        and execution.get("sealed_holdout_rows_read_count") == 0
        and execution.get("candidate_generation_performed") is False
        and execution.get("edge_claim_performed") is False
        and execution.get("family_release_performed") is False
        and execution.get("output_valid_for_edge_claim") is False
        and execution.get("replacement_checks_all_true") is False
        and access_log.get("safe_pre_holdout_read_available") is False
        and access_log.get("sealed_holdout_accessed") is False
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
        and registry.get("sealed_holdout_access_blocked_during_strategy_search") is True
        and registry.get("replacement_checks_all_true") is True
    )
    no_forbidden_actions = {
        "aggregation_performed_now": False,
        "data_build_performed": False,
        "data_download_performed": False,
        "full_1h_panel_read_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "original_source_full_csv_read_performed": False,
        "strategy_search_executed": False,
    }
    release_blocks = {
        "access_repair_apply_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "retry_strategy_search_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
    }
    approvals = {
        "approval_grants_access_repair_apply_now": False,
        "approval_grants_blocked_record_now": True,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_holdout_safe_access_plan_next": True,
        "approval_grants_holdout_access_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
    }

    replacement_checks = {
        "blocked_execution_confirmed": blocked_execution_confirmed,
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "exact_blocker_recorded": execution.get("blocked_reason") == EXPECTED_BLOCKER,
        "holdout_registry_still_valid": holdout_registry_still_valid,
        "no_access_repair_apply_now": release_blocks["access_repair_apply_allowed_now"] is False,
        "no_candidate_edge_runtime_enablement": (
            release_blocks["candidate_generation_allowed_now"] is False
            and release_blocks["edge_claim_allowed_now"] is False
            and release_blocks["runtime_live_capital_allowed_now"] is False
        ),
        "no_forbidden_reads_or_execution": (
            no_forbidden_actions["full_1h_panel_read_performed"] is False
            and no_forbidden_actions["original_source_full_csv_read_performed"] is False
            and no_forbidden_actions["strategy_search_executed"] is False
        ),
        "repo_clean_except_current_tool": repo_clean,
        "route_preregistration_still_valid": route_preregistration_still_valid,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_FAIL_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    record = {
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "blocked_execution_confirmed": blocked_execution_confirmed,
        "blocked_record_created": replacement_checks_all_true,
        "blocker_class": "HOLDOUT_SAFE_DATA_ACCESS_LAYOUT_BLOCKER",
        "blocker_interpretation_created": True,
        "candidate_generation_performed": False,
        "current_evidence_chain_quality_after_blocked_record": quality,
        "edge_claim_performed": False,
        "exact_blocker": EXPECTED_BLOCKER,
        "exact_blocker_recorded": execution.get("blocked_reason") == EXPECTED_BLOCKER,
        "family_release_performed": False,
        "future_holdout_safe_access_plan_required": True,
        "holdout_registry_still_valid": holdout_registry_still_valid,
        "next_module": next_module,
        "okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_status": status,
        "output_valid_for_edge_claim": False,
        "release_blocks_created": True,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "restricted_strategy_search_execution_performed": False,
        "route_preregistration_still_valid": route_preregistration_still_valid,
        "sealed_holdout_accessed": False,
        "sealed_holdout_rows_read_count": 0,
        "tested_config_count": 0,
        "tracked_python_count_at_blocked_record_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_load_errors": load_errors,
    }
    record.update(no_forbidden_actions)
    record.update(release_blocks)
    record.update(approvals)

    analysis = {
        "blocker_class": "HOLDOUT_SAFE_DATA_ACCESS_LAYOUT_BLOCKER",
        "blocker_interpretation": (
            "The validated 1h output appears sorted by symbol rather than globally time-partitioned or indexed by row offsets. "
            "Without a safe row-offset/time-partition index, reading pre-holdout rows for later symbols may require physically "
            "scanning through earlier symbols' sealed holdout rows. Physical scan/read of sealed holdout rows is forbidden by "
            "the holdout registry, so execution correctly failed closed before strategy search."
        ),
        "exact_blocker": EXPECTED_BLOCKER,
        "failure_is_data_access_layout_related_not_strategy_result": True,
        "repair_attempted_now": False,
        "route_preregistration_still_valid": route_preregistration_still_valid,
    }
    retry_policy = {
        "access_repair_apply_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "future_holdout_safe_access_plan_required": True,
        "retry_strategy_search_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
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
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_access_blocker_analysis.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_block_policy.json",
            "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_self_validator.json",
        ],
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
        "tool_path": str(REPO / TOOL_REL),
    }
    return {
        "record": record,
        "analysis": analysis,
        "retry_policy": retry_policy,
        "approval_record": approval_record,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payloads = {
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record.json": outputs["record"],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_access_blocker_analysis.json": outputs["analysis"],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_block_policy.json": outputs["retry_policy"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_approval_record.json": outputs["approval_record"],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_self_validator.json": outputs["self_validator"],
    }
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["record"], indent=2, sort_keys=True))
    return 0 if outputs["record"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
