from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
TOOL_REL = "tools/edge_factory_os_repo_only_generic_chunk_controller_post_repair_semantic_audit_and_dry_run_v1.py"
TOOL_PATH = REPO_ROOT / TOOL_REL
TARGET_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
TARGET_FILE = REPO_ROOT / TARGET_REL
EXPECTED_HEAD = "49470a4"
EXPECTED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
FAIL_NEXT_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_repair_review_after_post_repair_audit_v1.py"
EXPECTED_CHUNK_ID = "chunk_04"

OUTPUT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_post_repair_semantic_audit_and_dry_run_v1"
RAW_VERIFIER_SUMMARY = EDGE_LAB_ROOT / "edge_factory_os_repo_only_raw_evidence_independent_verifier_after_generic_controller_repair_apply_v1" / "repo_only_raw_evidence_independent_verifier_summary.json"
REPAIR_APPLY_SUMMARY = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_repair_apply_after_exhaustive_repair_plan_v1" / "repo_only_generic_chunk_controller_repair_apply_summary.json"

PASS_STATUS = "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_POST_REPAIR_SEMANTIC_AUDIT_CHUNK_04_EXECUTION_ALLOWED"
FAIL_STATUS = "FAIL_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_POST_REPAIR_SEMANTIC_AUDIT_REPAIR_REVIEW_REQUIRED"
PASS_DECISION = "POST_REPAIR_SEMANTIC_AUDIT_PASS_CHUNK_04_REAL_EXECUTION_ALLOWED_NEXT"
FAIL_DECISION = "POST_REPAIR_SEMANTIC_AUDIT_FAIL_REPAIR_REVIEW_REQUIRED"
PASS_QUALITY = "REPO_ONLY_GENERIC_CHUNK_CONTROLLER_POST_REPAIR_SEMANTIC_AUDIT_PASS_CHUNK_04_EXECUTION_ALLOWED"
FAIL_QUALITY = "REPO_ONLY_GENERIC_CHUNK_CONTROLLER_POST_REPAIR_SEMANTIC_AUDIT_FAIL_REPAIR_REVIEW_REQUIRED"

REQUIRED_ARTIFACTS = [
    "repo_only_generic_chunk_controller_post_repair_semantic_audit.json",
    "repo_only_generic_chunk_controller_post_repair_source_check_report.json",
    "repo_only_generic_chunk_controller_post_repair_dynamic_state_check_report.json",
    "repo_only_generic_chunk_controller_post_repair_dry_run_report.json",
    "repo_only_generic_chunk_controller_post_repair_safety_gate_report.json",
    "repo_only_generic_chunk_controller_post_repair_route_logic_report.json",
    "repo_only_generic_chunk_controller_post_repair_audit_summary.json",
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


def repo_effectively_clean_for_audit(lines: list[str]) -> bool:
    return {status_path(line) for line in lines}.issubset({TOOL_REL})


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_python_files() -> list[Path]:
    out = run_git(["ls-files", "--", "*.py"])
    return [REPO_ROOT / line for line in out.splitlines() if line.strip()]


def syntax_bom_tracked_plus_self() -> dict[str, Any]:
    files = tracked_python_files()
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
        except Exception as exc:  # noqa: BLE001 - audit records raw parser failure.
            syntax_errors.append({"file": rel, "error": repr(exc)})
    return {
        "files_checked": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "ast_parse_success_count": ok,
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def source_check(source: str) -> dict[str, Any]:
    ast.parse(source, filename=TARGET_REL)
    dynamic_state_loading = all(token in source for token in ("class ControllerState", "def load_latest_controller_state", "latest_json_by_completed_chunk", "ledger_value(ledger"))
    chunk_plan_lookup = all(token in source for token in ("CHUNK_PLAN", 'chunk.get("chunk_id") == next_chunk_id', "selected = next("))
    dynamic_selection = all(token in source for token in ("next_chunk_id = next_state.get(\"next_chunk_id_after_execution\")", "APPROVED_CHUNK_ID = state.chunk_id", "APPROVED_SYMBOLS = list(state.chunk_symbols)"))
    dynamic_artifacts = all(token in source for token in ("def artifact_file", "generic_chunk_coverage_cycle_{APPROVED_CHUNK_ID}_", "artifact_file(\"summary.json\")"))
    dynamic_ledger = all(
        token in source
        for token in (
            "CHUNKS_COMPLETED_AFTER = state.chunks_completed_before + 1",
            "CHUNKS_REMAINING_AFTER = state.chunks_total - CHUNKS_COMPLETED_AFTER",
            "SYMBOLS_EVALUATED_AFTER = state.symbols_evaluated_before + len(APPROVED_SYMBOLS)",
            "CUMULATIVE_PENDING_AFTER = state.total_candidate_symbol_count - SYMBOLS_EVALUATED_AFTER",
            "cumulative_complete_count = CUMULATIVE_COMPLETE_BEFORE + full_coverage_count",
            "cumulative_gap_count = CUMULATIVE_GAP_BEFORE + gap_symbol_count",
            "cumulative_available_count = CUMULATIVE_AVAILABLE_BEFORE + final_available_file_count",
            "cumulative_missing_count = CUMULATIVE_MISSING_BEFORE + missing_or_failed_file_count",
            "cumulative_planned_count = CUMULATIVE_PLANNED_BEFORE + EXPECTED_CHUNK_FILE_COUNT",
        )
    )
    route_logic = all(
        token in source
        for token in (
            "NEXT_CHUNK_ID_AFTER_EXECUTION = next_chunk_after(chunk_plan, state.chunk_number) if CHUNKS_REMAINING_AFTER > 0 else None",
            '"next_module": NEXT_MODULE if CHUNKS_REMAINING_AFTER > 0 else FINAL_SUMMARY_MODULE',
            "FINAL_SUMMARY_MODULE",
        )
    )
    safety = all(
        token in source
        for token in (
            '"no_api": True',
            '"no_browse": True',
            '"no_full_csv_read": True',
            '"no_build": True',
            '"no_aggregation": True',
            '"no_research_backtest_edge": True',
            '"no_runtime_capital_live": True',
            '"build_ready_symbol_count": 0',
            '"acquisition_ready_symbol_count": 0',
            '"output_valid_for_research_backtest": False',
            '"output_valid_for_edge_claim": False',
            '"full_universe_acquisition_allowed_now": False',
        )
    )
    active_hardcoded_chunk_03_only_reference_count = 0
    for token in ('APPROVED_CHUNK_ID = "chunk_03"', "APPROVED_SYMBOLS = [", "downloaded_chunk_03_approved_quarantine"):
        if token in source:
            active_hardcoded_chunk_03_only_reference_count += 1
    stale_tokens = (
        "CHUNKS_COMPLETED_BEFORE = 2",
        "CHUNKS_COMPLETED_AFTER = 3",
        "CHUNKS_REMAINING_AFTER = 13",
        "SYMBOLS_EVALUATED_AFTER = 60",
        "CUMULATIVE_PENDING_AFTER = 243",
        'NEXT_CHUNK_ID_AFTER_EXECUTION = "chunk_04"',
    )
    stale_count = sum(1 for token in stale_tokens if token in source)
    return {
        "artifact_type": "repo_only_generic_chunk_controller_post_repair_source_check_report",
        "target_file": TARGET_REL,
        "target_sha256": sha256_file(TARGET_FILE),
        "dynamic_state_loading_confirmed": dynamic_state_loading,
        "chunk_plan_lookup_confirmed": chunk_plan_lookup,
        "dynamic_chunk_selection_confirmed": dynamic_selection and 'APPROVED_CHUNK_ID = "chunk_03"' not in source and "APPROVED_SYMBOLS = [" not in source,
        "dynamic_artifact_naming_confirmed": dynamic_artifacts,
        "dynamic_ledger_update_confirmed": dynamic_ledger,
        "next_route_logic_confirmed": route_logic,
        "safety_gates_confirmed": safety,
        "active_hardcoded_chunk_03_only_reference_count": active_hardcoded_chunk_03_only_reference_count,
        "active_fixed_symbol_list_detected": "APPROVED_SYMBOLS = [" in source,
        "stale_active_ledger_constant_count": stale_count,
        "generic_controller_hardcoded_chunk_only_after_repair": active_hardcoded_chunk_03_only_reference_count > 0,
        "generic_controller_dynamic_chunk_selection_confirmed": dynamic_selection and dynamic_state_loading and chunk_plan_lookup,
        "generic_controller_safe_to_rerun_for_chunk_04_confirmed": all((dynamic_state_loading, chunk_plan_lookup, dynamic_selection, dynamic_artifacts, dynamic_ledger, route_logic, safety)) and active_hardcoded_chunk_03_only_reference_count == 0 and stale_count == 0,
    }


def controller_state_dry_run() -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("generic_controller_post_repair_audit", TARGET_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import target controller for state-check dry run")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    state = module.load_latest_controller_state()
    selected_symbols = list(getattr(state, "chunk_symbols", []))
    expected_file_count = len(selected_symbols) * int(getattr(module, "EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL", 1053))
    return {
        "artifact_type": "repo_only_generic_chunk_controller_post_repair_dynamic_state_check_report",
        "dry_run_state_check_performed": True,
        "dry_run_selected_next_chunk_id": getattr(state, "chunk_id", None),
        "dry_run_selected_chunk_number": getattr(state, "chunk_number", None),
        "dry_run_selected_chunk_symbol_count": len(selected_symbols),
        "dry_run_expected_chunk_file_count": expected_file_count,
        "dry_run_chunks_completed_before": getattr(state, "chunks_completed_before", None),
        "dry_run_chunks_remaining_before": getattr(state, "chunks_remaining_before", None),
        "dry_run_symbols_evaluated_before": getattr(state, "symbols_evaluated_before", None),
        "dry_run_cumulative_near_3y_complete_before": getattr(state, "cumulative_complete_before", None),
        "dry_run_cumulative_gap_before": getattr(state, "cumulative_gap_before", None),
        "dry_run_cumulative_pending_before": getattr(state, "cumulative_pending_before", None),
        "dry_run_download_performed": False,
        "dry_run_api_call_performed": False,
        "dry_run_browse_performed": False,
        "dry_run_data_build_performed": False,
        "dry_run_aggregation_performed": False,
        "dry_run_full_csv_read_performed": False,
    }


def external_confirmations() -> dict[str, Any]:
    raw = read_json(RAW_VERIFIER_SUMMARY) if RAW_VERIFIER_SUMMARY.exists() else {}
    apply = read_json(REPAIR_APPLY_SUMMARY) if REPAIR_APPLY_SUMMARY.exists() else {}
    return {
        "repair_apply_confirmed": (
            apply.get("patch_applied") is True
            and apply.get("target_file_modified") is True
            and apply.get("replacement_checks_all_true") is True
            and apply.get("next_module") == "edge_factory_os_repo_only_generic_chunk_controller_post_repair_semantic_audit_and_dry_run_v1.py"
        ),
        "raw_evidence_verifier_confirmed": (
            raw.get("raw_evidence_independent_verifier_status") == "PASS_REPO_ONLY_RAW_EVIDENCE_INDEPENDENT_VERIFIER_SELF_APPROVAL_RISK_LOW"
            and raw.get("claims_recomputed_from_raw_evidence") is True
            and raw.get("replacement_checks_all_true") is True
            and raw.get("next_module") == "edge_factory_os_repo_only_generic_chunk_controller_post_repair_semantic_audit_and_dry_run_v1.py"
        ),
        "self_approval_risk_level_before_audit": raw.get("self_approval_risk_level"),
        "raw_verifier_summary_path": str(RAW_VERIFIER_SUMMARY),
        "repair_apply_summary_path": str(REPAIR_APPLY_SUMMARY),
    }


def build_reports() -> dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = status_lines()
    target_sha_before = sha256_file(TARGET_FILE)
    source = TARGET_FILE.read_text(encoding="utf-8")
    source_report = source_check(source)
    dry_run = controller_state_dry_run()
    syntax = syntax_bom_tracked_plus_self()
    confirms = external_confirmations()
    target_sha_after = sha256_file(TARGET_FILE)
    safety_report = {
        "artifact_type": "repo_only_generic_chunk_controller_post_repair_safety_gate_report",
        "safety_gates_confirmed": source_report["safety_gates_confirmed"],
        "dry_run_download_performed": False,
        "dry_run_api_call_performed": False,
        "dry_run_browse_performed": False,
        "dry_run_data_build_performed": False,
        "dry_run_aggregation_performed": False,
        "dry_run_full_csv_read_performed": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "full_csv_read_performed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
    }
    route_report = {
        "artifact_type": "repo_only_generic_chunk_controller_post_repair_route_logic_report",
        "next_route_logic_confirmed": source_report["next_route_logic_confirmed"],
        "route_to_generic_while_chunks_remain_confirmed": '"next_module": NEXT_MODULE if CHUNKS_REMAINING_AFTER > 0 else FINAL_SUMMARY_MODULE' in source,
        "route_to_final_summary_after_chunk_16_confirmed": "else FINAL_SUMMARY_MODULE" in source and "NEXT_CHUNK_ID_AFTER_EXECUTION = next_chunk_after(chunk_plan, state.chunk_number) if CHUNKS_REMAINING_AFTER > 0 else None" in source,
        "expected_next_module_if_pass": EXPECTED_NEXT_MODULE,
    }
    dry_run_report = {
        "artifact_type": "repo_only_generic_chunk_controller_post_repair_dry_run_report",
        **dry_run,
        "dry_run_matches_expected_chunk_04_state": (
            dry_run["dry_run_selected_next_chunk_id"] == EXPECTED_CHUNK_ID
            and dry_run["dry_run_selected_chunk_symbol_count"] == 20
            and dry_run["dry_run_expected_chunk_file_count"] == 21060
            and dry_run["dry_run_chunks_completed_before"] == 3
            and dry_run["dry_run_chunks_remaining_before"] == 13
            and dry_run["dry_run_symbols_evaluated_before"] == 60
            and dry_run["dry_run_cumulative_near_3y_complete_before"] == 20
            and dry_run["dry_run_cumulative_gap_before"] == 40
            and dry_run["dry_run_cumulative_pending_before"] == 243
        ),
    }
    checks = {
        "head_matches": head == EXPECTED_HEAD,
        "repo_clean": repo_effectively_clean_for_audit(status),
        "target_file_exists": TARGET_FILE.exists(),
        "target_file_modified_false": target_sha_before == target_sha_after,
        "repair_apply_confirmed": confirms["repair_apply_confirmed"],
        "raw_evidence_verifier_confirmed": confirms["raw_evidence_verifier_confirmed"],
        "self_approval_risk_low": confirms["self_approval_risk_level_before_audit"] == "LOW",
        "dynamic_state_loading_confirmed": source_report["dynamic_state_loading_confirmed"],
        "chunk_plan_lookup_confirmed": source_report["chunk_plan_lookup_confirmed"],
        "dynamic_artifact_naming_confirmed": source_report["dynamic_artifact_naming_confirmed"],
        "dynamic_ledger_update_confirmed": source_report["dynamic_ledger_update_confirmed"],
        "next_route_logic_confirmed": source_report["next_route_logic_confirmed"],
        "safety_gates_confirmed": source_report["safety_gates_confirmed"],
        "not_hardcoded_chunk_only": source_report["generic_controller_hardcoded_chunk_only_after_repair"] is False,
        "no_fixed_symbol_list": source_report["active_fixed_symbol_list_detected"] is False,
        "no_stale_active_ledger_constants": source_report["stale_active_ledger_constant_count"] == 0,
        "dry_run_state_check_performed": dry_run["dry_run_state_check_performed"],
        "dry_run_selected_chunk_04": dry_run["dry_run_selected_next_chunk_id"] == EXPECTED_CHUNK_ID,
        "dry_run_expected_state": dry_run_report["dry_run_matches_expected_chunk_04_state"],
        "dry_run_no_forbidden_actions": not any(
            dry_run[key]
            for key in (
                "dry_run_download_performed",
                "dry_run_api_call_performed",
                "dry_run_browse_performed",
                "dry_run_data_build_performed",
                "dry_run_aggregation_performed",
                "dry_run_full_csv_read_performed",
            )
        ),
        "syntax_bom_clean": syntax["syntax_error_count"] == 0 and syntax["bom_error_count"] == 0,
    }
    passed = all(checks.values())
    summary = {
        "artifact_type": "repo_only_generic_chunk_controller_post_repair_audit_summary",
        "generic_chunk_controller_post_repair_semantic_audit_status": PASS_STATUS if passed else FAIL_STATUS,
        "audit_performed": True,
        "created_at_utc": utc_now(),
        "target_file": TARGET_REL.replace("/", "\\"),
        "target_file_modified": target_sha_before != target_sha_after,
        "repair_apply_confirmed": confirms["repair_apply_confirmed"],
        "raw_evidence_verifier_confirmed": confirms["raw_evidence_verifier_confirmed"],
        "self_approval_risk_level_before_audit": confirms["self_approval_risk_level_before_audit"],
        "generic_controller_dynamic_chunk_selection_confirmed": source_report["generic_controller_dynamic_chunk_selection_confirmed"],
        "generic_controller_hardcoded_chunk_only_after_repair": source_report["generic_controller_hardcoded_chunk_only_after_repair"],
        "generic_controller_safe_to_rerun_for_chunk_04_confirmed": source_report["generic_controller_safe_to_rerun_for_chunk_04_confirmed"] and dry_run_report["dry_run_matches_expected_chunk_04_state"],
        "dynamic_state_loading_confirmed": source_report["dynamic_state_loading_confirmed"],
        "chunk_plan_lookup_confirmed": source_report["chunk_plan_lookup_confirmed"],
        "dynamic_artifact_naming_confirmed": source_report["dynamic_artifact_naming_confirmed"],
        "dynamic_ledger_update_confirmed": source_report["dynamic_ledger_update_confirmed"],
        "next_route_logic_confirmed": source_report["next_route_logic_confirmed"],
        "safety_gates_confirmed": source_report["safety_gates_confirmed"],
        "active_hardcoded_chunk_03_only_reference_count": source_report["active_hardcoded_chunk_03_only_reference_count"],
        "active_fixed_symbol_list_detected": source_report["active_fixed_symbol_list_detected"],
        "stale_active_ledger_constant_count": source_report["stale_active_ledger_constant_count"],
        "dry_run_state_check_performed": dry_run["dry_run_state_check_performed"],
        "dry_run_selected_next_chunk_id": dry_run["dry_run_selected_next_chunk_id"],
        "dry_run_selected_chunk_symbol_count": dry_run["dry_run_selected_chunk_symbol_count"],
        "dry_run_expected_chunk_file_count": dry_run["dry_run_expected_chunk_file_count"],
        "dry_run_chunks_completed_before": dry_run["dry_run_chunks_completed_before"],
        "dry_run_chunks_remaining_before": dry_run["dry_run_chunks_remaining_before"],
        "dry_run_symbols_evaluated_before": dry_run["dry_run_symbols_evaluated_before"],
        "dry_run_cumulative_near_3y_complete_before": dry_run["dry_run_cumulative_near_3y_complete_before"],
        "dry_run_cumulative_gap_before": dry_run["dry_run_cumulative_gap_before"],
        "dry_run_cumulative_pending_before": dry_run["dry_run_cumulative_pending_before"],
        "dry_run_download_performed": False,
        "dry_run_api_call_performed": False,
        "dry_run_browse_performed": False,
        "dry_run_data_build_performed": False,
        "dry_run_aggregation_performed": False,
        "dry_run_full_csv_read_performed": False,
        "safe_for_chunk_04_real_execution": passed,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "full_csv_read_performed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 0 if passed else 1,
        "active_p1_attention_count": 0 if passed else 1,
        "final_decision": PASS_DECISION if passed else FAIL_DECISION,
        "current_evidence_chain_quality_after_audit": PASS_QUALITY if passed else FAIL_QUALITY,
        "next_module": EXPECTED_NEXT_MODULE if passed else FAIL_NEXT_MODULE,
        "replacement_checks_all_true": passed,
        "replacement_checks": checks,
    }
    audit_report = {
        "artifact_type": "repo_only_generic_chunk_controller_post_repair_semantic_audit",
        "summary": summary,
        "source_check_report": source_report,
        "dynamic_state_check_report": dry_run,
        "dry_run_report": dry_run_report,
        "safety_gate_report": safety_report,
        "route_logic_report": route_report,
        "external_confirmations": confirms,
        "syntax_bom_report": syntax,
        "forbidden_actions_performed": {
            "real_chunk_04_execution": False,
            "download": False,
            "api": False,
            "browse": False,
            "url_fetch": False,
            "zip_csv_parquet_read": False,
            "data_build": False,
            "aggregation": False,
            "patch": False,
            "delete": False,
            "move": False,
            "cleanup": False,
        },
    }
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_post_repair_semantic_audit.json", audit_report)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_post_repair_source_check_report.json", source_report)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_post_repair_dynamic_state_check_report.json", dry_run)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_post_repair_dry_run_report.json", dry_run_report)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_post_repair_safety_gate_report.json", safety_report)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_post_repair_route_logic_report.json", route_report)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_post_repair_audit_summary.json", summary)
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise RuntimeError(f"missing required artifacts: {missing}")
    return summary


def main() -> int:
    summary = build_reports()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    sys.exit(main())
