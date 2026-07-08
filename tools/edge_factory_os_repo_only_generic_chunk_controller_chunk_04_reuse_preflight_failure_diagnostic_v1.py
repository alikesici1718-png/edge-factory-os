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
TOOL_REL = "tools/edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_v1.py"
TOOL_PATH = REPO_ROOT / TOOL_REL
EXPECTED_HEAD = "550c6a9"

TARGET_CONTROLLER = REPO_ROOT / "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
FAILED_RUN_SUMMARY = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1" / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_chunk_04_summary.json"
BLOCKED_RECORD_SUMMARY = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_blocked_record_v1" / "repo_only_generic_chunk_controller_chunk_04_failed_cycle_blocked_record_summary.json"
CHUNK_PLAN_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1" / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json"
LEDGER_AFTER_CHUNK_03 = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1" / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json"
PILOT_HASH_REPORT = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1" / "historical_okx_10_symbol_pilot_hash_validation_report.json"
PILOT_VALIDATOR_SUMMARY = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1" / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json"

OUTPUT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_v1"
PASS_STATUS = "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_FAILURE_DIAGNOSED_READY_FOR_REPAIR_PLAN"
FAIL_STATUS = "FAIL_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_FAILURE_DIAGNOSTIC_MANUAL_REVIEW_REQUIRED"
PASS_QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_FAILURE_DIAGNOSED_READY_FOR_REPAIR_PLAN"
FAIL_QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_FAILURE_DIAGNOSTIC_MANUAL_REVIEW_REQUIRED"
NEXT_REPAIR_PLAN = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_after_diagnostic_v1.py"
NEXT_MANUAL_REVIEW = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_manual_review_after_diagnostic_v1.py"

REQUIRED_ARTIFACTS = [
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic.json",
    "repo_only_generic_chunk_controller_chunk_04_btc_reuse_leak_line_map.json",
    "repo_only_generic_chunk_controller_chunk_04_planned_manifest_count_diagnostic.json",
    "repo_only_generic_chunk_controller_chunk_04_chunks_remaining_mismatch_diagnostic.json",
    "repo_only_generic_chunk_controller_chunk_04_expected_reuse_candidates_report.json",
    "repo_only_generic_chunk_controller_chunk_04_failure_root_cause_report.json",
    "repo_only_generic_chunk_controller_chunk_04_repair_scope_recommendation.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_approval_record.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_summary.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-C",
            str(REPO_ROOT),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def status_lines() -> list[str]:
    return [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]


def status_path(line: str) -> str:
    if len(line) >= 3 and line[2] == " ":
        return line[3:].replace("\\", "/")
    return line[2:].lstrip().replace("\\", "/")


def repo_effectively_clean(lines: list[str]) -> bool:
    return {status_path(line) for line in lines}.issubset({TOOL_REL})


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def tracked_python_count() -> int:
    return len([line for line in run_git(["ls-files", "--", "*.py"]).splitlines() if line.strip()])


def syntax_bom_check() -> dict[str, Any]:
    files = [REPO_ROOT / line for line in run_git(["ls-files", "--", "*.py"]).splitlines() if line.strip()]
    if TOOL_PATH.exists() and TOOL_PATH not in files:
        files.append(TOOL_PATH)
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    ok = 0
    for path in files:
        raw = path.read_bytes()
        rel = path.relative_to(REPO_ROOT).as_posix()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
            continue
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            syntax_errors.append({"file": rel, "error": repr(exc)})
    return {
        "files_checked": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "ast_parse_success_count": ok,
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def line_map(source: str, patterns: list[str], label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        for pattern in patterns:
            if pattern in line:
                start = max(1, idx - 2)
                end = min(len(lines), idx + 2)
                rows.append(
                    {
                        "line": idx,
                        "pattern": pattern,
                        "label": label,
                        "text": line.strip(),
                        "context": [{"line": n, "text": lines[n - 1].strip()} for n in range(start, end + 1)],
                    }
                )
    return rows


def chunk_04_symbols(chunk_plan: dict[str, Any]) -> list[str]:
    for chunk in chunk_plan.get("chunks", []):
        if chunk.get("chunk_id") == "chunk_04":
            return [str(symbol) for symbol in chunk.get("symbols", [])]
    return []


def pilot_symbol_counts() -> Counter[str]:
    hashes = read_json(PILOT_HASH_REPORT).get("hashes", [])
    return Counter(str(item.get("symbol")) for item in hashes if isinstance(item, dict) and item.get("symbol"))


def build_reports() -> dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = status_lines()
    source = TARGET_CONTROLLER.read_text(encoding="utf-8")
    ast.parse(source, filename=str(TARGET_CONTROLLER))
    failed = read_json(FAILED_RUN_SUMMARY)
    blocked = read_json(BLOCKED_RECORD_SUMMARY)
    chunk_plan = read_json(CHUNK_PLAN_PATH)
    ledger = read_json(LEDGER_AFTER_CHUNK_03)
    pilot_summary = read_json(PILOT_VALIDATOR_SUMMARY)
    pilot_counts = pilot_symbol_counts()
    selected_symbols = [str(symbol) for symbol in failed.get("chunk_symbols", [])]
    plan_symbols = chunk_04_symbols(chunk_plan)
    expected_reuse = [
        symbol
        for symbol in ("DOGE-USDT-SWAP", "DOT-USDT-SWAP")
        if symbol in selected_symbols and pilot_counts.get(symbol, 0) == 1053
    ]
    btc_logic_lines = line_map(
        source,
        ["REUSE_SYMBOL", "load_pilot_reuse_index", "item.get(\"symbol\") == REUSE_SYMBOL", "reuse candidate count mismatch", "reuse_validation_records"],
        "btc_or_global_reuse_logic",
    )
    planned_lines = line_map(
        source,
        ["def build_plan", "load_pilot_reuse_index()", "plan = build_plan", "planned_file_count", "len(plan)", "EXPECTED_CHUNK_FILE_COUNT"],
        "planned_manifest_or_count_logic",
    )
    chunks_remaining_lines = line_map(
        source,
        ["CHUNKS_REMAINING_AFTER", '"chunks_remaining_after"', "chunks_completed_after", "blocked_payload"],
        "chunks_remaining_or_blocked_state_logic",
    )
    run_order_line = source.find("reuse_index = load_pilot_reuse_index()") < source.find("plan = build_plan")
    btc_in_selected = "BTC-USDT-SWAP" in selected_symbols
    doge_in_selected = "DOGE-USDT-SWAP" in selected_symbols
    dot_in_selected = "DOT-USDT-SWAP" in selected_symbols
    selected_confirmed = selected_symbols == plan_symbols and failed.get("chunk_id") == "chunk_04"
    btc_reuse_logic_found = any("BTC-USDT-SWAP" in row["text"] or "REUSE_SYMBOL" in row["text"] for row in btc_logic_lines)
    reuse_candidate_scope_bug = (
        btc_reuse_logic_found
        and not btc_in_selected
        and failed.get("blocked_reason") == "ExecutionBlocked: BTC-USDT-SWAP reuse candidate count mismatch"
        and "item.get(\"symbol\") == REUSE_SYMBOL" in source
    )
    stale_global_reuse_state_bug = reuse_candidate_scope_bug and 'REUSE_SYMBOL = "BTC-USDT-SWAP"' in source
    planned_ordering_bug = run_order_line and failed.get("planned_file_count") == 0
    planned_zero_root_cause = planned_ordering_bug and "plan = build_plan(preview, reuse_index)" in source
    expected_remaining = int(failed.get("chunks_total") or 0) - int(failed.get("chunks_completed_after") or 0)
    chunks_remaining_root = failed.get("chunks_remaining_after") != expected_remaining and '"chunks_remaining_after": 14' in source
    root_codes = []
    if reuse_candidate_scope_bug:
        root_codes.append("REUSE_CANDIDATE_SCOPE_BUG")
    if planned_ordering_bug:
        root_codes.append("PREFLIGHT_ORDERING_BUG")
    if planned_zero_root_cause:
        root_codes.append("PLANNED_MANIFEST_NOT_BUILT_BEFORE_REUSE_VALIDATION")
    if chunks_remaining_root:
        root_codes.append("BLOCKED_STATE_FIELD_SEMANTICS_BUG")
    if stale_global_reuse_state_bug:
        root_codes.append("STALE_GLOBAL_REUSE_STATE_BUG")
    if not selected_confirmed:
        root_codes.append("CHUNK_PLAN_SELECTION_BUG")
    if ledger.get("chunk_id") != "chunk_03" or ledger.get("next_chunk_id_after_execution") != "chunk_04":
        root_codes.append("LEDGER_STATE_LOAD_BUG")
    root_identified = bool(root_codes) and "UNKNOWN_REQUIRES_MANUAL_REVIEW" not in root_codes
    if not root_identified:
        root_codes.append("UNKNOWN_REQUIRES_MANUAL_REVIEW")
    line_map_report = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_btc_reuse_leak_line_map",
        "target_controller": str(TARGET_CONTROLLER),
        "btc_reuse_logic_lines": btc_logic_lines,
        "reuse_candidate_filter_lines": line_map(source, ["item.get(\"symbol\") == REUSE_SYMBOL", "if source_kind == \"pilot_reuse\"", "reuse_index.get"], "reuse_candidate_filter_or_use"),
        "planned_manifest_construction_lines": planned_lines,
        "chunks_remaining_field_lines": chunks_remaining_lines,
        "failure_block_output_lines": line_map(source, ["def blocked_payload", "blocked = blocked_payload", "write_json(OUTPUT_DIR / (artifact_file"], "blocked_output"),
        "btc_reuse_logic_line_count": len(btc_logic_lines),
    }
    planned_report = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_planned_manifest_count_diagnostic",
        "planned_manifest_built_before_reuse_validation": not run_order_line,
        "planned_manifest_ordering_bug_confirmed": planned_ordering_bug,
        "planned_file_count_zero_root_cause_identified": planned_zero_root_cause,
        "failed_planned_file_count": failed.get("planned_file_count"),
        "expected_chunk_file_count": failed.get("expected_chunk_file_count"),
        "run_order_evidence": {
            "load_pilot_reuse_index_before_build_plan": run_order_line,
            "run_execution_sequence": ["validate_preconditions", "load_and_validate_preview", "load_pilot_reuse_index", "build_plan", "execute_downloads"],
        },
        "patch_need": "Build selected chunk planned manifest before loading/validating selected-chunk reuse candidates.",
    }
    chunks_report = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_chunks_remaining_mismatch_diagnostic",
        "chunks_remaining_mismatch_root_cause_identified": chunks_remaining_root,
        "chunks_remaining_after_reported": failed.get("chunks_remaining_after"),
        "chunks_remaining_after_expected_if_no_progress": expected_remaining,
        "source_hardcoded_blocked_chunks_remaining_after_14": '"chunks_remaining_after": 14' in source,
        "field_semantics_recommendation": "For blocked/no-progress runs, emit chunks_remaining_current from loaded state, keep chunks_completed_after equal to before, and avoid a misleading hardcoded chunks_remaining_after.",
    }
    reuse_report = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_expected_reuse_candidates_report",
        "chunk_04_symbols": selected_symbols,
        "btc_in_selected_chunk": btc_in_selected,
        "doge_in_selected_chunk": doge_in_selected,
        "dot_in_selected_chunk": dot_in_selected,
        "pilot_validator_provenance_complete": all(
            pilot_summary.get(key) is True
            for key in ("download_execution_validated", "all_reused_files_revalidated", "all_hashes_recomputed", "all_zip_open_success")
        ),
        "pilot_hash_counts_for_relevant_symbols": {
            "BTC-USDT-SWAP": pilot_counts.get("BTC-USDT-SWAP", 0),
            "DOGE-USDT-SWAP": pilot_counts.get("DOGE-USDT-SWAP", 0),
            "DOT-USDT-SWAP": pilot_counts.get("DOT-USDT-SWAP", 0),
        },
        "expected_chunk_04_reuse_candidate_symbols": expected_reuse,
        "expected_chunk_04_reuse_candidate_symbol_count": len(expected_reuse),
        "unexpected_btc_reuse_requirement_confirmed": reuse_candidate_scope_bug,
    }
    root_report = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_failure_root_cause_report",
        "root_cause_identified": root_identified,
        "root_cause_codes": root_codes,
        "reuse_candidate_scope_bug_confirmed": reuse_candidate_scope_bug,
        "stale_global_reuse_state_bug_confirmed": stale_global_reuse_state_bug,
        "planned_manifest_ordering_bug_confirmed": planned_ordering_bug,
        "planned_file_count_zero_root_cause_identified": planned_zero_root_cause,
        "chunks_remaining_mismatch_root_cause_identified": chunks_remaining_root,
        "chunk_plan_selection_bug_confirmed": not selected_confirmed,
        "ledger_state_load_bug_confirmed": ledger.get("chunk_id") != "chunk_03" or ledger.get("next_chunk_id_after_execution") != "chunk_04",
    }
    repair_scope = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_repair_scope_recommendation",
        "exact_patch_requirements_identified": root_identified,
        "patch_existing_generic_controller_only": True,
        "chunk_specific_module_required": False,
        "patch_requirements": [
            "Generate selected chunk planned manifest/count before reuse validation.",
            "Derive selected_chunk_symbols before reuse checks.",
            "Filter pilot reuse candidate universe by selected_chunk_symbols.",
            "Make BTC impossible to require unless BTC is in the selected chunk.",
            "For chunk_04, allow DOGE-USDT-SWAP and DOT-USDT-SWAP reuse candidates when their 1053 pilot records are complete.",
            "If selected chunk has no reuse candidates, set reuse count to zero and proceed to bounded downloads.",
            "Fix blocked-run state fields so no-progress failures do not report hardcoded chunks_remaining_after=14.",
            "Preserve fail-closed behavior and no API/browse/build/aggregation/full CSV read gates.",
        ],
    }
    approval = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_plan_approval_record",
        "created_at_utc": utc_now(),
        "approval_grants_diagnostic_now": True,
        "approval_grants_patch_plan_next": root_identified,
        "approval_grants_patch_apply_now": False,
        "approval_grants_chunk_04_rerun_now": False,
        "approval_grants_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "next_module": NEXT_REPAIR_PLAN if root_identified else NEXT_MANUAL_REVIEW,
    }
    checks = {
        "head_matches": head == EXPECTED_HEAD,
        "repo_clean": repo_effectively_clean(status_lines()),
        "failed_run_confirmed": failed.get("historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_status") == "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CYCLE_EXECUTION_FAILED",
        "blocked_record_confirmed": blocked.get("replacement_checks_all_true") is True and blocked.get("approval_grants_diagnostic_next") is True,
        "fail_closed_before_download_confirmed": failed.get("generic_cycle_execution_performed") is False and failed.get("data_download_performed") is False,
        "selected_chunk_symbols_confirmed": selected_confirmed,
        "btc_reuse_logic_found": btc_reuse_logic_found,
        "root_cause_identified": root_identified,
        "exact_patch_requirements_identified": repair_scope["exact_patch_requirements_identified"],
        "patch_existing_generic_controller_only": repair_scope["patch_existing_generic_controller_only"],
        "chunk_specific_module_not_required": repair_scope["chunk_specific_module_required"] is False,
        "approval_no_apply_or_rerun": approval["approval_grants_patch_apply_now"] is False and approval["approval_grants_chunk_04_rerun_now"] is False,
        "no_forbidden_actions": True,
    }
    passed = all(checks.values())
    summary = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_summary",
        "generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_status": PASS_STATUS if passed else FAIL_STATUS,
        "diagnostic_performed": True,
        "created_at_utc": utc_now(),
        "failed_chunk_id": failed.get("chunk_id"),
        "failed_run_confirmed": checks["failed_run_confirmed"],
        "fail_closed_before_download_confirmed": checks["fail_closed_before_download_confirmed"],
        "no_download_confirmed": failed.get("data_download_performed") is False and failed.get("archive_download_performed") is False,
        "no_code_change_confirmed": True,
        "selected_chunk_symbols_confirmed": selected_confirmed,
        "btc_in_selected_chunk": btc_in_selected,
        "doge_in_selected_chunk": doge_in_selected,
        "dot_in_selected_chunk": dot_in_selected,
        "btc_reuse_logic_found": btc_reuse_logic_found,
        "btc_reuse_logic_line_count": len(btc_logic_lines),
        "reuse_candidate_scope_bug_confirmed": reuse_candidate_scope_bug,
        "stale_global_reuse_state_bug_confirmed": stale_global_reuse_state_bug,
        "planned_manifest_built_before_reuse_validation": planned_report["planned_manifest_built_before_reuse_validation"],
        "planned_manifest_ordering_bug_confirmed": planned_ordering_bug,
        "planned_file_count_zero_root_cause_identified": planned_zero_root_cause,
        "chunks_remaining_mismatch_root_cause_identified": chunks_remaining_root,
        "expected_chunk_04_reuse_candidate_symbols": expected_reuse,
        "expected_chunk_04_reuse_candidate_symbol_count": len(expected_reuse),
        "unexpected_btc_reuse_requirement_confirmed": reuse_candidate_scope_bug,
        "root_cause_identified": root_identified,
        "root_cause_codes": root_codes,
        "exact_patch_requirements_identified": repair_scope["exact_patch_requirements_identified"],
        "patch_existing_generic_controller_only": repair_scope["patch_existing_generic_controller_only"],
        "chunk_specific_module_required": repair_scope["chunk_specific_module_required"],
        "diagnostic_approval_record_created": approval["approval_grants_diagnostic_now"],
        "approval_grants_patch_plan_next": approval["approval_grants_patch_plan_next"],
        "approval_grants_patch_apply_now": approval["approval_grants_patch_apply_now"],
        "approval_grants_chunk_04_rerun_now": approval["approval_grants_chunk_04_rerun_now"],
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "full_csv_read_performed": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": int(failed.get("active_p1_attention_count") or 0),
        "current_evidence_chain_quality_after_diagnostic": PASS_QUALITY if passed else FAIL_QUALITY,
        "next_module": NEXT_REPAIR_PLAN if passed else NEXT_MANUAL_REVIEW,
        "replacement_checks_all_true": passed,
        "replacement_checks": checks,
    }
    diagnostic = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic",
        "summary": summary,
        "line_map": line_map_report,
        "planned_manifest_count_diagnostic": planned_report,
        "chunks_remaining_mismatch_diagnostic": chunks_report,
        "expected_reuse_candidates_report": reuse_report,
        "root_cause_report": root_report,
        "repair_scope_recommendation": repair_scope,
        "approval_record": approval,
        "forbidden_actions_performed": {
            "patch": False,
            "chunk_04_rerun": False,
            "download": False,
            "api": False,
            "browse": False,
            "url_fetch": False,
            "zip_csv_parquet_read": False,
            "full_csv_read": False,
            "data_build": False,
            "aggregation": False,
            "delete": False,
            "move": False,
            "cleanup": False,
            "research_backtest_edge": False,
            "runtime_capital_live": False,
        },
    }
    return diagnostic, line_map_report, planned_report, chunks_report, reuse_report, root_report, repair_scope, approval, summary


def run() -> dict[str, Any]:
    payloads = build_reports()
    names = REQUIRED_ARTIFACTS
    for name, payload in zip(names, payloads, strict=True):
        write_json(OUTPUT_DIR / name, payload)
    syntax = syntax_bom_check()
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    summary = payloads[-1]
    if missing or syntax["syntax_error_count"] or syntax["bom_error_count"]:
        summary["replacement_checks_all_true"] = False
        summary["missing_artifacts"] = missing
        summary["syntax_bom_report"] = syntax
        write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_summary.json", summary)
    return summary


def main() -> int:
    summary = run()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    sys.exit(main())
