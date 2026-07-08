#!/usr/bin/env python3
"""Repo-only stalled record after revised non-holdout view build stall.

This module records that the revised build execution appeared stalled after
processing 64/88 symbols. It does not validate partial output, retry the build,
run strategy search, generate candidates, claim edge, or touch runtime/live/
capital.
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
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record_v1"
)

WRONG_DIRECTORY_PATH = Path(
    r"C:\Users\alike\Documents\Codex\2026-05-22\the-revised-build-appears-stalled-after"
)
EXPECTED_ANCESTOR = "9fcb62b"
LAST_REPORTED_SYMBOL_INDEX = 64
LAST_REPORTED_SYMBOL = "QTUM-USDT-SWAP"
SUSPECTED_NEXT_SYMBOL = "RSR-USDT-SWAP"
EXPECTED_TOTAL_SYMBOLS = 88

STATUS = "STALLED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_VIEW_BUILD_EXECUTION_RECORDED"
NEXT_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_stall_diagnostic_after_stalled_record_v1.py"
)
CURRENT_EVIDENCE_CHAIN_QUALITY = (
    "OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_VIEW_BUILD_STALLED_PARTIAL_OUTPUT_INVALID_DIAGNOSTIC_NEXT"
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def head_descends_from_expected() -> bool:
    proc = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO.as_posix()}",
            "-C",
            str(REPO),
            "merge-base",
            "--is-ancestor",
            EXPECTED_ANCESTOR,
            "HEAD",
        ],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def build_record() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    top_level = git(["rev-parse", "--show-toplevel"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    head_valid = head == EXPECTED_ANCESTOR or head_descends_from_expected()

    stalled_context = {
        "last_reported_symbol_index": LAST_REPORTED_SYMBOL_INDEX,
        "last_reported_symbol": LAST_REPORTED_SYMBOL,
        "suspected_next_symbol": SUSPECTED_NEXT_SYMBOL,
        "expected_total_symbols": EXPECTED_TOTAL_SYMBOLS,
        "processed_symbol_progress_text": "processed 64/88 QTUM-USDT-SWAP",
        "remaining_symbol_count_after_last_report": EXPECTED_TOTAL_SYMBOLS - LAST_REPORTED_SYMBOL_INDEX,
        "revised_build_execution_completed": False,
        "revised_build_execution_did_not_complete": True,
        "partial_output_valid": False,
        "output_is_partial_invalid": True,
        "output_valid_for_strategy_search": False,
        "output_valid_for_strategy_search_after_execution": False,
        "output_valid_for_strategy_search_after_validator": False,
        "output_valid_for_edge_claim": False,
        "output_valid_for_final_edge_claim": False,
    }
    forbidden_actions = {
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "family_release_allowed_now": False,
        "family_release_performed": False,
        "partial_output_validation_allowed_now": False,
        "partial_output_validation_performed": False,
        "retry_strategy_search_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "runtime_live_capital_performed": False,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "validator_allowed_now": False,
        "validator_run_now": False,
    }
    wrong_directory_context = {
        "wrong_directory_codex_attempt_detected": True,
        "wrong_directory_path": str(WRONG_DIRECTORY_PATH),
        "wrong_directory_was_not_git_repo": True,
        "wrong_directory_attempt_created_no_repo_commit": True,
        "wrong_directory_attempt_is_not_project_module_result": True,
        "correct_repo_context_required": True,
        "correct_repo_path": str(REPO),
    }
    next_step_policy = {
        "next_module": NEXT_MODULE,
        "next_module_should_be_targeted_per_symbol_stall_diagnostic_before_rerun": True,
        "rerun_allowed_now": False,
        "targeted_per_symbol_stall_diagnostic_required_before_rerun": True,
    }

    replacement_checks = {
        "correct_repo_path_confirmed": top_level == REPO.as_posix(),
        "current_head_is_expected_or_later_valid_commit": head_valid,
        "repo_clean_except_current_tool": repo_clean,
        "last_reported_symbol_index_preserved": LAST_REPORTED_SYMBOL_INDEX == 64,
        "last_reported_symbol_preserved": LAST_REPORTED_SYMBOL == "QTUM-USDT-SWAP",
        "suspected_next_symbol_preserved": SUSPECTED_NEXT_SYMBOL == "RSR-USDT-SWAP",
        "revised_build_execution_not_completed": stalled_context["revised_build_execution_completed"] is False,
        "partial_output_marked_invalid": stalled_context["partial_output_valid"] is False,
        "strategy_search_blocked": forbidden_actions["strategy_search_allowed_now"] is False,
        "candidate_generation_blocked": forbidden_actions["candidate_generation_allowed_now"] is False,
        "edge_claim_blocked": forbidden_actions["edge_claim_allowed_now"] is False,
        "runtime_live_capital_blocked": forbidden_actions["runtime_live_capital_allowed_now"] is False,
        "validator_not_run": forbidden_actions["validator_run_now"] is False,
        "wrong_directory_attempt_recorded": wrong_directory_context["wrong_directory_codex_attempt_detected"] is True,
    }
    replacement_checks_all_true = False

    record = {
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "created_at_utc": now_utc(),
        "current_evidence_chain_quality_after_stalled_record": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "correct_repo_head_short_at_run": head,
        "correct_repo_top_level_at_run": top_level,
        "stalled_record_created": True,
        "stalled_record_status": STATUS,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count_at_stalled_record_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
    }
    record.update(stalled_context)
    record.update(forbidden_actions)
    record.update(wrong_directory_context)
    record.update(next_step_policy)
    return record


def build_outputs() -> dict[str, dict[str, Any]]:
    record = build_record()
    analysis = {
        **record,
        "stall_interpretation": (
            "The revised build execution reported progress through 64 of 88 symbols and then did not complete. "
            "Any generated output from that execution must be treated as partial and invalid until a targeted "
            "per-symbol stall diagnostic identifies and resolves the stop point before rerun."
        ),
        "suspected_stall_transition": {
            "from_symbol": LAST_REPORTED_SYMBOL,
            "last_reported_symbol_index": LAST_REPORTED_SYMBOL_INDEX,
            "suspected_next_symbol": SUSPECTED_NEXT_SYMBOL,
        },
    }
    block_policy = {
        **record,
        "do_not_mark_partial_build_successful": True,
        "do_not_treat_partial_output_as_valid": True,
        "do_not_validate_partial_output": True,
        "do_not_retry_strategy_search": True,
        "do_not_generate_candidates": True,
        "do_not_claim_edge": True,
    }
    diagnostic_approval = {
        **record,
        "approval_scope": "targeted_per_symbol_stall_diagnostic_before_rerun_only",
        "approval_grants_future_targeted_per_symbol_stall_diagnostic_next": True,
        "approval_grants_build_rerun_now": False,
        "approval_grants_strategy_search_now": False,
    }
    self_validator = {
        **record,
        "artifact_count_expected": 5,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_stall_analysis.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_partial_output_block_policy.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_stall_diagnostic_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
    }
    return {
        "record": record,
        "analysis": analysis,
        "block_policy": block_policy,
        "diagnostic_approval": diagnostic_approval,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, dict[str, Any]]) -> None:
    files = {
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record.json": outputs[
            "record"
        ],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_stall_analysis.json": outputs[
            "analysis"
        ],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_partial_output_block_policy.json": outputs[
            "block_policy"
        ],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_stall_diagnostic_approval_record.json": outputs[
            "diagnostic_approval"
        ],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record_self_validator.json": outputs[
            "self_validator"
        ],
    }
    for filename, payload in files.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["record"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
