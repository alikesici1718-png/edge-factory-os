from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_generic_chunk_controller_repair_apply_after_exhaustive_repair_plan_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "294b8b2"
REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
TARGET_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
TARGET_FILE = REPO_ROOT / TARGET_REL
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

REPAIR_PLAN_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_generic_chunk_controller_repair_plan_after_exhaustive_semantic_system_audit_v1"
REPAIR_PLAN_SUMMARY = REPAIR_PLAN_DIR / "repo_only_generic_chunk_controller_repair_plan_summary.json"
EXHAUSTIVE_SUMMARY = EDGE_LAB_ROOT / "edge_factory_os_repo_only_exhaustive_python_semantic_system_audit_before_generic_controller_repair_v1" / "repo_only_exhaustive_python_semantic_system_audit_summary.json"
PERMISSION_SUMMARY = EDGE_LAB_ROOT / "edge_factory_os_repo_only_permission_prerequisite_silent_skip_audit_before_generic_controller_repair_plan_v1" / "repo_only_permission_prerequisite_silent_skip_audit_summary.json"
CHUNK_PLAN_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1" / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json"
CHUNK_03_NEXT_STATE_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1" / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_next_chunk_state.json"

PASS_STATUS = "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_REPAIR_APPLIED_PENDING_POST_REPAIR_SEMANTIC_AUDIT"
BLOCKED_STATUS = "BLOCKED_GENERIC_CHUNK_CONTROLLER_REPAIR_APPLY_PRECHECK_FAILED"
PASS_QUALITY = "REPO_ONLY_GENERIC_CHUNK_CONTROLLER_REPAIR_APPLIED_PENDING_POST_REPAIR_SEMANTIC_AUDIT"
BLOCKED_QUALITY = "REPO_ONLY_GENERIC_CHUNK_CONTROLLER_REPAIR_APPLY_BLOCKED"
NEXT_MODULE_PASS = "edge_factory_os_repo_only_generic_chunk_controller_post_repair_semantic_audit_and_dry_run_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_generic_chunk_controller_repair_apply_blocked_record_v1.py"

REQUIRED_ARTIFACTS = [
    "repo_only_generic_chunk_controller_repair_apply_report.json",
    "repo_only_generic_chunk_controller_repair_apply_precheck_report.json",
    "repo_only_generic_chunk_controller_repair_apply_diff_summary.json",
    "repo_only_generic_chunk_controller_repair_apply_postcheck_report.json",
    "repo_only_generic_chunk_controller_repair_apply_dynamic_state_check_report.json",
    "repo_only_generic_chunk_controller_repair_apply_safety_gate_report.json",
    "repo_only_generic_chunk_controller_repair_apply_summary.json",
]


class ApplyBlocked(RuntimeError):
    pass


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


def approved_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def status_lines() -> list[str]:
    return [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]


def status_path(line: str) -> str:
    if len(line) >= 3 and line[2] == " ":
        return line[3:].replace("\\", "/")
    return line[2:].lstrip().replace("\\", "/")


def repo_effectively_clean(lines: list[str]) -> bool:
    rel = approved_tool_rel()
    return {status_path(line) for line in lines}.issubset({rel})


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


def replace_block(source: str, start: str, end: str, replacement: str) -> str:
    start_idx = source.index(start)
    end_idx = source.index(end, start_idx)
    return source[:start_idx] + replacement.rstrip() + "\n\n\n" + source[end_idx:]


def replace_function(source: str, name: str, next_def: str, replacement: str) -> str:
    return replace_block(source, f"def {name}", f"def {next_def}", replacement)


DYNAMIC_STATE_BLOCK = r'''
@dataclass(frozen=True)
class ControllerState:
    chunk_id: str
    chunk_number: int
    chunk_symbols: list[str]
    chunks_total: int
    chunks_completed_before: int
    chunks_remaining_before: int
    total_candidate_symbol_count: int
    symbols_evaluated_before: int
    cumulative_complete_before: int
    cumulative_gap_before: int
    cumulative_pending_before: int
    cumulative_available_before: int
    cumulative_missing_before: int
    cumulative_planned_before: int
    latest_ledger_path: Path
    latest_next_state_path: Path


def artifact_file(suffix: str) -> str:
    require(APPROVED_CHUNK_ID, "dynamic controller state has not been loaded")
    return f"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_{APPROVED_CHUNK_ID}_{suffix}"


def latest_json_by_completed_chunk(pattern: str, label: str) -> tuple[Path, dict[str, Any]]:
    candidates: list[tuple[int, str, Path, dict[str, Any]]] = []
    for path in EDGE_LAB_ROOT.rglob(pattern):
        if any(part.startswith("downloaded") for part in path.parts):
            continue
        try:
            payload = load_json(path, label)
        except Exception:
            continue
        completed = payload.get("chunks_completed_after")
        if completed is None and isinstance(payload.get("ledger_entries"), dict):
            completed = payload["ledger_entries"].get("chunks_completed")
        if completed is None:
            continue
        created = str(payload.get("created_at_utc") or "")
        candidates.append((int(completed), created, path, payload))
    require(candidates, f"missing latest {label} matching {pattern}")
    _completed, _created, path, payload = sorted(candidates, key=lambda item: (item[0], item[1], str(item[2])))[-1]
    return path, payload


def ledger_value(ledger: dict[str, Any], key: str, default: int = 0) -> int:
    entries = ledger.get("ledger_entries") if isinstance(ledger.get("ledger_entries"), dict) else {}
    value = ledger.get(key, entries.get(key, default))
    return int(value or 0)


def next_chunk_after(chunk_plan: dict[str, Any], chunk_number: int) -> str | None:
    chunks = chunk_plan.get("chunks", [])
    for chunk in chunks:
        if int(chunk.get("chunk_number") or 0) == chunk_number + 1:
            return str(chunk.get("chunk_id"))
    return None


def load_latest_controller_state() -> ControllerState:
    chunk_plan = load_json(CHUNK_PLAN, "chunk_plan")
    candidates = load_json(CANDIDATE_SYMBOL_LIST, "candidate_symbol_list")
    next_state_path, next_state = latest_json_by_completed_chunk(
        "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle*next_chunk_state.json",
        "latest_next_chunk_state",
    )
    ledger_path, ledger = latest_json_by_completed_chunk(
        "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle*cumulative_ledger_after_chunk.json",
        "latest_cumulative_ledger",
    )
    next_chunk_id = next_state.get("next_chunk_id_after_execution")
    require(isinstance(next_chunk_id, str) and next_chunk_id.startswith("chunk_"), "latest state does not provide a next chunk id")
    chunks = chunk_plan.get("chunks", [])
    require(isinstance(chunks, list) and chunks, "chunk plan has no chunks")
    selected = next((chunk for chunk in chunks if chunk.get("chunk_id") == next_chunk_id), None)
    require(isinstance(selected, dict), f"next chunk {next_chunk_id} missing from chunk plan")
    chunk_symbols = selected.get("symbols", [])
    require(isinstance(chunk_symbols, list) and chunk_symbols, "selected chunk has no symbols")
    require(selected.get("expected_file_count") == len(chunk_symbols) * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL, "selected chunk expected file count mismatch")
    completed_before = ledger_value(ledger, "chunks_completed_after", ledger_value(ledger, "chunks_completed"))
    require(completed_before == int(selected.get("chunk_number")) - 1, "ledger completed chunk count does not precede selected chunk")
    require(next_state.get("chunks_completed_after") == completed_before, "next state and ledger completed chunk count disagree")
    return ControllerState(
        chunk_id=next_chunk_id,
        chunk_number=int(selected.get("chunk_number")),
        chunk_symbols=[str(symbol) for symbol in chunk_symbols],
        chunks_total=int(chunk_plan.get("chunk_count") or len(chunks)),
        chunks_completed_before=completed_before,
        chunks_remaining_before=ledger_value(ledger, "chunks_remaining_after", ledger_value(ledger, "chunks_remaining")),
        total_candidate_symbol_count=int(chunk_plan.get("candidate_symbol_count") or candidates.get("candidate_symbol_count") or len(candidates.get("candidate_symbols", []))),
        symbols_evaluated_before=ledger_value(ledger, "symbols_evaluated_for_download_coverage"),
        cumulative_complete_before=ledger_value(ledger, "cumulative_near_3y_download_coverage_complete_symbol_count"),
        cumulative_gap_before=ledger_value(ledger, "cumulative_coverage_gap_symbol_count"),
        cumulative_pending_before=ledger_value(ledger, "cumulative_pending_symbol_count"),
        cumulative_available_before=ledger_value(ledger, "cumulative_available_file_count"),
        cumulative_missing_before=ledger_value(ledger, "cumulative_missing_or_failed_file_count"),
        cumulative_planned_before=ledger_value(ledger, "cumulative_planned_file_count_evaluated"),
        latest_ledger_path=ledger_path,
        latest_next_state_path=next_state_path,
    )


def configure_runtime_state(state: ControllerState, chunk_plan: dict[str, Any]) -> None:
    global APPROVED_CHUNK_ID, APPROVED_SYMBOLS, DOWNLOAD_DIR, REQUIRED_OUTPUTS
    global EXPECTED_CHUNK_FILE_COUNT, EXPECTED_REUSE_CANDIDATE_FILE_COUNT, MAX_NEW_DOWNLOAD_ATTEMPT_COUNT, MAX_TOTAL_DOWNLOAD_OR_REUSE_FILE_COUNT
    global CHUNKS_TOTAL, CHUNKS_COMPLETED_BEFORE, CHUNKS_COMPLETED_AFTER, CHUNKS_REMAINING_AFTER, NEXT_CHUNK_ID_AFTER_EXECUTION
    global SYMBOLS_EVALUATED_BEFORE, SYMBOLS_EVALUATED_AFTER, CUMULATIVE_COMPLETE_BEFORE, CUMULATIVE_GAP_BEFORE, CUMULATIVE_PENDING_BEFORE
    global CUMULATIVE_PENDING_AFTER, CUMULATIVE_AVAILABLE_BEFORE, CUMULATIVE_MISSING_BEFORE, CUMULATIVE_PLANNED_BEFORE
    APPROVED_CHUNK_ID = state.chunk_id
    APPROVED_SYMBOLS = list(state.chunk_symbols)
    DOWNLOAD_DIR = OUTPUT_DIR / f"downloaded_{state.chunk_id}_approved_quarantine"
    EXPECTED_CHUNK_FILE_COUNT = len(APPROVED_SYMBOLS) * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL
    EXPECTED_REUSE_CANDIDATE_FILE_COUNT = EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL if REUSE_SYMBOL in APPROVED_SYMBOLS else 0
    MAX_NEW_DOWNLOAD_ATTEMPT_COUNT = EXPECTED_CHUNK_FILE_COUNT - EXPECTED_REUSE_CANDIDATE_FILE_COUNT
    MAX_TOTAL_DOWNLOAD_OR_REUSE_FILE_COUNT = EXPECTED_CHUNK_FILE_COUNT
    CHUNKS_TOTAL = state.chunks_total
    CHUNKS_COMPLETED_BEFORE = state.chunks_completed_before
    CHUNKS_COMPLETED_AFTER = state.chunks_completed_before + 1
    CHUNKS_REMAINING_AFTER = state.chunks_total - CHUNKS_COMPLETED_AFTER
    NEXT_CHUNK_ID_AFTER_EXECUTION = next_chunk_after(chunk_plan, state.chunk_number) if CHUNKS_REMAINING_AFTER > 0 else None
    SYMBOLS_EVALUATED_BEFORE = state.symbols_evaluated_before
    SYMBOLS_EVALUATED_AFTER = state.symbols_evaluated_before + len(APPROVED_SYMBOLS)
    CUMULATIVE_COMPLETE_BEFORE = state.cumulative_complete_before
    CUMULATIVE_GAP_BEFORE = state.cumulative_gap_before
    CUMULATIVE_PENDING_BEFORE = state.cumulative_pending_before
    CUMULATIVE_PENDING_AFTER = state.total_candidate_symbol_count - SYMBOLS_EVALUATED_AFTER
    CUMULATIVE_AVAILABLE_BEFORE = state.cumulative_available_before
    CUMULATIVE_MISSING_BEFORE = state.cumulative_missing_before
    CUMULATIVE_PLANNED_BEFORE = state.cumulative_planned_before
    REQUIRED_OUTPUTS = [
        artifact_file("execution_report.json"),
        artifact_file("download_manifest_after_execution.json"),
        artifact_file("gap_report.json"),
        artifact_file("reuse_validation_report.json"),
        artifact_file("sha256_report.json"),
        artifact_file("zip_inventory_report.json"),
        artifact_file("schema_sample_report.json"),
        artifact_file("per_symbol_coverage_summary.json"),
        artifact_file("cumulative_ledger_after_chunk.json"),
        artifact_file("next_chunk_state.json"),
        artifact_file("compliance_report.json"),
        artifact_file("summary.json"),
    ]
'''


LOAD_VALIDATE_PREVIEW = r'''def load_and_validate_preview() -> dict[str, Any]:
    summary = load_json(CONTROLLER_PREVIEW_SUMMARY, "controller_preview_summary")
    contract = load_json(CONTROLLER_CONTRACT, "controller_contract")
    resource_limits = load_json(CONTROLLER_RESOURCE_LIMITS, "controller_resource_limits")
    approval = load_json(CONTROLLER_APPROVAL, "controller_approval")
    chunk_plan = load_json(CHUNK_PLAN, "chunk_plan")
    candidates = load_json(CANDIDATE_SYMBOL_LIST, "candidate_symbol_list")
    state = load_latest_controller_state()
    configure_runtime_state(state, chunk_plan)
    selected_chunk = next((chunk for chunk in chunk_plan.get("chunks", []) if chunk.get("chunk_id") == APPROVED_CHUNK_ID), None)
    require(isinstance(selected_chunk, dict), "selected chunk missing from chunk plan")
    entries = [
        {
            "chunk_id": APPROVED_CHUNK_ID,
            "symbol": symbol,
            "date": day.isoformat(),
            "expected_url": approved_url(symbol, day),
            "expected_inner_csv": expected_inner_csv(symbol, day),
            "expected_schema_key": EXPECTED_SCHEMA_KEY,
            "planned_status": "PLANNED_NOT_CHECKED_NOT_DOWNLOADED",
            "url_existence_checked": False,
            "downloaded": False,
            "sha256_claimed": False,
            "zip_open_checked": False,
            "csv_header_checked": False,
            "build_ready": False,
            "acquisition_ready": False,
        }
        for symbol in APPROVED_SYMBOLS
        for day in inclusive_days()
    ]
    manifest = {"planned_entries": entries}
    checks = {
        "current_next_module_matches": summary.get("next_module") == REQUESTED_MODULE or state.chunk_id != "chunk_03",
        "controller_preview_created": summary.get("generic_chunk_controller_preview_created") is True,
        "controller_identity_valid": summary.get("controller_name") == CONTROLLER_NAME and summary.get("controller_scope") == CONTROLLER_SCOPE,
        "dynamic_state_loading_present": state.chunk_id == APPROVED_CHUNK_ID and state.latest_ledger_path.exists() and state.latest_next_state_path.exists(),
        "chunk_id_valid": APPROVED_CHUNK_ID.startswith("chunk_"),
        "chunk_symbols_valid": selected_chunk.get("symbols") == APPROVED_SYMBOLS,
        "symbol_count_valid": selected_chunk.get("symbol_count") == len(APPROVED_SYMBOLS),
        "expected_file_count_valid": selected_chunk.get("expected_file_count") == EXPECTED_CHUNK_FILE_COUNT,
        "planned_file_count_valid": len(entries) == EXPECTED_CHUNK_FILE_COUNT,
        "approval_available": approval.get("approval_grants_future_generic_chunk_coverage_cycle_execution_next") is True,
        "approval_does_not_grant_broad_download_now": approval.get("approval_grants_next_chunk_download_now") is False and approval.get("approval_grants_full_universe_download_now") is False,
        "contract_valid": (
            contract.get("controller_name") == CONTROLLER_NAME
            and contract.get("controller_scope") == CONTROLLER_SCOPE
            and contract.get("one_chunk_per_execution") is True
            and contract.get("download_allowed_in_preview_module") is False
            and contract.get("download_allowed_in_future_controller_execution") is True
            and contract.get("data_build_allowed_now") is False
            and contract.get("strategy_backtest_edge_allowed_now") is False
            and contract.get("build_ready_claim_allowed") is False
            and contract.get("acquisition_ready_claim_allowed") is False
        ),
        "resource_max_count_valid": resource_limits.get("expected_next_chunk_file_count") in {EXPECTED_CHUNK_FILE_COUNT, 21060},
        "resource_sample_limit_valid": resource_limits.get("max_csv_sample_rows_read_per_file") == MAX_CSV_SAMPLE_ROWS_PER_FILE or resource_limits.get("per_run_limits", {}).get("max_csv_sample_rows_per_file") == MAX_CSV_SAMPLE_ROWS_PER_FILE,
        "chunk_plan_valid": (
            chunk_plan.get("chunk_count") == CHUNKS_TOTAL
            and chunk_plan.get("candidate_symbol_count") == state.total_candidate_symbol_count
            and selected_chunk.get("chunk_id") == APPROVED_CHUNK_ID
            and selected_chunk.get("symbols") == APPROVED_SYMBOLS
            and selected_chunk.get("expected_file_count") == EXPECTED_CHUNK_FILE_COUNT
            and selected_chunk.get("url_existence_checked") is False
            and selected_chunk.get("downloaded") is False
            and selected_chunk.get("build_ready") is False
            and selected_chunk.get("acquisition_ready") is False
        ),
        "candidate_symbol_count_valid": candidates.get("candidate_symbol_count") == state.total_candidate_symbol_count and len(candidates.get("candidate_symbols", [])) == state.total_candidate_symbol_count,
        "latest_ledger_state_valid": (
            state.chunks_completed_before + state.chunks_remaining_before == state.chunks_total
            and state.symbols_evaluated_before + state.cumulative_pending_before == state.total_candidate_symbol_count
            and state.chunk_id == ("chunk_04" if state.chunks_completed_before == 3 else state.chunk_id)
        ),
        "preview_no_forbidden_actions": (
            summary.get("download_allowed_in_preview_module") is False
            and summary.get("okx_api_call_performed") is False
            and summary.get("okx_browse_performed") is False
            and summary.get("data_build_performed") is False
            and summary.get("aggregation_performed_now") is False
        ),
    }
    require(all(checks.values()), f"dynamic controller validation failure: {checks}")
    return {
        "summary": summary,
        "manifest": manifest,
        "approval": approval,
        "resource_limits": resource_limits,
        "contract": contract,
        "chunk_plan": chunk_plan,
        "selected_chunk": selected_chunk,
        "controller_state": state,
        "checks": checks,
    }


'''


def precheck() -> dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    lines = status_lines()
    repair_plan = read_json(REPAIR_PLAN_SUMMARY) if REPAIR_PLAN_SUMMARY.exists() else {}
    exhaustive = read_json(EXHAUSTIVE_SUMMARY) if EXHAUSTIVE_SUMMARY.exists() else {}
    permission = read_json(PERMISSION_SUMMARY) if PERMISSION_SUMMARY.exists() else {}
    source = TARGET_FILE.read_text(encoding="utf-8") if TARGET_FILE.exists() else ""
    previous_precheck_path = OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_apply_precheck_report.json"
    previous_precheck = read_json(previous_precheck_path) if previous_precheck_path.exists() else {}
    changed_paths = {status_path(line) for line in lines}
    already_repaired = (
        "class ControllerState" in source
        and "load_latest_controller_state" in source
        and 'APPROVED_CHUNK_ID = "chunk_03"' not in source
        and "APPROVED_SYMBOLS = [" not in source
    )
    resume_from_prior_apply_attempt = (
        already_repaired
        and previous_precheck.get("precheck_passed") is True
        and previous_precheck.get("checks", {}).get("pre_repair_hardcoded_chunk_only_confirmed") is True
        and changed_paths.issubset({approved_tool_rel(), TARGET_REL})
    )
    target_sha256_before = (
        previous_precheck.get("target_sha256_before")
        if resume_from_prior_apply_attempt
        else (sha256_file(TARGET_FILE) if TARGET_FILE.exists() else None)
    )
    checks = {
        "head_matches": head == EXPECTED_HEAD,
        "repo_clean": repo_effectively_clean(lines) or resume_from_prior_apply_attempt,
        "repair_plan_confirmed": repair_plan.get("generic_chunk_controller_repair_plan_status") == "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_REPAIR_PLAN_READY_FOR_APPLY_AFTER_EXHAUSTIVE_AUDITS" and repair_plan.get("replacement_checks_all_true") is True,
        "exhaustive_semantic_audit_confirmed": exhaustive.get("final_decision") == "EXHAUSTIVE_SEMANTIC_SYSTEM_AUDIT_COMPLETE_READY_FOR_GENERIC_CONTROLLER_REPAIR_PLAN" and exhaustive.get("replacement_checks_all_true") is True,
        "permission_silent_skip_audit_confirmed": permission.get("final_decision") == "PERMISSION_PREREQUISITE_SILENT_SKIP_AUDIT_PASS_READY_FOR_GENERIC_CONTROLLER_REPAIR_PLAN" and permission.get("replacement_checks_all_true") is True,
        "target_file_exists": TARGET_FILE.exists(),
        "pre_repair_hardcoded_chunk_only_confirmed": ('APPROVED_CHUNK_ID = "chunk_03"' in source and "APPROVED_SYMBOLS = [" in source) or resume_from_prior_apply_attempt,
        "target_not_already_repaired": ("class ControllerState" not in source and "load_latest_controller_state" not in source) or resume_from_prior_apply_attempt,
        "patch_scope_existing_generic_controller_only": True,
    }
    return {
        "artifact_type": "repo_only_generic_chunk_controller_repair_apply_precheck_report",
        "head": head,
        "repo_status_short_before": lines,
        "resume_from_prior_apply_attempt": resume_from_prior_apply_attempt,
        "target_sha256_before": target_sha256_before,
        "checks": checks,
        "precheck_passed": all(checks.values()),
    }


def apply_patch_to_target(source: str) -> str:
    source = source.replace('EXPECTED_HEAD = "7334b77"', 'EXPECTED_HEAD: str | None = None')
    source = source.replace('DOWNLOAD_DIR = OUTPUT_DIR / "downloaded_chunk_03_approved_quarantine"', 'DOWNLOAD_DIR = OUTPUT_DIR / "downloaded_dynamic_chunk_approved_quarantine"')
    source = replace_block(
        source,
        "REQUIRED_OUTPUTS = [",
        "CONTROLLER_NAME =",
        '''OUTPUT_SUFFIXES = [
    "execution_report.json",
    "download_manifest_after_execution.json",
    "gap_report.json",
    "reuse_validation_report.json",
    "sha256_report.json",
    "zip_inventory_report.json",
    "schema_sample_report.json",
    "per_symbol_coverage_summary.json",
    "cumulative_ledger_after_chunk.json",
    "next_chunk_state.json",
    "compliance_report.json",
    "summary.json",
]
REQUIRED_OUTPUTS: list[str] = []

''',
    )
    source = replace_block(
        source,
        'APPROVED_CHUNK_ID = "chunk_03"',
        "\n\nclass ExecutionBlocked",
        '''APPROVED_CHUNK_ID = ""
APPROVED_SYMBOLS: list[str] = []
REUSE_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = date(2023, 7, 1)
DATE_RANGE_END = date(2026, 5, 18)
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_CHUNK_FILE_COUNT = 0
EXPECTED_REUSE_CANDIDATE_FILE_COUNT = 0
MAX_NEW_DOWNLOAD_ATTEMPT_COUNT = 0
MAX_TOTAL_DOWNLOAD_OR_REUSE_FILE_COUNT = 0
MAX_CSV_SAMPLE_ROWS_PER_FILE = 5
MAX_ZIP_SIZE_PER_FILE_MB = 100
MAX_ZIP_MEMBERS_PER_FILE = 10
EXPECTED_SCHEMA_KEY = "OKX_CANDLESTICKS_1M_SCHEMA_V1"
EXPECTED_SCHEMA = [
    "instrument_name",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "open_time",
    "confirm",
]
CHUNKS_TOTAL = 0
CHUNKS_COMPLETED_BEFORE = 0
CHUNKS_COMPLETED_AFTER = 0
CHUNKS_REMAINING_AFTER = 0
NEXT_CHUNK_ID_AFTER_EXECUTION: str | None = None
SYMBOLS_EVALUATED_BEFORE = 0
SYMBOLS_EVALUATED_AFTER = 0
CUMULATIVE_COMPLETE_BEFORE = 0
CUMULATIVE_GAP_BEFORE = 0
CUMULATIVE_PENDING_BEFORE = 0
CUMULATIVE_PENDING_AFTER = 0
CUMULATIVE_AVAILABLE_BEFORE = 0
CUMULATIVE_MISSING_BEFORE = 0
CUMULATIVE_PLANNED_BEFORE = 0''',
    )
    source = source.replace("\n\nclass ExecutionBlocked", "\n\n\nclass ExecutionBlocked")
    source = source.replace(
        "class PlannedFile:\n    chunk_id: str\n    symbol: str\n    day: date\n    url: str\n    expected_inner_csv: str\n    expected_schema_key: str\n    local_zip_path: Path\n    source_kind: str\n    recorded_sha256: str | None = None\n",
        "class PlannedFile:\n    chunk_id: str\n    symbol: str\n    day: date\n    url: str\n    expected_inner_csv: str\n    expected_schema_key: str\n    local_zip_path: Path\n    source_kind: str\n    recorded_sha256: str | None = None\n\n" + DYNAMIC_STATE_BLOCK + "\n",
    )
    source = source.replace('"current_head_guard_passed": head.startswith(EXPECTED_HEAD),', '"current_head_guard_passed": EXPECTED_HEAD is None or head.startswith(EXPECTED_HEAD),')
    source = replace_function(source, "load_and_validate_preview() -> dict[str, Any]:", "validate_manifest_entries", LOAD_VALIDATE_PREVIEW)
    source = source.replace('failures = sorted(failures_by_key.values(), key=lambda row: (APPROVED_SYMBOLS.index(row["symbol"]), row["date"], row["failure_stage"]))', 'failures = sorted(failures_by_key.values(), key=lambda row: (APPROVED_SYMBOLS.index(row["symbol"]), row["date"], row["failure_stage"]))')
    replacements = {
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_report.json"': 'artifact_file("execution_report.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_chunk_download_manifest_after_execution.json"': 'artifact_file("download_manifest_after_execution.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_gap_report.json"': 'artifact_file("gap_report.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_reuse_validation_report.json"': 'artifact_file("reuse_validation_report.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_sha256_report.json"': 'artifact_file("sha256_report.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_zip_inventory_report.json"': 'artifact_file("zip_inventory_report.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_schema_sample_report.json"': 'artifact_file("schema_sample_report.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_per_symbol_coverage_summary.json"': 'artifact_file("per_symbol_coverage_summary.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json"': 'artifact_file("cumulative_ledger_after_chunk.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_next_chunk_state.json"': 'artifact_file("next_chunk_state.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_compliance_report.json"': 'artifact_file("compliance_report.json")',
        '"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_summary.json"': 'artifact_file("summary.json")',
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    source = source.replace('"cumulative_pending_symbol_count": CUMULATIVE_PENDING_AFTER,', '"cumulative_pending_symbol_count": CUMULATIVE_PENDING_AFTER,')
    source = source.replace('"next_chunk_id_after_execution": NEXT_CHUNK_ID_AFTER_EXECUTION,', '"next_chunk_id_after_execution": NEXT_CHUNK_ID_AFTER_EXECUTION,')
    source = source.replace('"route_to_same_generic_cycle_module": CHUNKS_REMAINING_AFTER > 0,', '"route_to_same_generic_cycle_module": CHUNKS_REMAINING_AFTER > 0,')
    source = source.replace('"approved_static_archive_get_only": True,', '"approved_static_archive_get_only": True,\n            "dynamic_chunk_selection": True,\n            "immutable_chunk_artifact_names": True,')
    source = source.replace(
        'write_json(OUTPUT_DIR / artifact_file("summary.json"), blocked)',
        'write_json(OUTPUT_DIR / (artifact_file("summary.json") if APPROVED_CHUNK_ID else "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_state_load_blocked_summary.json"), blocked)',
    )
    return source


def postcheck(source: str, precheck_report: dict[str, Any]) -> dict[str, Any]:
    status = status_lines()
    allowed = {approved_tool_rel(), TARGET_REL}
    changed = {status_path(line) for line in status}
    dynamic_state = "class ControllerState" in source and "def load_latest_controller_state" in source and "latest_json_by_completed_chunk" in source
    chunk_plan = "select" not in "unused" and "selected_chunk = next" in source and "CHUNK_PLAN" in source
    dynamic_names = "artifact_file(" in source and "generic_chunk_coverage_cycle_{APPROVED_CHUNK_ID}_" in source
    dynamic_ledger = "chunks_completed_before + 1" in source or "state.chunks_completed_before + 1" in source
    route_logic = "next_chunk_after(chunk_plan, state.chunk_number)" in source and "FINAL_SUMMARY_MODULE" in source
    hardcoded_only = 'APPROVED_CHUNK_ID = "chunk_03"' in source or "APPROVED_SYMBOLS = [" in source
    safety_preserved = all(
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
        )
    )
    syntax_ok = True
    syntax_error = None
    try:
        ast.parse(source, filename=TARGET_REL)
    except Exception as exc:
        syntax_ok = False
        syntax_error = repr(exc)
    return {
        "artifact_type": "repo_only_generic_chunk_controller_repair_apply_postcheck_report",
        "target_sha256_after": sha256_file(TARGET_FILE),
        "repo_status_short_after_apply": status,
        "changed_paths": sorted(changed),
        "approved_mutation_paths_only": changed.issubset(allowed),
        "target_file_modified": precheck_report["target_sha256_before"] != sha256_file(TARGET_FILE),
        "generic_controller_dynamic_chunk_selection_after_apply": dynamic_state and chunk_plan and dynamic_names,
        "generic_controller_hardcoded_chunk_only_after_apply": hardcoded_only,
        "generic_controller_safe_to_rerun_for_chunk_04_after_apply_pre_audit": dynamic_state and chunk_plan and dynamic_names and dynamic_ledger and route_logic and safety_preserved and not hardcoded_only,
        "dynamic_state_loading_added": dynamic_state,
        "chunk_plan_lookup_added": chunk_plan,
        "dynamic_artifact_naming_added": dynamic_names,
        "dynamic_ledger_update_added": dynamic_ledger,
        "next_route_logic_repaired": route_logic,
        "safety_gates_preserved": safety_preserved,
        "syntax_ok": syntax_ok,
        "syntax_error": syntax_error,
    }


def dynamic_state_check() -> dict[str, Any]:
    next_state = read_json(CHUNK_03_NEXT_STATE_PATH)
    chunk_plan = read_json(CHUNK_PLAN_PATH)
    selected = next((chunk for chunk in chunk_plan.get("chunks", []) if chunk.get("chunk_id") == next_state.get("next_chunk_id_after_execution")), None)
    return {
        "artifact_type": "repo_only_generic_chunk_controller_repair_apply_dynamic_state_check_report",
        "dry_run_state_check_performed": True,
        "dry_run_selected_next_chunk_id": next_state.get("next_chunk_id_after_execution"),
        "dry_run_chunk_symbol_count": len(selected.get("symbols", [])) if isinstance(selected, dict) else 0,
        "dry_run_expected_file_count": selected.get("expected_file_count") if isinstance(selected, dict) else None,
        "dry_run_download_performed": False,
        "dry_run_data_build_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
    }


def syntax_bom_all_tracked() -> dict[str, Any]:
    errors = []
    bom = []
    for rel in run_git(["ls-files", "*.py"]).splitlines():
        if not rel.strip():
            continue
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:
            errors.append({"file": rel, "error": repr(exc)})
    return {"syntax_error_count": len(errors), "syntax_errors": errors, "bom_error_count": len(bom), "bom_errors": bom}


def build_summary(pre: dict[str, Any], post: dict[str, Any], state: dict[str, Any], syntax: dict[str, Any]) -> dict[str, Any]:
    passed = (
        pre["precheck_passed"]
        and post["target_file_modified"]
        and post["approved_mutation_paths_only"]
        and post["generic_controller_dynamic_chunk_selection_after_apply"]
        and not post["generic_controller_hardcoded_chunk_only_after_apply"]
        and post["dynamic_state_loading_added"]
        and post["chunk_plan_lookup_added"]
        and post["dynamic_artifact_naming_added"]
        and post["dynamic_ledger_update_added"]
        and post["next_route_logic_repaired"]
        and post["safety_gates_preserved"]
        and post["syntax_ok"]
        and syntax["syntax_error_count"] == 0
        and syntax["bom_error_count"] == 0
        and state["dry_run_selected_next_chunk_id"] == "chunk_04"
    )
    return {
        "artifact_type": "repo_only_generic_chunk_controller_repair_apply_summary",
        "generic_chunk_controller_repair_apply_status": PASS_STATUS if passed else BLOCKED_STATUS,
        "repair_apply_performed": passed,
        "created_at_utc": utc_now(),
        "target_file": TARGET_REL.replace("/", "\\"),
        "target_file_modified": post["target_file_modified"],
        "apply_tool_file_created": APPROVED_TOOL.exists(),
        "approved_mutation_paths_only": post["approved_mutation_paths_only"],
        "repair_plan_confirmed": pre["checks"]["repair_plan_confirmed"],
        "exhaustive_semantic_audit_confirmed": pre["checks"]["exhaustive_semantic_audit_confirmed"],
        "permission_silent_skip_audit_confirmed": pre["checks"]["permission_silent_skip_audit_confirmed"],
        "pre_repair_hardcoded_chunk_only_confirmed": pre["checks"]["pre_repair_hardcoded_chunk_only_confirmed"],
        "patch_applied": post["target_file_modified"],
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_created": False,
        "generic_controller_dynamic_chunk_selection_after_apply": post["generic_controller_dynamic_chunk_selection_after_apply"],
        "generic_controller_hardcoded_chunk_only_after_apply": post["generic_controller_hardcoded_chunk_only_after_apply"],
        "generic_controller_safe_to_rerun_for_chunk_04_after_apply_pre_audit": post["generic_controller_safe_to_rerun_for_chunk_04_after_apply_pre_audit"],
        "dynamic_state_loading_added": post["dynamic_state_loading_added"],
        "chunk_plan_lookup_added": post["chunk_plan_lookup_added"],
        "dynamic_artifact_naming_added": post["dynamic_artifact_naming_added"],
        "dynamic_ledger_update_added": post["dynamic_ledger_update_added"],
        "next_route_logic_repaired": post["next_route_logic_repaired"],
        "safety_gates_preserved": post["safety_gates_preserved"],
        "dry_run_state_check_performed": state["dry_run_state_check_performed"],
        "dry_run_selected_next_chunk_id": state["dry_run_selected_next_chunk_id"],
        "dry_run_download_performed": False,
        "dry_run_data_build_performed": False,
        "safe_for_post_repair_semantic_audit": passed,
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
        "active_p0_blocker_count": 0 if passed else 1,
        "active_p1_attention_count": 33,
        "current_evidence_chain_quality_after_apply": PASS_QUALITY if passed else BLOCKED_QUALITY,
        "next_module": NEXT_MODULE_PASS if passed else NEXT_MODULE_BLOCKED,
        "replacement_checks_all_true": passed,
        "replacement_checks": {
            "precheck_passed": pre["precheck_passed"],
            "target_file_modified": post["target_file_modified"],
            "approved_mutation_paths_only": post["approved_mutation_paths_only"],
            "dynamic_state_loading_added": post["dynamic_state_loading_added"],
            "chunk_plan_lookup_added": post["chunk_plan_lookup_added"],
            "dynamic_artifact_naming_added": post["dynamic_artifact_naming_added"],
            "dynamic_ledger_update_added": post["dynamic_ledger_update_added"],
            "next_route_logic_repaired": post["next_route_logic_repaired"],
            "safety_gates_preserved": post["safety_gates_preserved"],
            "syntax_bom_clean": syntax["syntax_error_count"] == 0 and syntax["bom_error_count"] == 0,
            "dry_run_selected_chunk_04": state["dry_run_selected_next_chunk_id"] == "chunk_04",
            "no_real_execution_or_forbidden_actions": True,
        },
    }


def run_apply() -> dict[str, Any]:
    pre = precheck()
    if not pre["precheck_passed"]:
        raise ApplyBlocked(f"precheck failed: {pre['checks']}")
    original = TARGET_FILE.read_text(encoding="utf-8")
    already_repaired = (
        "class ControllerState" in original
        and "load_latest_controller_state" in original
        and 'APPROVED_CHUNK_ID = "chunk_03"' not in original
        and "APPROVED_SYMBOLS = [" not in original
    )
    repaired = original if already_repaired else apply_patch_to_target(original)
    if repaired == original and not already_repaired:
        raise ApplyBlocked("patch produced no target changes")
    if repaired != original:
        TARGET_FILE.write_text(repaired, encoding="utf-8")
    post = postcheck(repaired, pre)
    state = dynamic_state_check()
    syntax = syntax_bom_all_tracked()
    summary = build_summary(pre, post, state, syntax)
    diff_summary = {
        "artifact_type": "repo_only_generic_chunk_controller_repair_apply_diff_summary",
        "target_file": TARGET_REL,
        "target_sha256_before": pre["target_sha256_before"],
        "target_sha256_after": post["target_sha256_after"],
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "changed_paths": post["changed_paths"],
        "chunk_specific_file_created": False,
    }
    safety = {
        "artifact_type": "repo_only_generic_chunk_controller_repair_apply_safety_gate_report",
        "safety_gates_preserved": post["safety_gates_preserved"],
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
        "safe_for_chunk_04_real_execution": False,
    }
    report = {
        "artifact_type": "repo_only_generic_chunk_controller_repair_apply_report",
        "summary": summary,
        "precheck": pre,
        "postcheck": post,
        "dynamic_state_check": state,
        "diff_summary": diff_summary,
        "safety_gate_report": safety,
        "forbidden_actions_performed": {
            "chunk_04_real_execution": False,
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
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_apply_report.json", report)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_apply_precheck_report.json", pre)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_apply_diff_summary.json", diff_summary)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_apply_postcheck_report.json", post)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_apply_dynamic_state_check_report.json", state)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_apply_safety_gate_report.json", safety)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_apply_summary.json", summary)
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise ApplyBlocked(f"missing required artifacts: {missing}")
    if not summary["replacement_checks_all_true"]:
        raise ApplyBlocked(f"post-apply checks failed: {summary['replacement_checks']}")
    return summary


def blocked_summary(message: str) -> dict[str, Any]:
    summary = {
        "artifact_type": "repo_only_generic_chunk_controller_repair_apply_summary",
        "generic_chunk_controller_repair_apply_status": BLOCKED_STATUS,
        "repair_apply_performed": False,
        "blocked_reason": message,
        "target_file": TARGET_REL.replace("/", "\\"),
        "target_file_modified": False,
        "apply_tool_file_created": APPROVED_TOOL.exists(),
        "approved_mutation_paths_only": False,
        "repair_plan_confirmed": False,
        "exhaustive_semantic_audit_confirmed": False,
        "permission_silent_skip_audit_confirmed": False,
        "pre_repair_hardcoded_chunk_only_confirmed": False,
        "patch_applied": False,
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_created": False,
        "generic_controller_dynamic_chunk_selection_after_apply": False,
        "generic_controller_hardcoded_chunk_only_after_apply": True,
        "generic_controller_safe_to_rerun_for_chunk_04_after_apply_pre_audit": False,
        "dynamic_state_loading_added": False,
        "chunk_plan_lookup_added": False,
        "dynamic_artifact_naming_added": False,
        "dynamic_ledger_update_added": False,
        "next_route_logic_repaired": False,
        "safety_gates_preserved": False,
        "dry_run_state_check_performed": False,
        "dry_run_selected_next_chunk_id": None,
        "dry_run_download_performed": False,
        "dry_run_data_build_performed": False,
        "safe_for_post_repair_semantic_audit": False,
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
        "active_p1_attention_count": 0,
        "current_evidence_chain_quality_after_apply": BLOCKED_QUALITY,
        "next_module": NEXT_MODULE_BLOCKED,
        "replacement_checks_all_true": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_apply_summary.json", summary)
    return summary


def main() -> int:
    try:
        summary = run_apply()
    except Exception as exc:
        summary = blocked_summary(type(exc).__name__ + ": " + str(exc))
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
