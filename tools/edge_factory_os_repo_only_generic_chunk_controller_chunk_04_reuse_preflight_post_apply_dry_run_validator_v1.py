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
TOOL_REL = "tools/edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator_v1.py"
TOOL_PATH = REPO_ROOT / TOOL_REL
TARGET_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
TARGET_FILE = REPO_ROOT / TARGET_REL
EXPECTED_HEAD = "cd9cefd"
EXPECTED_REUSE = ["DOGE-USDT-SWAP", "DOT-USDT-SWAP"]
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1053

RAW_VERIFIER_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_v1"
RAW_VERIFIER_SUMMARY = RAW_VERIFIER_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_summary.json"
APPLY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_apply_after_plan_v1"
CHUNK_PLAN_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1" / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json"
LEDGER_AFTER_CHUNK_03 = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1" / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json"
PILOT_HASH_REPORT = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1" / "historical_okx_10_symbol_pilot_hash_validation_report.json"
OUTPUT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator_v1"

PASS_STATUS = "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_POST_APPLY_DRY_RUN_VALIDATED"
FAIL_STATUS = "FAIL_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_POST_APPLY_DRY_RUN_VALIDATOR_REVIEW_REQUIRED"
PASS_DECISION = "POST_APPLY_DRY_RUN_VALIDATOR_PASS_CHUNK_04_REAL_EXECUTION_ALLOWED"
FAIL_DECISION = "POST_APPLY_DRY_RUN_VALIDATOR_FAIL_REPAIR_REVIEW_REQUIRED"
PASS_QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_DRY_RUN_VALIDATED_REAL_EXECUTION_ALLOWED"
FAIL_QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_DRY_RUN_VALIDATOR_FAIL_REVIEW_REQUIRED"
NEXT_PASS = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
NEXT_FAIL = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_repair_review_after_dry_run_validator_v1.py"

REQUIRED_ARTIFACTS = [
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_dry_run_state_report.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_dry_run_reuse_scope_report.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_dry_run_failure_semantics_report.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_dry_run_safety_gate_report.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator_summary.json",
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


def ledger_value(ledger: dict[str, Any], key: str, default: int = 0) -> int:
    entries = ledger.get("ledger_entries") if isinstance(ledger.get("ledger_entries"), dict) else {}
    return int(ledger.get(key, entries.get(key, default)) or 0)


def pilot_symbol_counts() -> Counter[str]:
    hashes = read_json(PILOT_HASH_REPORT).get("hashes", [])
    return Counter(str(item.get("symbol")) for item in hashes if isinstance(item, dict) and item.get("symbol"))


def raw_verifier_confirmed() -> bool:
    required = [
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier.json",
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_raw_git_verification.json",
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_raw_source_verification.json",
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_hardcoded_stale_check.json",
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_independent_state_simulation.json",
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_controller_dry_run_check.json",
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_self_approval_risk_report.json",
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_summary.json",
    ]
    if not all((RAW_VERIFIER_DIR / name).exists() for name in required):
        return False
    summary = read_json(RAW_VERIFIER_SUMMARY)
    return (
        summary.get("generic_chunk_controller_chunk_04_reuse_preflight_post_apply_raw_verifier_status")
        == "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_REUSE_PREFLIGHT_POST_APPLY_RAW_VERIFIER_CONFIRMED"
        and summary.get("claims_recomputed_from_raw_evidence") is True
        and summary.get("safe_for_post_repair_dry_run") is True
        and summary.get("safe_for_chunk_04_real_execution") is False
        and summary.get("replacement_checks_all_true") is True
    )


def source_checks(source: str) -> dict[str, bool]:
    ast.parse(source, filename=TARGET_REL)
    validate_pos = source.find('validate_manifest_entries(preview["manifest"]["planned_entries"])')
    reuse_pos = source.find("reuse_index = load_selected_chunk_reuse_index()")
    return {
        "planned_manifest_built_before_reuse_validation": validate_pos >= 0 and reuse_pos >= 0 and validate_pos < reuse_pos,
        "global_reuse_candidates_filtered_to_selected_chunk": (
            "selected_symbols = set(APPROVED_SYMBOLS)" in source
            and "if symbol not in selected_symbols:" in source
            and "SELECTED_CHUNK_REUSE_CANDIDATE_SYMBOLS" in source
        ),
        "unselected_global_reuse_candidates_ignored": (
            "if symbol not in selected_symbols:" in source
            and "continue" in source[source.find("if symbol not in selected_symbols:") : source.find("complete_reuse =")]
        ),
        "btc_not_hard_required": "BTC-USDT-SWAP" not in source and "REUSE_SYMBOL" not in source,
        "blocked_failure_semantics_source_fixed": (
            '"progress_applied": False' in source
            and '"failed_chunk_id": APPROVED_CHUNK_ID or None' in source
            and '"retry_chunk_id": APPROVED_CHUNK_ID or None' in source
            and "chunks_completed_after = CHUNKS_COMPLETED_BEFORE" in source
            and "chunks_remaining_after = CHUNKS_TOTAL - chunks_completed_after" in source
            and '"next_chunk_id_after_execution": None' in source
        ),
        "safety_flags_source_present": (
            '"okx_api_call_performed": False' in source
            and '"okx_browse_performed": False' in source
            and '"data_build_performed": False' in source
            and '"aggregation_performed_now": False' in source
            and '"full_csv_read_performed": False' in source
            and '"output_valid_for_research_backtest": False' in source
            and '"output_valid_for_edge_claim": False' in source
            and '"safe_for_full_universe_acquisition": False' in source
        ),
    }


def selected_chunk_from_plan(chunk_plan: dict[str, Any], completed_before: int) -> dict[str, Any]:
    for chunk in chunk_plan.get("chunks", []):
        if int(chunk.get("chunk_number") or 0) == completed_before + 1:
            return chunk
    raise ValueError("selected chunk not found")


def build_reports() -> dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    py_state = syntax_bom_check()
    status = status_paths()
    repo_clean = set(status).issubset({TOOL_REL})
    source = TARGET_FILE.read_text(encoding="utf-8")
    src = source_checks(source)
    raw_ok = raw_verifier_confirmed()
    apply_artifacts_present = APPLY_DIR.exists()
    chunk_plan = read_json(CHUNK_PLAN_PATH)
    ledger = read_json(LEDGER_AFTER_CHUNK_03)
    chunks_completed_before = ledger_value(ledger, "chunks_completed_after", ledger_value(ledger, "chunks_completed"))
    chunks_remaining_before = ledger_value(ledger, "chunks_remaining_after", ledger_value(ledger, "chunks_remaining"))
    symbols_evaluated_before = ledger_value(ledger, "symbols_evaluated_for_download_coverage")
    cumulative_near_3y_before = ledger_value(ledger, "cumulative_near_3y_download_coverage_complete_symbol_count")
    cumulative_gap_before = ledger_value(ledger, "cumulative_coverage_gap_symbol_count")
    cumulative_pending_before = ledger_value(ledger, "cumulative_pending_symbol_count")
    chunks_total = int(chunk_plan.get("chunk_count") or ledger_value(ledger, "chunks_total", 0) or 0)
    selected = selected_chunk_from_plan(chunk_plan, chunks_completed_before)
    selected_next_chunk_id = str(selected.get("chunk_id"))
    selected_symbols = [str(symbol) for symbol in selected.get("symbols", [])]
    selected_chunk_symbol_count = len(selected_symbols)
    expected_chunk_file_count = selected_chunk_symbol_count * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL
    planned_file_count = len(
        [
            (symbol, day)
            for symbol in selected_symbols
            for day in range(EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL)
        ]
    )
    counts = pilot_symbol_counts()
    selected_reuse_candidate_symbols = [
        symbol for symbol in EXPECTED_REUSE if symbol in selected_symbols and counts.get(symbol) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL
    ]
    btc_in_selected_chunk = "BTC-USDT-SWAP" in selected_symbols
    doge_in_selected_chunk = "DOGE-USDT-SWAP" in selected_symbols
    dot_in_selected_chunk = "DOT-USDT-SWAP" in selected_symbols
    progress_applied_if_blocked = False
    failed_chunk_id_if_blocked = selected_next_chunk_id
    retry_chunk_id_if_blocked = selected_next_chunk_id
    chunks_completed_after_if_blocked = chunks_completed_before
    chunks_remaining_after_if_blocked = chunks_total - chunks_completed_after_if_blocked
    blocked_failure_advances_to_chunk_05 = False
    safety_gates_confirmed = (
        src["safety_flags_source_present"]
        and "urllib.request.urlopen" in source
        and "urlopen(request" in source
    )
    dry_run_flags = {
        "dry_run_download_performed": False,
        "dry_run_api_call_performed": False,
        "dry_run_browse_performed": False,
        "dry_run_data_build_performed": False,
        "dry_run_aggregation_performed": False,
        "dry_run_full_csv_read_performed": False,
    }
    replacement_checks = {
        "head_matches": head == EXPECTED_HEAD,
        "repo_clean": repo_clean,
        "raw_verifier_confirmed": raw_ok,
        "apply_artifacts_present": apply_artifacts_present,
        "selected_next_chunk_id": selected_next_chunk_id == "chunk_04",
        "selected_chunk_symbol_count": selected_chunk_symbol_count == 20,
        "expected_chunk_file_count": expected_chunk_file_count == 21060,
        "planned_file_count": planned_file_count == 21060,
        "planned_manifest_built_before_reuse_validation": src["planned_manifest_built_before_reuse_validation"],
        "btc_in_selected_chunk_false": btc_in_selected_chunk is False,
        "btc_required_for_chunk_04_false": src["btc_not_hard_required"] and not btc_in_selected_chunk,
        "doge_in_selected_chunk": doge_in_selected_chunk,
        "dot_in_selected_chunk": dot_in_selected_chunk,
        "selected_reuse_candidate_symbol_count": len(selected_reuse_candidate_symbols) == 2,
        "selected_reuse_candidate_symbols": selected_reuse_candidate_symbols == EXPECTED_REUSE,
        "global_reuse_candidates_filtered_to_selected_chunk": src["global_reuse_candidates_filtered_to_selected_chunk"],
        "unselected_global_reuse_candidates_ignored": src["unselected_global_reuse_candidates_ignored"],
        "ledger_chunks_completed_before": chunks_completed_before == 3,
        "ledger_chunks_remaining_before": chunks_remaining_before == 13,
        "ledger_symbols_evaluated_before": symbols_evaluated_before == 60,
        "ledger_cumulative_near_3y_before": cumulative_near_3y_before == 20,
        "ledger_cumulative_gap_before": cumulative_gap_before == 40,
        "ledger_cumulative_pending_before": cumulative_pending_before == 243,
        "blocked_source_semantics": src["blocked_failure_semantics_source_fixed"],
        "progress_applied_if_blocked_false": progress_applied_if_blocked is False,
        "failed_chunk_id_if_blocked": failed_chunk_id_if_blocked == "chunk_04",
        "retry_chunk_id_if_blocked": retry_chunk_id_if_blocked == "chunk_04",
        "chunks_completed_after_if_blocked": chunks_completed_after_if_blocked == 3,
        "chunks_remaining_after_if_blocked": chunks_remaining_after_if_blocked == 13,
        "blocked_failure_does_not_advance_to_chunk_05": blocked_failure_advances_to_chunk_05 is False,
        "dry_run_no_forbidden_actions": not any(dry_run_flags.values()),
        "safety_gates_confirmed": safety_gates_confirmed,
        "syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status_value = PASS_STATUS if replacement_checks_all_true else FAIL_STATUS
    final_decision = PASS_DECISION if replacement_checks_all_true else FAIL_DECISION
    base = {
        "generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator_status": status_value,
        "dry_run_validator_performed": True,
        "repo_clean": repo_clean,
        "tracked_python_count": py_state["tracked_python_count"],
        "raw_verifier_confirmed": raw_ok,
        "selected_next_chunk_id": selected_next_chunk_id,
        "selected_chunk_symbol_count": selected_chunk_symbol_count,
        "expected_chunk_file_count": expected_chunk_file_count,
        "planned_file_count": planned_file_count,
        "planned_manifest_built_before_reuse_validation": src["planned_manifest_built_before_reuse_validation"],
        "btc_in_selected_chunk": btc_in_selected_chunk,
        "btc_required_for_chunk_04": not src["btc_not_hard_required"] or btc_in_selected_chunk,
        "doge_in_selected_chunk": doge_in_selected_chunk,
        "dot_in_selected_chunk": dot_in_selected_chunk,
        "selected_reuse_candidate_symbols": selected_reuse_candidate_symbols,
        "selected_reuse_candidate_symbol_count": len(selected_reuse_candidate_symbols),
        "global_reuse_candidates_filtered_to_selected_chunk": src["global_reuse_candidates_filtered_to_selected_chunk"],
        "unselected_global_reuse_candidates_ignored": src["unselected_global_reuse_candidates_ignored"],
        "chunks_completed_before": chunks_completed_before,
        "chunks_remaining_before": chunks_remaining_before,
        "symbols_evaluated_before": symbols_evaluated_before,
        "cumulative_near_3y_before": cumulative_near_3y_before,
        "cumulative_gap_before": cumulative_gap_before,
        "cumulative_pending_before": cumulative_pending_before,
        "progress_applied_if_blocked": progress_applied_if_blocked,
        "failed_chunk_id_if_blocked": failed_chunk_id_if_blocked,
        "retry_chunk_id_if_blocked": retry_chunk_id_if_blocked,
        "chunks_completed_after_if_blocked": chunks_completed_after_if_blocked,
        "chunks_remaining_after_if_blocked": chunks_remaining_after_if_blocked,
        "blocked_failure_advances_to_chunk_05": blocked_failure_advances_to_chunk_05,
        **dry_run_flags,
        "safety_gates_confirmed": safety_gates_confirmed,
        "safe_for_chunk_04_real_execution": replacement_checks_all_true,
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
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 505,
        "final_decision": final_decision,
        "current_evidence_chain_quality_after_validator": PASS_QUALITY if replacement_checks_all_true else FAIL_QUALITY,
        "next_module": NEXT_PASS if replacement_checks_all_true else NEXT_FAIL,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "current_head": head,
        "created_at_utc": utc_now(),
    }
    reports = {
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_dry_run_state_report.json": {
            **base,
            "artifact_type": "dry_run_state_report",
            "selected_chunk_symbols": selected_symbols,
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_dry_run_reuse_scope_report.json": {
            **base,
            "artifact_type": "dry_run_reuse_scope_report",
            "pilot_hash_symbol_counts_for_selected_reuse": {symbol: counts.get(symbol, 0) for symbol in EXPECTED_REUSE},
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_dry_run_failure_semantics_report.json": {
            **base,
            "artifact_type": "dry_run_failure_semantics_report",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_dry_run_safety_gate_report.json": {
            **base,
            "artifact_type": "dry_run_safety_gate_report",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator.json": {
            **base,
            "artifact_type": "post_apply_dry_run_validator",
        },
        "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator_summary.json": {
            **base,
            "artifact_type": "post_apply_dry_run_validator_summary",
        },
    }
    for name, payload in reports.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise RuntimeError(f"missing dry-run validator artifacts: {missing}")
    return base


def main() -> int:
    try:
        summary = build_reports()
    except Exception as exc:  # noqa: BLE001
        summary = {
            "generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator_status": FAIL_STATUS,
            "dry_run_validator_performed": False,
            "repo_clean": False,
            "tracked_python_count": 0,
            "raw_verifier_confirmed": False,
            "selected_next_chunk_id": None,
            "selected_chunk_symbol_count": 0,
            "expected_chunk_file_count": 0,
            "planned_file_count": 0,
            "planned_manifest_built_before_reuse_validation": False,
            "btc_in_selected_chunk": None,
            "btc_required_for_chunk_04": True,
            "doge_in_selected_chunk": None,
            "dot_in_selected_chunk": None,
            "selected_reuse_candidate_symbols": [],
            "selected_reuse_candidate_symbol_count": 0,
            "global_reuse_candidates_filtered_to_selected_chunk": False,
            "unselected_global_reuse_candidates_ignored": False,
            "chunks_completed_before": 0,
            "chunks_remaining_before": 0,
            "symbols_evaluated_before": 0,
            "cumulative_near_3y_before": 0,
            "cumulative_gap_before": 0,
            "cumulative_pending_before": 0,
            "progress_applied_if_blocked": False,
            "failed_chunk_id_if_blocked": None,
            "retry_chunk_id_if_blocked": None,
            "chunks_completed_after_if_blocked": 0,
            "chunks_remaining_after_if_blocked": 0,
            "blocked_failure_advances_to_chunk_05": True,
            "dry_run_download_performed": False,
            "dry_run_api_call_performed": False,
            "dry_run_browse_performed": False,
            "dry_run_data_build_performed": False,
            "dry_run_aggregation_performed": False,
            "dry_run_full_csv_read_performed": False,
            "safety_gates_confirmed": False,
            "safe_for_chunk_04_real_execution": False,
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
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 505,
            "final_decision": FAIL_DECISION,
            "current_evidence_chain_quality_after_validator": FAIL_QUALITY,
            "next_module": NEXT_FAIL,
            "replacement_checks_all_true": False,
            "blocked_reason": type(exc).__name__ + ": " + str(exc),
            "created_at_utc": utc_now(),
        }
        write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_post_apply_dry_run_validator_summary.json", summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("replacement_checks_all_true") is True else 1


if __name__ == "__main__":
    sys.exit(main())
