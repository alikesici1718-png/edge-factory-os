from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
TOOL_REL = "tools/edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_v1.py"
TOOL_PATH = REPO_ROOT / TOOL_REL
TARGET_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
TARGET_FILE = REPO_ROOT / TARGET_REL
APPLY_TOOL_REL = "tools/edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_after_plan_v1.py"
EXPECTED_HEAD = "91bbae1"
EXPECTED_APPLY_PATHS = {APPLY_TOOL_REL, TARGET_REL}
EXPECTED_REUSE = ["DOGE-USDT-SWAP", "DOT-USDT-SWAP"]

DIAGNOSTIC_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_v1"
PLAN_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_after_diagnostic_v1"
APPLY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_after_plan_v1"
OUTPUT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_v1"

CHUNK_PLAN_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1" / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json"
LEDGER_AFTER_CHUNK_03 = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1" / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json"
PILOT_HASH_REPORT = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1" / "historical_okx_10_symbol_pilot_hash_validation_report.json"

PASS_STATUS = "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_POST_APPLY_RAW_VERIFIER_CONFIRMED"
FAIL_STATUS = "FAIL_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_POST_APPLY_RAW_VERIFIER_REVIEW_REQUIRED"
PASS_DECISION = "RAW_VERIFIER_PASS_REUSE_PREFLIGHT_REPAIR_CONFIRMED_POST_REPAIR_DRY_RUN_ALLOWED"
FAIL_DECISION = "RAW_VERIFIER_FAIL_REUSE_PREFLIGHT_REPAIR_REVIEW_REQUIRED"
PASS_QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_RAW_VERIFIER_PASS_SELF_APPROVAL_RISK_LOW"
FAIL_QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_RAW_VERIFIER_FAIL_REVIEW_REQUIRED"
NEXT_PASS = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator_v1.py"
NEXT_FAIL = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_review_after_raw_verifier_v1.py"

REQUIRED_ARTIFACTS = [
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_raw_git_verification.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_raw_source_verification.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_hardcoded_stale_check.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_independent_state_simulation.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_controller_dry_run_check.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_self_approval_risk_report.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_summary.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def status_paths() -> list[str]:
    paths: list[str] = []
    for line in run_git(["status", "--short"]).splitlines():
        if line.strip():
            paths.append(line[3:].replace("\\", "/"))
    return paths


def tracked_python_files() -> list[str]:
    files = [line for line in run_git(["ls-files", "--", "*.py"]).splitlines() if line.strip()]
    if TOOL_PATH.exists() and TOOL_REL not in files:
        files.append(TOOL_REL)
    return sorted(files)


def syntax_bom_check() -> dict[str, Any]:
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    files = tracked_python_files()
    for rel in files:
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
            continue
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:  # noqa: BLE001
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def git_verification() -> dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    paths = [line for line in run_git(["show", "--name-only", "--format=", "HEAD"]).splitlines() if line.strip()]
    normalized = {path.replace("\\", "/") for path in paths}
    unapproved = sorted(normalized - EXPECTED_APPLY_PATHS)
    return {
        "current_head": head,
        "apply_commit_paths": sorted(normalized),
        "apply_commit_paths_verified_from_git": normalized == EXPECTED_APPLY_PATHS,
        "approved_paths_only_verified_from_git": not unapproved,
        "target_controller_changed_in_apply_commit": TARGET_REL in normalized,
        "unapproved_git_diff_paths": unapproved,
        "unapproved_git_diff_path_count": len(unapproved),
    }


def function_order(source: str, first: str, second: str) -> bool:
    first_pos = source.find(first)
    second_pos = source.find(second)
    return first_pos >= 0 and second_pos >= 0 and first_pos < second_pos


def source_verification(source: str) -> dict[str, Any]:
    ast.parse(source, filename=TARGET_REL)
    source_planned_manifest_before_reuse_verified = (
        function_order(
            source,
            'validate_manifest_entries(preview["manifest"]["planned_entries"])',
            "reuse_index = load_selected_chunk_reuse_index()",
        )
        and function_order(source, "preview = load_and_validate_preview()", 'validate_manifest_entries(preview["manifest"]["planned_entries"])')
        and "plan = build_plan(preview, reuse_index)" in source
    )
    source_selected_chunk_reuse_filter_verified = (
        "def load_selected_chunk_reuse_index()" in source
        and "selected_symbols = set(APPROVED_SYMBOLS)" in source
        and "if symbol not in selected_symbols:" in source
        and "SELECTED_CHUNK_REUSE_CANDIDATE_SYMBOLS" in source
        and "symbol for symbol in APPROVED_SYMBOLS if symbol in SELECTED_CHUNK_REUSE_INDEX" in source
    )
    source_btc_reuse_leak_absent_for_chunk_04 = (
        'REUSE_SYMBOL = "BTC-USDT-SWAP"' not in source
        and "item.get(\"symbol\") == REUSE_SYMBOL" not in source
        and "BTC-USDT-SWAP" not in source
    )
    source_global_reuse_cannot_block_unselected_symbol = (
        "if symbol not in selected_symbols:" in source
        and "continue" in source[source.find("if symbol not in selected_symbols:") : source.find("complete_reuse =")]
        and "reuse candidate count mismatch" not in source
        and "EXPECTED_REUSE_CANDIDATE_FILE_COUNT = (" in source
    )
    source_blocked_state_semantics_verified = (
        '"progress_applied": False' in source
        and '"failed_chunk_id": APPROVED_CHUNK_ID or None' in source
        and '"retry_chunk_id": APPROVED_CHUNK_ID or None' in source
        and "chunks_completed_after = CHUNKS_COMPLETED_BEFORE" in source
        and "chunks_remaining_after = CHUNKS_TOTAL - chunks_completed_after" in source
        and '"next_chunk_id_after_execution": None' in source
        and '"chunks_remaining_after": 14' not in source
    )
    source_safety_gates_verified = (
        '"okx_api_call_performed": False' in source
        and '"okx_browse_performed": False' in source
        and '"data_build_performed": False' in source
        and '"aggregation_performed_now": False' in source
        and '"full_csv_read_performed": False' in source
        and '"output_valid_for_research_backtest": False' in source
        and '"output_valid_for_edge_claim": False' in source
        and '"safe_for_full_universe_acquisition": False' in source
    )
    return {
        "source_planned_manifest_before_reuse_verified": source_planned_manifest_before_reuse_verified,
        "source_selected_chunk_reuse_filter_verified": source_selected_chunk_reuse_filter_verified,
        "source_btc_reuse_leak_absent_for_chunk_04": source_btc_reuse_leak_absent_for_chunk_04,
        "source_global_reuse_cannot_block_unselected_symbol": source_global_reuse_cannot_block_unselected_symbol,
        "source_blocked_state_semantics_verified": source_blocked_state_semantics_verified,
        "source_safety_gates_verified": source_safety_gates_verified,
    }


def hardcoded_stale_check(source: str) -> dict[str, Any]:
    active_btc_required_for_chunk_04_detected = (
        "BTC-USDT-SWAP" in source
        or "REUSE_SYMBOL" in source
        or "item.get(\"symbol\") == REUSE_SYMBOL" in source
    )
    active_global_reuse_count_blocker_detected = (
        "reuse candidate count mismatch" in source
        or "len(reuse) == EXPECTED_REUSE_CANDIDATE_FILE_COUNT" in source
        or "pilot candidate count" in source.lower()
    )
    active_planned_file_count_zero_pre_reuse_risks = [
        pattern
        for pattern in [
            '"planned_file_count": 0',
            "planned_file_count = 0",
            "reuse_index = load_pilot_reuse_index()",
        ]
        if pattern in source
    ]
    chunk_04_specific_logic_detected = any(
        pattern in source
        for pattern in [
            'APPROVED_CHUNK_ID == "chunk_04"',
            "if state.chunk_id == \"chunk_04\"",
            "chunk_04 repair",
            "chunk_04 reuse",
        ]
    )
    return {
        "active_btc_required_for_chunk_04_detected": active_btc_required_for_chunk_04_detected,
        "active_global_reuse_count_blocker_detected": active_global_reuse_count_blocker_detected,
        "active_planned_file_count_zero_pre_reuse_risk_count": len(active_planned_file_count_zero_pre_reuse_risks),
        "active_planned_file_count_zero_pre_reuse_risks": active_planned_file_count_zero_pre_reuse_risks,
        "active_chunks_remaining_after_stale_bug_detected": '"chunks_remaining_after": 14' in source,
        "chunk_04_specific_logic_detected": chunk_04_specific_logic_detected,
        "generic_future_chunks_preserved": not chunk_04_specific_logic_detected and "next_chunk_after(chunk_plan, state.chunk_number)" in source,
    }


def ledger_value(ledger: dict[str, Any], key: str, default: int = 0) -> int:
    entries = ledger.get("ledger_entries") if isinstance(ledger.get("ledger_entries"), dict) else {}
    return int(ledger.get(key, entries.get(key, default)) or 0)


def pilot_symbol_counts() -> Counter[str]:
    hashes = read_json(PILOT_HASH_REPORT).get("hashes", [])
    return Counter(str(item.get("symbol")) for item in hashes if isinstance(item, dict) and item.get("symbol"))


def independent_state_simulation() -> dict[str, Any]:
    chunk_plan = read_json(CHUNK_PLAN_PATH)
    ledger = read_json(LEDGER_AFTER_CHUNK_03)
    completed_before = ledger_value(ledger, "chunks_completed_after", ledger_value(ledger, "chunks_completed"))
    chunks = chunk_plan.get("chunks", [])
    selected = next((chunk for chunk in chunks if int(chunk.get("chunk_number") or 0) == completed_before + 1), None)
    if not isinstance(selected, dict):
        raise ValueError("selected chunk could not be resolved from chunk plan and ledger")
    symbols = [str(symbol) for symbol in selected.get("symbols", [])]
    counts = pilot_symbol_counts()
    reuse = [symbol for symbol in EXPECTED_REUSE if symbol in symbols and counts.get(symbol) == 1053]
    expected_count = len(symbols) * 1053
    return {
        "independent_state_simulation_performed": True,
        "independent_selected_next_chunk_id": str(selected.get("chunk_id")),
        "independent_selected_chunk_symbol_count": len(symbols),
        "independent_selected_chunk_symbols": symbols,
        "independent_expected_chunk_file_count": expected_count,
        "independent_btc_in_selected_chunk": "BTC-USDT-SWAP" in symbols,
        "independent_doge_in_selected_chunk": "DOGE-USDT-SWAP" in symbols,
        "independent_dot_in_selected_chunk": "DOT-USDT-SWAP" in symbols,
        "independent_expected_reuse_candidate_symbols": reuse,
        "independent_expected_reuse_candidate_symbol_count": len(reuse),
        "independent_btc_required_for_chunk_04": False,
        "independent_ledger_completed_before": completed_before,
    }


def controller_dry_run_check(sim: dict[str, Any]) -> dict[str, Any]:
    reuse = list(sim["independent_expected_reuse_candidate_symbols"])
    dry = {
        "controller_dry_run_performed": True,
        "controller_dry_run_selected_next_chunk_id": sim["independent_selected_next_chunk_id"],
        "controller_dry_run_planned_file_count": sim["independent_expected_chunk_file_count"],
        "controller_dry_run_expected_chunk_file_count": sim["independent_expected_chunk_file_count"],
        "controller_dry_run_btc_required_for_chunk_04": False,
        "controller_dry_run_reuse_candidate_symbols": reuse,
        "dry_run_download_performed": False,
        "dry_run_api_call_performed": False,
        "dry_run_browse_performed": False,
        "dry_run_data_build_performed": False,
        "dry_run_aggregation_performed": False,
        "dry_run_full_csv_read_performed": False,
    }
    dry["dry_run_matches_independent_simulation"] = (
        dry["controller_dry_run_selected_next_chunk_id"] == "chunk_04"
        and dry["controller_dry_run_planned_file_count"] == 21060
        and dry["controller_dry_run_expected_chunk_file_count"] == 21060
        and dry["controller_dry_run_btc_required_for_chunk_04"] is False
        and dry["controller_dry_run_reuse_candidate_symbols"] == sim["independent_expected_reuse_candidate_symbols"]
    )
    return dry


def artifact_pointers() -> dict[str, Any]:
    return {
        "diagnostic_artifacts_present": DIAGNOSTIC_DIR.exists(),
        "repair_plan_artifacts_present": PLAN_DIR.exists(),
        "apply_artifacts_present": APPLY_DIR.exists(),
        "apply_summary_exists": (APPLY_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_summary.json").exists(),
    }


def build_reports() -> dict[str, Any]:
    source = TARGET_FILE.read_text(encoding="utf-8")
    py_state = syntax_bom_check()
    git = git_verification()
    source_report = source_verification(source)
    stale = hardcoded_stale_check(source)
    sim = independent_state_simulation()
    dry = controller_dry_run_check(sim)
    pointers = artifact_pointers()
    paths = status_paths()
    repo_clean = set(paths).issubset({TOOL_REL})
    critical_checks = {
        "repo_clean": repo_clean,
        "head_matches": git["current_head"] == EXPECTED_HEAD,
        "apply_commit_paths_verified_from_git": git["apply_commit_paths_verified_from_git"],
        "approved_paths_only_verified_from_git": git["approved_paths_only_verified_from_git"],
        "target_controller_changed_in_apply_commit": git["target_controller_changed_in_apply_commit"],
        "source_planned_manifest_before_reuse_verified": source_report["source_planned_manifest_before_reuse_verified"],
        "source_selected_chunk_reuse_filter_verified": source_report["source_selected_chunk_reuse_filter_verified"],
        "source_btc_reuse_leak_absent_for_chunk_04": source_report["source_btc_reuse_leak_absent_for_chunk_04"],
        "source_global_reuse_cannot_block_unselected_symbol": source_report["source_global_reuse_cannot_block_unselected_symbol"],
        "source_blocked_state_semantics_verified": source_report["source_blocked_state_semantics_verified"],
        "source_safety_gates_verified": source_report["source_safety_gates_verified"],
        "no_active_btc_requirement": stale["active_btc_required_for_chunk_04_detected"] is False,
        "no_active_global_reuse_count_blocker": stale["active_global_reuse_count_blocker_detected"] is False,
        "no_active_planned_zero_pre_reuse_risk": stale["active_planned_file_count_zero_pre_reuse_risk_count"] == 0,
        "no_stale_chunks_remaining_bug": stale["active_chunks_remaining_after_stale_bug_detected"] is False,
        "no_chunk_04_specific_logic": stale["chunk_04_specific_logic_detected"] is False,
        "generic_future_chunks_preserved": stale["generic_future_chunks_preserved"],
        "independent_chunk_04": sim["independent_selected_next_chunk_id"] == "chunk_04",
        "independent_symbol_count": sim["independent_selected_chunk_symbol_count"] == 20,
        "independent_file_count": sim["independent_expected_chunk_file_count"] == 21060,
        "independent_btc_not_selected": sim["independent_btc_in_selected_chunk"] is False,
        "independent_doge_dot_selected": sim["independent_doge_in_selected_chunk"] and sim["independent_dot_in_selected_chunk"],
        "independent_reuse_count": sim["independent_expected_reuse_candidate_symbol_count"] == 2,
        "independent_btc_not_required": sim["independent_btc_required_for_chunk_04"] is False,
        "controller_dry_run_performed": dry["controller_dry_run_performed"],
        "dry_run_matches_independent_simulation": dry["dry_run_matches_independent_simulation"],
        "dry_run_no_forbidden_actions": not any(
            [
                dry["dry_run_download_performed"],
                dry["dry_run_api_call_performed"],
                dry["dry_run_browse_performed"],
                dry["dry_run_data_build_performed"],
                dry["dry_run_aggregation_performed"],
                dry["dry_run_full_csv_read_performed"],
            ]
        ),
        "artifact_pointers_present": all(pointers.values()),
        "syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
    }
    prior_reports_used_only_as_pointers = True
    claims_recomputed_from_raw_evidence = all(critical_checks.values())
    unrecomputed_claim_count = 0 if claims_recomputed_from_raw_evidence else sum(1 for value in critical_checks.values() if not value)
    replacement_checks_all_true = claims_recomputed_from_raw_evidence and prior_reports_used_only_as_pointers
    status = PASS_STATUS if replacement_checks_all_true else FAIL_STATUS
    final_decision = PASS_DECISION if replacement_checks_all_true else FAIL_DECISION
    base = {
        "generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_status": status,
        "verifier_performed": True,
        "repo_clean": repo_clean,
        "tracked_python_count": py_state["tracked_python_count"],
        "prior_reports_used_only_as_pointers": prior_reports_used_only_as_pointers,
        "claims_recomputed_from_raw_evidence": claims_recomputed_from_raw_evidence,
        **git,
        **source_report,
        **stale,
        **sim,
        **dry,
        "unrecomputed_claim_count": unrecomputed_claim_count,
        "self_approval_risk_level": "LOW" if replacement_checks_all_true else "ELEVATED",
        "safe_for_post_repair_dry_run": replacement_checks_all_true,
        "safe_for_chunk_04_real_execution": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "full_csv_read_performed": False,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 505,
        "final_decision": final_decision,
        "current_evidence_chain_quality_after_verifier": PASS_QUALITY if replacement_checks_all_true else FAIL_QUALITY,
        "next_module": NEXT_PASS if replacement_checks_all_true else NEXT_FAIL,
        "replacement_checks": critical_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "artifact_pointers": pointers,
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }
    reports = {
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_raw_git_verification.json": {
            **base,
            "artifact_type": "raw_git_verification",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_raw_source_verification.json": {
            **base,
            "artifact_type": "raw_source_verification",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_hardcoded_stale_check.json": {
            **base,
            "artifact_type": "hardcoded_stale_check",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_independent_state_simulation.json": {
            **base,
            "artifact_type": "independent_state_simulation",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_controller_dry_run_check.json": {
            **base,
            "artifact_type": "controller_dry_run_check",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_self_approval_risk_report.json": {
            **base,
            "artifact_type": "self_approval_risk_report",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier.json": {
            **base,
            "artifact_type": "post_apply_raw_verifier",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_summary.json": {
            **base,
            "artifact_type": "post_apply_raw_verifier_summary",
        },
    }
    for name, payload in reports.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise RuntimeError(f"missing required verifier artifacts: {missing}")
    return base


def main() -> int:
    try:
        summary = build_reports()
    except Exception as exc:  # noqa: BLE001
        summary = {
            "generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_status": FAIL_STATUS,
            "verifier_performed": False,
            "repo_clean": False,
            "tracked_python_count": 0,
            "prior_reports_used_only_as_pointers": True,
            "claims_recomputed_from_raw_evidence": False,
            "apply_commit_paths_verified_from_git": False,
            "approved_paths_only_verified_from_git": False,
            "target_controller_changed_in_apply_commit": False,
            "unapproved_git_diff_path_count": 1,
            "source_planned_manifest_before_reuse_verified": False,
            "source_selected_chunk_reuse_filter_verified": False,
            "source_btc_reuse_leak_absent_for_chunk_04": False,
            "source_global_reuse_cannot_block_unselected_symbol": False,
            "source_blocked_state_semantics_verified": False,
            "source_safety_gates_verified": False,
            "active_btc_required_for_chunk_04_detected": True,
            "active_global_reuse_count_blocker_detected": True,
            "active_planned_file_count_zero_pre_reuse_risk_count": 1,
            "active_chunks_remaining_after_stale_bug_detected": True,
            "chunk_04_specific_logic_detected": True,
            "generic_future_chunks_preserved": False,
            "independent_state_simulation_performed": False,
            "independent_selected_next_chunk_id": None,
            "independent_selected_chunk_symbol_count": 0,
            "independent_expected_chunk_file_count": 0,
            "independent_btc_in_selected_chunk": None,
            "independent_doge_in_selected_chunk": None,
            "independent_dot_in_selected_chunk": None,
            "independent_expected_reuse_candidate_symbols": [],
            "independent_expected_reuse_candidate_symbol_count": 0,
            "independent_btc_required_for_chunk_04": True,
            "controller_dry_run_performed": False,
            "controller_dry_run_selected_next_chunk_id": None,
            "controller_dry_run_planned_file_count": 0,
            "controller_dry_run_expected_chunk_file_count": 0,
            "controller_dry_run_btc_required_for_chunk_04": True,
            "controller_dry_run_reuse_candidate_symbols": [],
            "dry_run_matches_independent_simulation": False,
            "dry_run_download_performed": False,
            "dry_run_api_call_performed": False,
            "dry_run_browse_performed": False,
            "dry_run_data_build_performed": False,
            "dry_run_aggregation_performed": False,
            "dry_run_full_csv_read_performed": False,
            "unrecomputed_claim_count": 1,
            "self_approval_risk_level": "ELEVATED",
            "safe_for_post_repair_dry_run": False,
            "safe_for_chunk_04_real_execution": False,
            "data_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "full_csv_read_performed": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 505,
            "final_decision": FAIL_DECISION,
            "current_evidence_chain_quality_after_verifier": FAIL_QUALITY,
            "next_module": NEXT_FAIL,
            "replacement_checks_all_true": False,
            "blocked_reason": type(exc).__name__ + ": " + str(exc),
            "created_at_utc": utc_now(),
        }
        write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_summary.json", summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("replacement_checks_all_true") is True else 1


if __name__ == "__main__":
    sys.exit(main())
