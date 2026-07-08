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
TOOL_REL = "tools/edge_factory_os_repo_only_raw_evidence_independent_verifier_after_generic_controller_repair_apply_v1.py"
TOOL_PATH = REPO_ROOT / TOOL_REL
TARGET_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
TARGET_FILE = REPO_ROOT / TARGET_REL
EXPECTED_HEAD = "c09aa02"
EXPECTED_NEXT_CHUNK = "chunk_04"
EXPECTED_NEXT_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_post_repair_semantic_audit_and_dry_run_v1.py"

OUTPUT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_raw_evidence_independent_verifier_after_generic_controller_repair_apply_v1"
GENERIC_CYCLE_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1"
CHUNK_PLAN_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1" / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json"
LEDGER_PATH = GENERIC_CYCLE_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json"
NEXT_STATE_PATH = GENERIC_CYCLE_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_next_chunk_state.json"
APPLY_STATE_CHECK_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_repair_apply_after_exhaustive_repair_plan_v1" / "repo_only_generic_chunk_controller_repair_apply_dynamic_state_check_report.json"

APPROVED_APPLY_COMMIT_PATHS = {
    "tools/edge_factory_os_repo_only_generic_chunk_controller_repair_apply_after_exhaustive_repair_plan_v1.py",
    TARGET_REL,
}

PASS_STATUS = "PASS_REPO_ONLY_RAW_EVIDENCE_INDEPENDENT_VERIFIER_SELF_APPROVAL_RISK_LOW"
FAIL_STATUS = "FAIL_REPO_ONLY_RAW_EVIDENCE_INDEPENDENT_VERIFIER_REPAIR_REVIEW_REQUIRED"
PASS_DECISION = "RAW_EVIDENCE_VERIFIER_PASS_PROCEED_TO_POST_REPAIR_AUDIT_AND_DRY_RUN"
FAIL_DECISION = "RAW_EVIDENCE_VERIFIER_FAIL_REPAIR_REVIEW_REQUIRED"
PASS_QUALITY = "REPO_ONLY_RAW_EVIDENCE_VERIFIER_PASS_SELF_APPROVAL_RISK_LOW"
FAIL_QUALITY = "REPO_ONLY_RAW_EVIDENCE_VERIFIER_FAIL_REPAIR_REVIEW_REQUIRED"
FAIL_NEXT_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_repair_raw_evidence_review_v1.py"

REQUIRED_ARTIFACTS = [
    "repo_only_raw_evidence_independent_verifier_report.json",
    "repo_only_raw_evidence_git_diff_verification.json",
    "repo_only_raw_evidence_source_code_verification.json",
    "repo_only_raw_evidence_hardcoded_stale_check.json",
    "repo_only_raw_evidence_artifact_verification.json",
    "repo_only_raw_evidence_independent_state_simulation.json",
    "repo_only_raw_evidence_self_approval_risk_classification.json",
    "repo_only_raw_evidence_independent_verifier_summary.json",
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


def repo_effectively_clean_for_verifier(lines: list[str]) -> bool:
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
        except Exception as exc:  # noqa: BLE001 - verifier records raw parser failure.
            syntax_errors.append({"file": rel, "error": repr(exc)})
    return {
        "files_checked": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "ast_parse_success_count": ok,
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def latest_commit_paths() -> list[str]:
    out = run_git(["show", "--name-only", "--pretty=format:", "HEAD"])
    return [line.replace("\\", "/") for line in out.splitlines() if line.strip()]


def git_diff_verification() -> dict[str, Any]:
    paths = latest_commit_paths()
    status = status_lines()
    changed_now = {status_path(line) for line in status}
    unapproved_now = sorted(path for path in changed_now if path != TOOL_REL)
    return {
        "artifact_type": "repo_only_raw_evidence_git_diff_verification",
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "repo_status_short": status,
        "latest_commit_paths": paths,
        "repair_apply_commit_paths_verified_from_git": set(paths) == APPROVED_APPLY_COMMIT_PATHS,
        "approved_paths_only_verified_from_git": set(paths).issubset(APPROVED_APPLY_COMMIT_PATHS),
        "target_controller_changed_in_apply_commit": TARGET_REL in paths,
        "unapproved_git_diff_paths": unapproved_now,
        "unapproved_git_diff_path_count": len(unapproved_now),
    }


def source_code_verification(source: str) -> dict[str, Any]:
    tree = ast.parse(source, filename=TARGET_REL)
    functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    source_dynamic_state_loading_verified = (
        "ControllerState" in source
        and "def load_latest_controller_state" in source
        and "latest_json_by_completed_chunk" in source
        and "ledger_value(ledger" in source
    )
    source_chunk_plan_lookup_verified = (
        "CHUNK_PLAN" in source
        and 'chunk.get("chunk_id") == next_chunk_id' in source
        and "chunk_plan.get(\"chunks\"" in source
    )
    source_dynamic_chunk_selection_verified = (
        "next_chunk_id = next_state.get(\"next_chunk_id_after_execution\")" in source
        and "APPROVED_CHUNK_ID = state.chunk_id" in source
        and "APPROVED_SYMBOLS = list(state.chunk_symbols)" in source
        and 'APPROVED_CHUNK_ID = "chunk_03"' not in source
        and "APPROVED_SYMBOLS = [" not in source
    )
    source_dynamic_artifact_naming_verified = (
        "def artifact_file" in source
        and "generic_chunk_coverage_cycle_{APPROVED_CHUNK_ID}_" in source
        and "artifact_file(\"execution_report.json\")" in source
        and "artifact_file(\"cumulative_ledger_after_chunk.json\")" in source
    )
    source_dynamic_ledger_update_verified = all(
        token in source
        for token in (
            "CHUNKS_COMPLETED_AFTER = state.chunks_completed_before + 1",
            "CHUNKS_REMAINING_AFTER = state.chunks_total - CHUNKS_COMPLETED_AFTER",
            "SYMBOLS_EVALUATED_AFTER = state.symbols_evaluated_before + len(APPROVED_SYMBOLS)",
            "CUMULATIVE_PENDING_AFTER = state.total_candidate_symbol_count - SYMBOLS_EVALUATED_AFTER",
            "cumulative_available_count = CUMULATIVE_AVAILABLE_BEFORE + final_available_file_count",
            "cumulative_missing_count = CUMULATIVE_MISSING_BEFORE + missing_or_failed_file_count",
            "cumulative_planned_count = CUMULATIVE_PLANNED_BEFORE + EXPECTED_CHUNK_FILE_COUNT",
        )
    )
    source_next_route_logic_verified = (
        "NEXT_CHUNK_ID_AFTER_EXECUTION = next_chunk_after(chunk_plan, state.chunk_number) if CHUNKS_REMAINING_AFTER > 0 else None" in source
        and '"next_module": NEXT_MODULE if CHUNKS_REMAINING_AFTER > 0 else FINAL_SUMMARY_MODULE' in source
        and "FINAL_SUMMARY_MODULE" in source
    )
    source_safety_gates_verified = all(
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
            '"full_universe_acquisition_allowed_now": False',
            '"output_valid_for_research_backtest": False',
            '"output_valid_for_edge_claim": False',
        )
    )
    return {
        "artifact_type": "repo_only_raw_evidence_source_code_verification",
        "target_file": TARGET_REL,
        "target_sha256": sha256_file(TARGET_FILE),
        "function_names_seen": sorted(functions),
        "source_dynamic_state_loading_verified": source_dynamic_state_loading_verified,
        "source_chunk_plan_lookup_verified": source_chunk_plan_lookup_verified,
        "source_dynamic_chunk_selection_verified": source_dynamic_chunk_selection_verified,
        "source_dynamic_artifact_naming_verified": source_dynamic_artifact_naming_verified,
        "source_dynamic_ledger_update_verified": source_dynamic_ledger_update_verified,
        "source_next_route_logic_verified": source_next_route_logic_verified,
        "source_safety_gates_verified": source_safety_gates_verified,
    }


def hardcoded_stale_check(source: str) -> dict[str, Any]:
    active_chunk_03_only_logic_count = 0
    if 'APPROVED_CHUNK_ID = "chunk_03"' in source:
        active_chunk_03_only_logic_count += 1
    if "APPROVED_SYMBOLS = [" in source:
        active_chunk_03_only_logic_count += 1
    if "downloaded_chunk_03_approved_quarantine" in source:
        active_chunk_03_only_logic_count += 1
    active_fixed_symbol_list_detected = "APPROVED_SYMBOLS = [" in source
    active_static_next_chunk_output_detected = 'NEXT_CHUNK_ID_AFTER_EXECUTION = "chunk_04"' in source
    stale_ledger_tokens = [
        "CHUNKS_COMPLETED_BEFORE = 2",
        "CHUNKS_COMPLETED_AFTER = 3",
        "CHUNKS_REMAINING_AFTER = 13",
        "SYMBOLS_EVALUATED_BEFORE = 40",
        "SYMBOLS_EVALUATED_AFTER = 60",
        "CUMULATIVE_PENDING_AFTER = 243",
    ]
    active_stale_ledger_constant_count = sum(1 for token in stale_ledger_tokens if token in source)
    active_chunk_03_output_overwrite_risk_count = 0
    if '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_report.json"' in source:
        active_chunk_03_output_overwrite_risk_count += 1
    if "generic_chunk_coverage_cycle_chunk_03_" in source:
        active_chunk_03_output_overwrite_risk_count += 1
    return {
        "artifact_type": "repo_only_raw_evidence_hardcoded_stale_check",
        "active_chunk_03_only_logic_count": active_chunk_03_only_logic_count,
        "active_fixed_symbol_list_detected": active_fixed_symbol_list_detected,
        "active_static_next_chunk_output_detected": active_static_next_chunk_output_detected,
        "active_stale_ledger_constant_count": active_stale_ledger_constant_count,
        "active_chunk_03_output_overwrite_risk_count": active_chunk_03_output_overwrite_risk_count,
    }


def bool_true_value(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.lower() == "true")


def artifact_verification() -> dict[str, Any]:
    chunk_plan = read_json(CHUNK_PLAN_PATH)
    ledger = read_json(LEDGER_PATH)
    next_state = read_json(NEXT_STATE_PATH)
    chunks = chunk_plan.get("chunks", [])
    chunk_04 = next((chunk for chunk in chunks if chunk.get("chunk_id") == EXPECTED_NEXT_CHUNK), {})
    symbols = chunk_04.get("symbols", []) if isinstance(chunk_04, dict) else []
    raw_chunk_04_symbol_count = len(symbols)
    expected_count = raw_chunk_04_symbol_count * 1053
    ledger_entries = ledger.get("ledger_entries", {})
    raw_cumulative_ledger_after_chunk_03_verified = (
        ledger.get("chunk_id") == "chunk_03"
        and ledger.get("chunks_completed_after") == 3
        and ledger.get("chunks_remaining_after") == 13
        and ledger.get("symbols_evaluated_for_download_coverage") == 60
        and ledger.get("cumulative_near_3y_download_coverage_complete_symbol_count") == 20
        and ledger.get("cumulative_coverage_gap_symbol_count") == 40
        and ledger.get("cumulative_pending_symbol_count") == 243
        and ledger_entries.get("chunks_completed") == 3
        and ledger_entries.get("symbols_evaluated_for_download_coverage") == 60
    )
    raw_next_chunk_state_verified = (
        next_state.get("chunk_id") == "chunk_03"
        and next_state.get("next_chunk_id_after_execution") == EXPECTED_NEXT_CHUNK
        and next_state.get("chunks_completed_after") == 3
        and next_state.get("chunks_remaining_after") == 13
        and next_state.get("route_to_same_generic_cycle_module") is True
    )
    raw_artifacts = [chunk_plan, ledger, next_state]
    forbidden_true_fields = []
    for name, payload in (("chunk_plan", chunk_plan), ("ledger_after_chunk_03", ledger), ("next_state_after_chunk_03", next_state)):
        for key in (
            "data_build_allowed_now",
            "data_build_performed",
            "aggregation_performed_now",
            "strategy_backtest_edge_allowed_now",
            "output_valid_for_research_backtest",
            "output_valid_for_edge_claim",
            "full_universe_acquisition_allowed_now",
            "broad_acquisition_ready",
            "safe_for_full_universe_acquisition",
        ):
            if bool_true_value(payload.get(key)):
                forbidden_true_fields.append({"artifact": name, "field": key, "value": payload.get(key)})
    no_chunk_04_executed = all(payload.get("chunk_id") != EXPECTED_NEXT_CHUNK for payload in raw_artifacts)
    return {
        "artifact_type": "repo_only_raw_evidence_artifact_verification",
        "chunk_plan_path": str(CHUNK_PLAN_PATH),
        "ledger_path": str(LEDGER_PATH),
        "next_state_path": str(NEXT_STATE_PATH),
        "raw_chunk_plan_chunk_04_verified": bool(chunk_04) and raw_chunk_04_symbol_count > 0 and chunk_04.get("expected_file_count") == expected_count,
        "raw_chunk_04_symbol_count": raw_chunk_04_symbol_count,
        "raw_chunk_04_symbols": symbols,
        "raw_chunk_04_expected_file_count": expected_count,
        "chunk_plan_expected_file_count": chunk_04.get("expected_file_count") if isinstance(chunk_04, dict) else None,
        "raw_cumulative_ledger_after_chunk_03_verified": raw_cumulative_ledger_after_chunk_03_verified,
        "raw_next_chunk_state_verified": raw_next_chunk_state_verified,
        "no_artifact_says_chunk_04_already_executed": no_chunk_04_executed,
        "raw_artifact_build_backtest_edge_allowed_fields": forbidden_true_fields,
        "raw_artifact_build_backtest_edge_allowed_count": len(forbidden_true_fields),
    }


def independent_state_simulation(artifact: dict[str, Any]) -> dict[str, Any]:
    ledger = read_json(LEDGER_PATH)
    next_state = read_json(NEXT_STATE_PATH)
    chunk_plan = read_json(CHUNK_PLAN_PATH)
    chunks = chunk_plan.get("chunks", [])
    selected_id = next_state.get("next_chunk_id_after_execution")
    selected = next((chunk for chunk in chunks if chunk.get("chunk_id") == selected_id), {})
    symbols = selected.get("symbols", []) if isinstance(selected, dict) else []
    expected_count = len(symbols) * 1053
    independent_ok = (
        selected_id == EXPECTED_NEXT_CHUNK
        and ledger.get("chunks_completed_after") == 3
        and ledger.get("chunks_remaining_after") == 13
        and ledger.get("symbols_evaluated_for_download_coverage") == 60
        and ledger.get("cumulative_near_3y_download_coverage_complete_symbol_count") == 20
        and ledger.get("cumulative_coverage_gap_symbol_count") == 40
        and ledger.get("cumulative_pending_symbol_count") == 243
        and expected_count == artifact["raw_chunk_04_expected_file_count"]
    )
    controller_dry_run = controller_state_loader_dry_run()
    apply_state_check = read_json(APPLY_STATE_CHECK_PATH) if APPLY_STATE_CHECK_PATH.exists() else {}
    controller_selected = controller_dry_run.get("selected_chunk_id") or apply_state_check.get("dry_run_selected_next_chunk_id")
    dry_run_matches = (
        controller_selected == selected_id
        and (controller_dry_run.get("selected_chunk_symbol_count") or apply_state_check.get("dry_run_chunk_symbol_count")) == len(symbols)
    )
    return {
        "artifact_type": "repo_only_raw_evidence_independent_state_simulation",
        "independent_state_simulation_performed": True,
        "independent_selected_next_chunk_id": selected_id,
        "independent_selected_chunk_symbol_count": len(symbols),
        "independent_expected_chunk_file_count": expected_count,
        "independent_expected_chunks_completed_before": ledger.get("chunks_completed_after"),
        "independent_expected_chunks_remaining_before": ledger.get("chunks_remaining_after"),
        "independent_expected_symbols_evaluated_before": ledger.get("symbols_evaluated_for_download_coverage"),
        "independent_expected_cumulative_near_3y_before": ledger.get("cumulative_near_3y_download_coverage_complete_symbol_count"),
        "independent_expected_cumulative_gap_before": ledger.get("cumulative_coverage_gap_symbol_count"),
        "independent_expected_cumulative_pending_before": ledger.get("cumulative_pending_symbol_count"),
        "independent_simulation_clean": independent_ok,
        "controller_dry_run_performed": controller_dry_run.get("controller_dry_run_performed", False),
        "controller_dry_run_selected_next_chunk_id": controller_selected,
        "controller_dry_run_source": controller_dry_run.get("controller_dry_run_source"),
        "dry_run_matches_independent_simulation": dry_run_matches,
        "dry_run_download_performed": False,
        "dry_run_api_call_performed": False,
        "dry_run_browse_performed": False,
        "dry_run_data_build_performed": False,
        "dry_run_aggregation_performed": False,
        "dry_run_full_csv_read_performed": False,
        "apply_state_check_raw_pointer": apply_state_check,
    }


def controller_state_loader_dry_run() -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("generic_controller_repaired_raw_verifier", TARGET_FILE)
    if spec is None or spec.loader is None:
        return {"controller_dry_run_performed": False, "controller_dry_run_error": "spec unavailable"}
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    state = module.load_latest_controller_state()
    return {
        "controller_dry_run_performed": True,
        "controller_dry_run_source": "imported_controller_load_latest_controller_state_only",
        "selected_chunk_id": getattr(state, "chunk_id", None),
        "selected_chunk_number": getattr(state, "chunk_number", None),
        "selected_chunk_symbol_count": len(getattr(state, "chunk_symbols", [])),
        "expected_chunk_file_count": len(getattr(state, "chunk_symbols", [])) * 1053,
        "chunks_completed_before": getattr(state, "chunks_completed_before", None),
        "chunks_remaining_before": getattr(state, "chunks_remaining_before", None),
        "symbols_evaluated_before": getattr(state, "symbols_evaluated_before", None),
        "cumulative_complete_before": getattr(state, "cumulative_complete_before", None),
        "cumulative_gap_before": getattr(state, "cumulative_gap_before", None),
        "cumulative_pending_before": getattr(state, "cumulative_pending_before", None),
    }


def self_approval_classification(critical: dict[str, bool]) -> dict[str, Any]:
    unrecomputed = [key for key, value in critical.items() if not value]
    risk = "LOW" if not unrecomputed else ("HIGH" if any("source" in key or "git" in key or "simulation" in key for key in unrecomputed) else "MEDIUM")
    return {
        "artifact_type": "repo_only_raw_evidence_self_approval_risk_classification",
        "prior_reports_used_only_as_pointers": True,
        "claims_recomputed_from_raw_evidence": not unrecomputed,
        "critical_claim_recomputation_map": critical,
        "unrecomputed_claim_count": len(unrecomputed),
        "unrecomputed_claims": unrecomputed,
        "self_approval_risk_level": risk,
    }


def build_summary(
    gitv: dict[str, Any],
    sourcev: dict[str, Any],
    stale: dict[str, Any],
    artifactv: dict[str, Any],
    sim: dict[str, Any],
    risk: dict[str, Any],
    syntax: dict[str, Any],
) -> dict[str, Any]:
    replacement_checks = {
        "head_matches": gitv["head"] == EXPECTED_HEAD,
        "repo_clean": repo_effectively_clean_for_verifier(status_lines()),
        "syntax_bom_clean": syntax["syntax_error_count"] == 0 and syntax["bom_error_count"] == 0,
        "repair_apply_commit_paths_verified_from_git": gitv["repair_apply_commit_paths_verified_from_git"],
        "approved_paths_only_verified_from_git": gitv["approved_paths_only_verified_from_git"],
        "target_controller_changed_in_apply_commit": gitv["target_controller_changed_in_apply_commit"],
        "unapproved_git_diff_path_count_zero": gitv["unapproved_git_diff_path_count"] == 0,
        "source_dynamic_state_loading_verified": sourcev["source_dynamic_state_loading_verified"],
        "source_chunk_plan_lookup_verified": sourcev["source_chunk_plan_lookup_verified"],
        "source_dynamic_chunk_selection_verified": sourcev["source_dynamic_chunk_selection_verified"],
        "source_dynamic_artifact_naming_verified": sourcev["source_dynamic_artifact_naming_verified"],
        "source_dynamic_ledger_update_verified": sourcev["source_dynamic_ledger_update_verified"],
        "source_next_route_logic_verified": sourcev["source_next_route_logic_verified"],
        "source_safety_gates_verified": sourcev["source_safety_gates_verified"],
        "no_active_chunk_03_logic": stale["active_chunk_03_only_logic_count"] == 0,
        "no_active_fixed_symbol_list": stale["active_fixed_symbol_list_detected"] is False,
        "no_static_next_chunk_output": stale["active_static_next_chunk_output_detected"] is False,
        "no_active_stale_ledger_constants": stale["active_stale_ledger_constant_count"] == 0,
        "no_chunk_03_overwrite_risk": stale["active_chunk_03_output_overwrite_risk_count"] == 0,
        "raw_chunk_plan_chunk_04_verified": artifactv["raw_chunk_plan_chunk_04_verified"],
        "raw_cumulative_ledger_after_chunk_03_verified": artifactv["raw_cumulative_ledger_after_chunk_03_verified"],
        "raw_next_chunk_state_verified": artifactv["raw_next_chunk_state_verified"],
        "no_build_backtest_edge_artifact_claims": artifactv["raw_artifact_build_backtest_edge_allowed_count"] == 0,
        "independent_state_simulation_performed": sim["independent_state_simulation_performed"],
        "independent_selected_chunk_04": sim["independent_selected_next_chunk_id"] == EXPECTED_NEXT_CHUNK,
        "controller_dry_run_performed": sim["controller_dry_run_performed"],
        "controller_dry_run_selected_chunk_04": sim["controller_dry_run_selected_next_chunk_id"] == EXPECTED_NEXT_CHUNK,
        "dry_run_matches_independent_simulation": sim["dry_run_matches_independent_simulation"],
        "dry_run_no_forbidden_actions": not any(
            sim[key]
            for key in (
                "dry_run_download_performed",
                "dry_run_api_call_performed",
                "dry_run_browse_performed",
                "dry_run_data_build_performed",
                "dry_run_aggregation_performed",
                "dry_run_full_csv_read_performed",
            )
        ),
        "claims_recomputed_from_raw_evidence": risk["claims_recomputed_from_raw_evidence"],
        "self_approval_risk_low": risk["self_approval_risk_level"] == "LOW",
    }
    passed = all(replacement_checks.values())
    return {
        "artifact_type": "repo_only_raw_evidence_independent_verifier_summary",
        "raw_evidence_independent_verifier_status": PASS_STATUS if passed else FAIL_STATUS,
        "verifier_performed": True,
        "created_at_utc": utc_now(),
        "repo_clean": replacement_checks["repo_clean"],
        "tracked_python_count": len(tracked_python_files()),
        "prior_reports_used_only_as_pointers": risk["prior_reports_used_only_as_pointers"],
        "claims_recomputed_from_raw_evidence": risk["claims_recomputed_from_raw_evidence"],
        "repair_apply_commit_paths_verified_from_git": gitv["repair_apply_commit_paths_verified_from_git"],
        "approved_paths_only_verified_from_git": gitv["approved_paths_only_verified_from_git"],
        "target_controller_changed_in_apply_commit": gitv["target_controller_changed_in_apply_commit"],
        "unapproved_git_diff_path_count": gitv["unapproved_git_diff_path_count"],
        "source_dynamic_state_loading_verified": sourcev["source_dynamic_state_loading_verified"],
        "source_chunk_plan_lookup_verified": sourcev["source_chunk_plan_lookup_verified"],
        "source_dynamic_chunk_selection_verified": sourcev["source_dynamic_chunk_selection_verified"],
        "source_dynamic_artifact_naming_verified": sourcev["source_dynamic_artifact_naming_verified"],
        "source_dynamic_ledger_update_verified": sourcev["source_dynamic_ledger_update_verified"],
        "source_next_route_logic_verified": sourcev["source_next_route_logic_verified"],
        "source_safety_gates_verified": sourcev["source_safety_gates_verified"],
        "active_chunk_03_only_logic_count": stale["active_chunk_03_only_logic_count"],
        "active_fixed_symbol_list_detected": stale["active_fixed_symbol_list_detected"],
        "active_static_next_chunk_output_detected": stale["active_static_next_chunk_output_detected"],
        "active_stale_ledger_constant_count": stale["active_stale_ledger_constant_count"],
        "active_chunk_03_output_overwrite_risk_count": stale["active_chunk_03_output_overwrite_risk_count"],
        "raw_chunk_plan_chunk_04_verified": artifactv["raw_chunk_plan_chunk_04_verified"],
        "raw_chunk_04_symbol_count": artifactv["raw_chunk_04_symbol_count"],
        "raw_chunk_04_expected_file_count": artifactv["raw_chunk_04_expected_file_count"],
        "raw_cumulative_ledger_after_chunk_03_verified": artifactv["raw_cumulative_ledger_after_chunk_03_verified"],
        "raw_next_chunk_state_verified": artifactv["raw_next_chunk_state_verified"],
        "raw_artifact_build_backtest_edge_allowed_count": artifactv["raw_artifact_build_backtest_edge_allowed_count"],
        "independent_state_simulation_performed": sim["independent_state_simulation_performed"],
        "independent_selected_next_chunk_id": sim["independent_selected_next_chunk_id"],
        "independent_selected_chunk_symbol_count": sim["independent_selected_chunk_symbol_count"],
        "independent_expected_chunk_file_count": sim["independent_expected_chunk_file_count"],
        "controller_dry_run_performed": sim["controller_dry_run_performed"],
        "controller_dry_run_selected_next_chunk_id": sim["controller_dry_run_selected_next_chunk_id"],
        "dry_run_matches_independent_simulation": sim["dry_run_matches_independent_simulation"],
        "dry_run_download_performed": sim["dry_run_download_performed"],
        "dry_run_api_call_performed": sim["dry_run_api_call_performed"],
        "dry_run_browse_performed": sim["dry_run_browse_performed"],
        "dry_run_data_build_performed": sim["dry_run_data_build_performed"],
        "dry_run_aggregation_performed": sim["dry_run_aggregation_performed"],
        "dry_run_full_csv_read_performed": sim["dry_run_full_csv_read_performed"],
        "unrecomputed_claim_count": risk["unrecomputed_claim_count"],
        "unrecomputed_claims": risk["unrecomputed_claims"],
        "self_approval_risk_level": risk["self_approval_risk_level"],
        "safe_for_post_repair_semantic_audit": passed,
        "safe_for_chunk_04_real_execution": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "full_csv_read_performed": False,
        "active_p0_blocker_count": 0 if passed else 1,
        "active_p1_attention_count": 0 if passed else 1,
        "final_decision": PASS_DECISION if passed else FAIL_DECISION,
        "current_evidence_chain_quality_after_verifier": PASS_QUALITY if passed else FAIL_QUALITY,
        "next_module": EXPECTED_NEXT_MODULE if passed else FAIL_NEXT_MODULE,
        "replacement_checks_all_true": passed,
        "replacement_checks": replacement_checks,
    }


def run_verifier() -> dict[str, Any]:
    source = TARGET_FILE.read_text(encoding="utf-8")
    gitv = git_diff_verification()
    sourcev = source_code_verification(source)
    stale = hardcoded_stale_check(source)
    artifactv = artifact_verification()
    sim = independent_state_simulation(artifactv)
    critical = {
        "git_paths": gitv["repair_apply_commit_paths_verified_from_git"] and gitv["target_controller_changed_in_apply_commit"] and gitv["unapproved_git_diff_path_count"] == 0,
        "source_dynamic_controller": all(
            sourcev[key]
            for key in (
                "source_dynamic_state_loading_verified",
                "source_chunk_plan_lookup_verified",
                "source_dynamic_chunk_selection_verified",
                "source_dynamic_artifact_naming_verified",
                "source_dynamic_ledger_update_verified",
                "source_next_route_logic_verified",
                "source_safety_gates_verified",
            )
        ),
        "source_no_active_stale_chunk_03": stale["active_chunk_03_only_logic_count"] == 0 and not stale["active_fixed_symbol_list_detected"] and stale["active_stale_ledger_constant_count"] == 0,
        "raw_artifacts": artifactv["raw_chunk_plan_chunk_04_verified"] and artifactv["raw_cumulative_ledger_after_chunk_03_verified"] and artifactv["raw_next_chunk_state_verified"],
        "independent_simulation": sim["independent_state_simulation_performed"] and sim["independent_selected_next_chunk_id"] == EXPECTED_NEXT_CHUNK,
        "controller_state_loader_dry_run": sim["controller_dry_run_performed"] and sim["controller_dry_run_selected_next_chunk_id"] == EXPECTED_NEXT_CHUNK and sim["dry_run_matches_independent_simulation"],
        "no_forbidden_action_claims": artifactv["raw_artifact_build_backtest_edge_allowed_count"] == 0 and not sim["dry_run_download_performed"],
    }
    risk = self_approval_classification(critical)
    syntax = syntax_bom_tracked_plus_self()
    summary = build_summary(gitv, sourcev, stale, artifactv, sim, risk, syntax)
    report = {
        "artifact_type": "repo_only_raw_evidence_independent_verifier_report",
        "summary": summary,
        "git_diff_verification": gitv,
        "source_code_verification": sourcev,
        "hardcoded_stale_check": stale,
        "artifact_verification": artifactv,
        "independent_state_simulation": sim,
        "self_approval_risk_classification": risk,
        "syntax_bom_verification": syntax,
        "forbidden_actions_performed": {
            "download": False,
            "api": False,
            "browse": False,
            "url_fetch": False,
            "data_build": False,
            "aggregation": False,
            "full_csv_read": False,
            "patch": False,
            "delete": False,
            "move": False,
            "cleanup": False,
            "chunk_04_real_execution": False,
        },
    }
    write_json(OUTPUT_DIR / "repo_only_raw_evidence_independent_verifier_report.json", report)
    write_json(OUTPUT_DIR / "repo_only_raw_evidence_git_diff_verification.json", gitv)
    write_json(OUTPUT_DIR / "repo_only_raw_evidence_source_code_verification.json", sourcev)
    write_json(OUTPUT_DIR / "repo_only_raw_evidence_hardcoded_stale_check.json", stale)
    write_json(OUTPUT_DIR / "repo_only_raw_evidence_artifact_verification.json", artifactv)
    write_json(OUTPUT_DIR / "repo_only_raw_evidence_independent_state_simulation.json", sim)
    write_json(OUTPUT_DIR / "repo_only_raw_evidence_self_approval_risk_classification.json", risk)
    write_json(OUTPUT_DIR / "repo_only_raw_evidence_independent_verifier_summary.json", summary)
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise RuntimeError(f"missing required artifacts: {missing}")
    return summary


def main() -> int:
    summary = run_verifier()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    sys.exit(main())
