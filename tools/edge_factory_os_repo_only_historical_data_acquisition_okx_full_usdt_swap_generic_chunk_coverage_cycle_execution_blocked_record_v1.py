from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
TOOL_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_blocked_record_v1.py"
TOOL_PATH = REPO_ROOT / TOOL_REL
EXPECTED_HEAD = "cfcff02"

FAILED_RUN_SUMMARY = (
    EDGE_LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1"
    / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_chunk_04_summary.json"
)
TARGET_CONTROLLER = REPO_ROOT / "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
OUTPUT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_blocked_record_v1"
NEXT_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_chunk_04_reuse_preflight_failure_diagnostic_v1.py"

BLOCKED_RECORD_STATUS = "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_CHUNK_04_FAILED_CYCLE_BLOCKED_RECORD_READY_FOR_DIAGNOSTIC"
FAILURE_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CYCLE_EXECUTION_FAILED"
QUALITY = "GENERIC_CHUNK_CONTROLLER_CHUNK_04_FAILED_CYCLE_BLOCKED_RECORD_READY_FOR_REUSE_PREFLIGHT_DIAGNOSTIC"
BLOCKER_REASON = "BTC-USDT-SWAP reuse candidate count mismatch"

REQUIRED_ARTIFACTS = [
    "repo_only_generic_chunk_controller_chunk_04_failed_cycle_blocked_record.json",
    "repo_only_generic_chunk_controller_chunk_04_failure_symptom_report.json",
    "repo_only_generic_chunk_controller_chunk_04_failure_hypothesis_report.json",
    "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_diagnostic_approval_record.json",
    "repo_only_generic_chunk_controller_chunk_04_failed_cycle_blocked_record_summary.json",
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


def build_payloads() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = status_lines()
    failed = read_json(FAILED_RUN_SUMMARY)
    source = TARGET_CONTROLLER.read_text(encoding="utf-8")
    chunks_total = int(failed.get("chunks_total") or 0)
    completed_after = int(failed.get("chunks_completed_after") or 0)
    expected_remaining_if_no_progress = chunks_total - completed_after
    blocked_reason = str(failed.get("blocked_reason", "")).removeprefix("ExecutionBlocked: ")
    selected_symbols = list(failed.get("chunk_symbols", []))
    symptom_report = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_failure_symptom_report",
        "failed_run_summary_path": str(FAILED_RUN_SUMMARY),
        "failed_chunk_id": failed.get("chunk_id"),
        "failure_status": failed.get("historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_status"),
        "blocked_reason": blocked_reason,
        "selected_chunk_symbols": selected_symbols,
        "btc_in_selected_chunk_symbols": "BTC-USDT-SWAP" in selected_symbols,
        "expected_chunk_file_count": failed.get("expected_chunk_file_count"),
        "planned_file_count": failed.get("planned_file_count"),
        "planned_file_count_mismatch": failed.get("planned_file_count") != failed.get("expected_chunk_file_count"),
        "count_reconciliation_pass": failed.get("count_reconciliation_pass"),
        "chunks_remaining_after_reported": failed.get("chunks_remaining_after"),
        "chunks_remaining_after_expected_if_no_progress": expected_remaining_if_no_progress,
        "chunks_remaining_mismatch": failed.get("chunks_remaining_after") != expected_remaining_if_no_progress,
        "download_performed_before_block": failed.get("data_download_performed") is True or failed.get("archive_download_performed") is True,
        "generic_cycle_execution_performed": failed.get("generic_cycle_execution_performed"),
    }
    hypothesis_report = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_failure_hypothesis_report",
        "stale_reuse_candidate_suspected": blocked_reason == BLOCKER_REASON,
        "btc_reuse_leak_into_chunk_04_suspected": blocked_reason.startswith("BTC-USDT-SWAP") and "BTC-USDT-SWAP" not in selected_symbols,
        "controller_preflight_bug_suspected": failed.get("planned_file_count") == 0 and failed.get("expected_chunk_file_count") == 21060,
        "planned_manifest_not_built_before_reuse_validation_suspected": failed.get("planned_file_count") == 0,
        "chunks_remaining_bug_suspected": failed.get("chunks_remaining_after") != expected_remaining_if_no_progress,
        "reuse_logic_global_not_selected_chunk_scoped_suspected": "REUSE_SYMBOL = \"BTC-USDT-SWAP\"" in source and "REUSE_SYMBOL in APPROVED_SYMBOLS" in source,
        "diagnostic_questions": [
            "why BTC-USDT-SWAP reuse candidate is evaluated for chunk_04",
            "why planned_file_count is zero",
            "why the chunk_04 planned manifest was not built or counted before blocking",
            "why chunks_remaining_after is 14 instead of 13",
            "whether DOGE/DOT reuse candidates from the 10-symbol pilot are handled correctly",
            "whether reuse candidate logic is global instead of selected-chunk scoped",
            "whether planned manifest should be built before reuse validation",
            "whether latest chunk_03 ledger/state loading is consistent",
        ],
    }
    approval = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_diagnostic_approval_record",
        "created_at_utc": utc_now(),
        "approval_grants_blocked_record_now": True,
        "approval_grants_diagnostic_next": True,
        "approval_grants_patch_apply_now": False,
        "approval_grants_chunk_04_rerun_now": False,
        "approval_grants_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "next_module": NEXT_MODULE,
    }
    checks = {
        "head_matches": head == EXPECTED_HEAD,
        "repo_clean": repo_effectively_clean(status),
        "failed_run_exists": FAILED_RUN_SUMMARY.exists(),
        "target_controller_exists": TARGET_CONTROLLER.exists(),
        "failure_status_confirmed": failed.get("historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_status") == FAILURE_STATUS,
        "failed_chunk_04": failed.get("chunk_id") == "chunk_04",
        "blocked_reason_confirmed": blocked_reason == BLOCKER_REASON,
        "fail_closed_before_download": failed.get("generic_cycle_execution_performed") is False and failed.get("data_download_performed") is False and failed.get("archive_download_performed") is False,
        "no_code_change": True,
        "planned_count_mismatch": symptom_report["planned_file_count_mismatch"] is True,
        "chunks_remaining_mismatch": symptom_report["chunks_remaining_mismatch"] is True,
        "diagnostic_approval_not_patch_or_rerun": approval["approval_grants_diagnostic_next"] is True and approval["approval_grants_patch_apply_now"] is False and approval["approval_grants_chunk_04_rerun_now"] is False,
        "no_forbidden_actions": True,
    }
    passed = all(checks.values())
    summary = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_failed_cycle_blocked_record_summary",
        "generic_chunk_controller_chunk_04_failed_cycle_blocked_record_status": BLOCKED_RECORD_STATUS if passed else "BLOCKED_RECORD_FAILED_CLOSED",
        "blocked_record_created": passed,
        "created_at_utc": utc_now(),
        "failed_chunk_id": failed.get("chunk_id"),
        "failure_status": failed.get("historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_status"),
        "fail_closed_before_download": checks["fail_closed_before_download"],
        "blocker_reason": blocked_reason,
        "no_download_performed": failed.get("data_download_performed") is False and failed.get("archive_download_performed") is False,
        "no_code_change": True,
        "repo_clean_after_failure": repo_effectively_clean(status),
        "expected_chunk_file_count": failed.get("expected_chunk_file_count"),
        "planned_file_count": failed.get("planned_file_count"),
        "planned_file_count_mismatch": symptom_report["planned_file_count_mismatch"],
        "count_reconciliation_pass": failed.get("count_reconciliation_pass"),
        "selected_chunk_symbols": selected_symbols,
        "btc_reuse_leak_into_chunk_04_suspected": hypothesis_report["btc_reuse_leak_into_chunk_04_suspected"],
        "stale_reuse_candidate_suspected": hypothesis_report["stale_reuse_candidate_suspected"],
        "controller_preflight_bug_suspected": hypothesis_report["controller_preflight_bug_suspected"],
        "chunks_remaining_after_reported": failed.get("chunks_remaining_after"),
        "chunks_remaining_after_expected_if_no_progress": expected_remaining_if_no_progress,
        "chunks_remaining_mismatch": symptom_report["chunks_remaining_mismatch"],
        "diagnostic_approval_record_created": approval["approval_grants_diagnostic_next"],
        "approval_grants_diagnostic_next": approval["approval_grants_diagnostic_next"],
        "approval_grants_patch_apply_now": approval["approval_grants_patch_apply_now"],
        "approval_grants_chunk_04_rerun_now": approval["approval_grants_chunk_04_rerun_now"],
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": int(failed.get("active_p1_attention_count") or 0),
        "current_evidence_chain_quality_after_blocked_record": QUALITY if passed else "GENERIC_CHUNK_CONTROLLER_CHUNK_04_FAILED_CYCLE_BLOCKED_RECORD_FAILED_CLOSED",
        "next_module": NEXT_MODULE,
        "replacement_checks_all_true": passed,
        "replacement_checks": checks,
    }
    blocked_record = {
        "artifact_type": "repo_only_generic_chunk_controller_chunk_04_failed_cycle_blocked_record",
        "summary": summary,
        "failed_run_raw_summary": failed,
        "symptom_report": symptom_report,
        "hypothesis_report": hypothesis_report,
        "approval_record": approval,
        "forbidden_actions_performed": {
            "patch": False,
            "chunk_04_rerun": False,
            "download": False,
            "api": False,
            "browse": False,
            "url_fetch": False,
            "zip_csv_parquet_read": False,
            "data_build": False,
            "aggregation": False,
            "delete": False,
            "move": False,
            "cleanup": False,
            "research_backtest_edge": False,
            "runtime_capital_live": False,
        },
    }
    return blocked_record, symptom_report, hypothesis_report, approval, summary


def run() -> dict[str, Any]:
    blocked_record, symptom_report, hypothesis_report, approval, summary = build_payloads()
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_failed_cycle_blocked_record.json", blocked_record)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_failure_symptom_report.json", symptom_report)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_failure_hypothesis_report.json", hypothesis_report)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_reuse_preflight_diagnostic_approval_record.json", approval)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_failed_cycle_blocked_record_summary.json", summary)
    syntax = syntax_bom_check()
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise RuntimeError(f"missing required artifacts: {missing}")
    if syntax["syntax_error_count"] or syntax["bom_error_count"]:
        summary["replacement_checks_all_true"] = False
        summary["syntax_bom_report"] = syntax
        write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_chunk_04_failed_cycle_blocked_record_summary.json", summary)
    return summary


def main() -> int:
    summary = run()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    sys.exit(main())
